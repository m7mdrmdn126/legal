from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import time
import os
import sqlite3

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from dependencies.auth import get_current_user, get_admin_user
from models.user import User
from config.database import db_manager
from config.settings import settings

router = APIRouter(prefix="/performance", tags=["Performance"])

class PerformanceManager:
    """System performance monitoring and optimization"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = {}
        self.performance_logs = []
        self._ensure_performance_tables()
    
    def _ensure_performance_tables(self):
        """Ensure performance tracking tables exist"""
        
        # Performance logs table
        db_manager.execute_write("""
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                memory_usage_mb REAL,
                cpu_percent REAL,
                user_id INTEGER,
                endpoint TEXT,
                parameters TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # System metrics table
        db_manager.execute_write("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                memory_used_mb REAL,
                disk_usage_percent REAL,
                active_connections INTEGER,
                database_size_mb REAL
            )
        """)
        
        # Query performance table
        db_manager.execute_write("""
            CREATE TABLE IF NOT EXISTS query_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                query_hash TEXT NOT NULL,
                query_text TEXT,
                duration_ms INTEGER NOT NULL,
                rows_affected INTEGER,
                execution_plan TEXT
            )
        """)
    
    def log_operation(self, operation_type: str, duration_ms: int, 
                     user_id: Optional[int] = None, endpoint: Optional[str] = None,
                     parameters: Optional[Dict] = None):
        """Log operation performance"""
        try:
            # Get system metrics
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                memory_usage_mb = memory.used / 1024 / 1024
            else:
                cpu_percent = 0.0
                memory_usage_mb = 0.0
            
            db_manager.execute_write("""
                INSERT INTO performance_logs 
                (timestamp, operation_type, duration_ms, memory_usage_mb, 
                 cpu_percent, user_id, endpoint, parameters)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                operation_type,
                duration_ms,
                memory_usage_mb,
                cpu_percent,
                user_id,
                endpoint,
                str(parameters) if parameters else None
            ))
            
            # Keep in-memory log (last 100 operations)
            self.performance_logs.append({
                "timestamp": datetime.now().isoformat(),
                "operation_type": operation_type,
                "duration_ms": duration_ms,
                "memory_usage_mb": memory_usage_mb,
                "cpu_percent": cpu_percent
            })
            
            if len(self.performance_logs) > 100:
                self.performance_logs.pop(0)
                
        except Exception as e:
            print(f"Error logging performance: {e}")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            if PSUTIL_AVAILABLE:
                # CPU and Memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Disk usage
                disk = psutil.disk_usage('/')
            else:
                # Fallback values when psutil is not available
                cpu_percent = 0.0
                memory = type('obj', (object,), {
                    'percent': 0.0, 'used': 0, 'available': 0
                })
                disk = type('obj', (object,), {
                    'percent': 0.0, 'free': 0
                })
            
            # Database size
            db_size_mb = 0
            try:
                db_size_mb = os.path.getsize(db_manager.db_path) / 1024 / 1024
            except:
                pass
            
            # Active database connections (estimate)
            active_connections = len(self.performance_logs)  # Simplified metric
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / 1024 / 1024,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_usage_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "database_size_mb": db_size_mb,
                "active_connections": active_connections
            }
            
            # Store metrics
            db_manager.execute_write("""
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_mb, 
                 disk_usage_percent, active_connections, database_size_mb)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics["timestamp"],
                metrics["cpu_percent"],
                metrics["memory_percent"],
                metrics["memory_used_mb"],
                metrics["disk_usage_percent"],
                metrics["active_connections"],
                metrics["database_size_mb"]
            ))
            
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_database_performance(self) -> Dict[str, Any]:
        """Analyze database performance"""
        try:
            # Table sizes and row counts
            tables_info = []
            
            # Get all tables
            tables = db_manager.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            
            for table in tables:
                table_name = table['name']
                try:
                    # Row count
                    count_result = db_manager.execute_query(f"SELECT COUNT(*) as count FROM {table_name}")
                    row_count = count_result[0]['count'] if count_result else 0
                    
                    tables_info.append({
                        "table_name": table_name,
                        "row_count": row_count
                    })
                except:
                    tables_info.append({
                        "table_name": table_name,
                        "row_count": 0,
                        "error": "Could not get row count"
                    })
            
            # Database integrity check
            try:
                integrity_result = db_manager.execute_query("PRAGMA integrity_check")
                integrity_ok = integrity_result[0].get('integrity_check') == 'ok' if integrity_result else False
            except:
                integrity_ok = False
            
            # Recent performance logs
            recent_logs = db_manager.execute_query("""
                SELECT operation_type, AVG(duration_ms) as avg_duration, 
                       COUNT(*) as count, MAX(duration_ms) as max_duration
                FROM performance_logs
                WHERE timestamp > datetime('now', '-1 hour')
                GROUP BY operation_type
                ORDER BY avg_duration DESC
            """)
            
            return {
                "database_size_mb": os.path.getsize(db_manager.db_path) / 1024 / 1024,
                "tables_info": tables_info,
                "integrity_check": integrity_ok,
                "recent_performance": recent_logs,
                "total_tables": len(tables_info),
                "total_records": sum(table.get('row_count', 0) for table in tables_info)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization"""
        optimization_results = []
        start_time = time.time()
        
        try:
            # VACUUM - Reclaim unused space
            db_manager.execute_write("VACUUM")
            optimization_results.append("VACUUM completed - Reclaimed unused space")
            
            # ANALYZE - Update statistics
            db_manager.execute_write("ANALYZE")
            optimization_results.append("ANALYZE completed - Updated statistics")
            
            # Reindex
            db_manager.execute_write("REINDEX")
            optimization_results.append("REINDEX completed - Rebuilt indexes")
            
            # Clean old performance logs (keep last 30 days)
            deleted_logs = db_manager.execute_write("""
                DELETE FROM performance_logs 
                WHERE timestamp < datetime('now', '-30 days')
            """)
            optimization_results.append(f"Cleaned old performance logs: {deleted_logs} records")
            
            # Clean old system metrics (keep last 7 days)
            deleted_metrics = db_manager.execute_write("""
                DELETE FROM system_metrics 
                WHERE timestamp < datetime('now', '-7 days')
            """)
            optimization_results.append(f"Cleaned old system metrics: {deleted_metrics} records")
            
            end_time = time.time()
            duration_ms = int((end_time - start_time) * 1000)
            
            # Log the optimization
            self.log_operation("database_optimization", duration_ms)
            
            return {
                "status": "success",
                "duration_ms": duration_ms,
                "operations": optimization_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "duration_ms": int((time.time() - start_time) * 1000)
            }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear application cache"""
        cache_items = len(self.cache)
        self.cache.clear()
        self.cache_ttl.clear()
        
        return {
            "status": "success",
            "cleared_items": cache_items,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        
        # Clean expired items
        expired_keys = [key for key, ttl in self.cache_ttl.items() if ttl < current_time]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.cache_ttl.pop(key, None)
        
        return {
            "cache_size": len(self.cache),
            "cache_items": list(self.cache.keys()),
            "memory_usage_estimate": len(str(self.cache)) / 1024,  # KB estimate
            "expired_cleaned": len(expired_keys)
        }
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        
        since = datetime.now() - timedelta(hours=hours)
        
        # System metrics trend
        system_trends = db_manager.execute_query("""
            SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent
            FROM system_metrics
            WHERE timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 100
        """, (since.isoformat(),))
        
        # Operation performance trends
        operation_trends = db_manager.execute_query("""
            SELECT 
                strftime('%Y-%m-%d %H:00', timestamp) as hour,
                operation_type,
                AVG(duration_ms) as avg_duration,
                COUNT(*) as count
            FROM performance_logs
            WHERE timestamp > ?
            GROUP BY hour, operation_type
            ORDER BY hour DESC
        """, (since.isoformat(),))
        
        # Slowest operations
        slow_operations = db_manager.execute_query("""
            SELECT operation_type, endpoint, duration_ms, timestamp, parameters
            FROM performance_logs
            WHERE timestamp > ?
            ORDER BY duration_ms DESC
            LIMIT 20
        """, (since.isoformat(),))
        
        return {
            "period_hours": hours,
            "system_trends": system_trends,
            "operation_trends": operation_trends,
            "slow_operations": slow_operations,
            "total_operations": len(operation_trends)
        }

# Initialize performance manager
performance_manager = PerformanceManager()

@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get current system performance metrics"""
    return performance_manager.get_system_metrics()

@router.get("/database")
async def get_database_performance(
    current_user: User = Depends(get_current_user)
):
    """Get database performance information"""
    return performance_manager.get_database_performance()

@router.post("/optimize")
async def optimize_system(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user)
):
    """Optimize system performance (Admin only)"""
    
    def run_optimization():
        return performance_manager.optimize_database()
    
    # Run optimization in background
    background_tasks.add_task(run_optimization)
    
    return {
        "status": "started",
        "message": "System optimization started in background",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/optimize/sync")
async def optimize_system_sync(
    current_user: User = Depends(get_admin_user)
):
    """Optimize system performance synchronously (Admin only)"""
    return performance_manager.optimize_database()

@router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(get_admin_user)
):
    """Clear application cache (Admin only)"""
    return performance_manager.clear_cache()

