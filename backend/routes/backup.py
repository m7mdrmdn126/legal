from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import Dict, Any, List
from datetime import datetime
import os
import sqlite3
import shutil
import json
import zipfile
import tempfile
from io import BytesIO

from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings

router = APIRouter(prefix="/backup", tags=["Database Backup"])

class BackupManager:
    """Comprehensive database backup and restore manager"""
    
    def __init__(self):
        self.db_path = db_manager.db_path
        self.backup_dir = os.path.join(os.path.dirname(self.db_path), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_full_backup(self, user_id: int) -> Dict[str, Any]:
        """Create a complete database backup with metadata"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"legal_cases_backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Get database statistics for metadata
        stats = self._get_backup_stats()
        
        # Create backup metadata
        metadata = {
            "backup_date": datetime.now().isoformat(),
            "backup_type": "full",
            "created_by": user_id,
            "database_size": os.path.getsize(self.db_path),
            "statistics": stats,
            "version": settings.app_version,
            "tables": self._get_table_info()
        }
        
        # Create ZIP backup with database and metadata
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add database file
            zipf.write(self.db_path, "legal_cases.db")
            
            # Add metadata
            zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False))
            
            # Add table schemas
            schemas = self._export_table_schemas()
            zipf.writestr("table_schemas.sql", schemas)
        
        # Store backup info in database
        backup_info = {
            "backup_name": backup_name,
            "backup_path": backup_path,
            "backup_size": os.path.getsize(backup_path),
            "created_by": user_id,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Create backups table if not exists
        self._ensure_backups_table()
        
        # Insert backup record
        db_manager.execute_write(
            """INSERT INTO backups 
               (backup_name, backup_path, backup_size, created_by, created_at, metadata) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (backup_name, backup_path, backup_info["backup_size"], 
             user_id, backup_info["created_at"], json.dumps(metadata))
        )
        
        return backup_info
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups with metadata"""
        self._ensure_backups_table()
        
        backups = db_manager.execute_query(
            """SELECT b.*, u.full_name as creator_name
               FROM backups b
               LEFT JOIN users u ON b.created_by = u.id
               ORDER BY b.created_at DESC"""
        )
        
        # Parse metadata and check file existence
        for backup in backups:
            try:
                backup["metadata"] = json.loads(backup["metadata"]) if backup["metadata"] else {}
                backup["file_exists"] = os.path.exists(backup["backup_path"])
                backup["size_mb"] = round(backup["backup_size"] / (1024 * 1024), 2)
            except:
                backup["metadata"] = {}
                backup["file_exists"] = False
        
        return backups
    
    def restore_backup(self, backup_id: int, user_id: int) -> Dict[str, Any]:
        """Restore database from backup"""
        # Get backup info
        backup = db_manager.execute_query(
            "SELECT * FROM backups WHERE id = ?", (backup_id,)
        )
        
        if not backup:
            raise HTTPException(status_code=404, detail="Backup not found")
        
        backup = backup[0]
        backup_path = backup["backup_path"]
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # Create a backup of current database before restore
        current_backup = self.create_full_backup(user_id)
        
        try:
            # Extract and restore from backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract database to temporary location
                with tempfile.TemporaryDirectory() as temp_dir:
                    zipf.extract("legal_cases.db", temp_dir)
                    temp_db_path = os.path.join(temp_dir, "legal_cases.db")
                    
                    # Validate extracted database
                    if not self._validate_database(temp_db_path):
                        raise HTTPException(status_code=400, detail="Invalid backup database")
                    
                    # Replace current database
                    shutil.copy2(temp_db_path, self.db_path)
            
            # Log restore operation
            db_manager.execute_write(
                """INSERT INTO backup_operations 
                   (operation_type, backup_id, user_id, operation_date, status) 
                   VALUES (?, ?, ?, ?, ?)""",
                ("restore", backup_id, user_id, datetime.now().isoformat(), "success")
            )
            
            return {
                "status": "success",
                "message": "Database restored successfully",
                "backup_name": backup["backup_name"],
                "restore_date": datetime.now().isoformat(),
                "current_backup_created": current_backup["backup_name"]
            }
            
        except Exception as e:
            # Log failed restore
            db_manager.execute_write(
                """INSERT INTO backup_operations 
                   (operation_type, backup_id, user_id, operation_date, status, error_message) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("restore", backup_id, user_id, datetime.now().isoformat(), "failed", str(e))
            )
            raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
    
    def _get_backup_stats(self) -> Dict[str, int]:
        """Get database statistics for backup metadata"""
        stats = {}
        tables = ["cases", "users", "case_types", "case_sessions", "case_notes"]
        
        for table in tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = result[0]["count"]
            except:
                stats[table] = 0
        
        return stats
    
    def _get_table_info(self) -> List[Dict[str, Any]]:
        """Get information about all tables"""
        tables = db_manager.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        
        table_info = []
        for table in tables:
            table_name = table["name"]
            try:
                count = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")[0]["count"]
                table_info.append({
                    "name": table_name,
                    "record_count": count
                })
            except:
                table_info.append({
                    "name": table_name,
                    "record_count": 0
                })
        
        return table_info
    
    def _export_table_schemas(self) -> str:
        """Export table schemas as SQL"""
        schemas = []
        
        # Get all tables
        tables = db_manager.execute_query(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        
        for table in tables:
            if table["sql"]:
                schemas.append(table["sql"] + ";\n")
        
        return "\n".join(schemas)
    
    def _validate_database(self, db_path: str) -> bool:
        """Validate database integrity"""
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA integrity_check")
            
            # Check for required tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["cases", "users", "case_types"]
            for table in required_tables:
                if table not in tables:
                    return False
            
            conn.close()
            return True
        except:
            return False
    
    def _ensure_backups_table(self):
        """Ensure backup tracking tables exist"""
        db_manager.execute_write("""
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_name TEXT NOT NULL,
                backup_path TEXT NOT NULL,
                backup_size INTEGER NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        """)
        
        db_manager.execute_write("""
            CREATE TABLE IF NOT EXISTS backup_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                backup_id INTEGER,
                user_id INTEGER NOT NULL,
                operation_date TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                FOREIGN KEY (backup_id) REFERENCES backups (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

# Initialize backup manager
backup_manager = BackupManager()

@router.post("/create")
async def create_backup(
    current_user: User = Depends(get_admin_user)
):
    """Create a new database backup (Admin only)"""
    try:
        backup_info = backup_manager.create_full_backup(current_user.id)
        return {
            "status": "success",
            "message": "Backup created successfully",
            "backup": backup_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")

@router.get("/list")
async def list_backups(
    current_user: User = Depends(get_admin_user)
):
    """List all available backups (Admin only)"""
    try:
        backups = backup_manager.list_backups()
        return {
            "backups": backups,
            "total": len(backups)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post("/restore/{backup_id}")
async def restore_backup(
    backup_id: int,
    current_user: User = Depends(get_admin_user)
):
    """Restore database from backup (Admin only)"""
    return backup_manager.restore_backup(backup_id, current_user.id)

@router.get("/download/{backup_id}")
async def download_backup(
    backup_id: int,
    current_user: User = Depends(get_admin_user)
):
    """Download backup file (Admin only)"""
    backup = db_manager.execute_query(
        "SELECT * FROM backups WHERE id = ?", (backup_id,)
    )
    
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    backup = backup[0]
    backup_path = backup["backup_path"]
    
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=404, detail="Backup file not found")
    
    return FileResponse(
        path=backup_path,
        filename=backup["backup_name"],
        media_type="application/zip"
    )

@router.delete("/delete/{backup_id}")
async def delete_backup(
    backup_id: int,
    current_user: User = Depends(get_admin_user)
):
    """Delete a backup (Admin only)"""
    backup = db_manager.execute_query(
        "SELECT * FROM backups WHERE id = ?", (backup_id,)
    )
    
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    backup = backup[0]
    backup_path = backup["backup_path"]
    
    try:
        # Delete file
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        # Delete record
        db_manager.execute_write(
            "DELETE FROM backups WHERE id = ?", (backup_id,)
        )
        
        return {
            "status": "success",
            "message": "Backup deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete backup: {str(e)}")

@router.get("/operations")
async def get_backup_operations(
    current_user: User = Depends(get_admin_user)
):
    """Get backup operation history (Admin only)"""
    operations = db_manager.execute_query("""
        SELECT bo.*, u.full_name as user_name, b.backup_name
        FROM backup_operations bo
        LEFT JOIN users u ON bo.user_id = u.id
        LEFT JOIN backups b ON bo.backup_id = b.id
        ORDER BY bo.operation_date DESC
        LIMIT 100
    """)
    
    return {"operations": operations}