@router.get("/cache")
async def get_cache_info(
    current_user: User = Depends(get_admin_user)
):
    """Get cache information (Admin only)"""
    return performance_manager.get_cache_info()

@router.get("/trends")
async def get_performance_trends(
    hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Get performance trends over specified hours"""
    return performance_manager.get_performance_trends(hours)

@router.get("/logs")
async def get_performance_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get recent performance logs"""
    
    logs = db_manager.execute_query("""
        SELECT * FROM performance_logs
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    return {
        "logs": logs,
        "total": len(logs)
    }

@router.get("/health")
async def health_check(
    current_user: User = Depends(get_current_user)
):
    """System health check endpoint"""
    
    start_time = time.time()
    
    # Test database connection
    try:
        db_test = db_manager.execute_query("SELECT 1 as test")
        db_status = "healthy" if db_test else "unhealthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Get basic metrics
    try:
        if PSUTIL_AVAILABLE:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
        else:
            cpu = memory = disk = None
    except:
        cpu = memory = disk = None
    
    response_time = int((time.time() - start_time) * 1000)
    
    # Log health check
    performance_manager.log_operation("health_check", response_time, current_user.id, "/performance/health")
    
    health_status = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "response_time_ms": response_time,
        "database": db_status,
        "system": {
            "cpu_percent": cpu,
            "memory_percent": memory.percent if memory else None,
            "disk_percent": disk.percent if disk else None
        }
    }
    
    return health_status
