#!/usr/bin/env python3
"""
Migration Script: Add Phone Directory Table
==========================================

This script adds the phone_directory table to an existing legal_cases database.
"""

import sqlite3
import os
from datetime import datetime

def migrate_phone_directory(db_path="legal_cases.db"):
    """
    Add phone_directory table to existing database.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist!")
        return False
    
    # Create backup first
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Create backup
        print(f"📁 Creating backup: {backup_path}")
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        # Connect to database
        print("🔗 Connecting to database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Check if table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='phone_directory';
        """)
        
        if cursor.fetchone():
            print("⚠️  Phone directory table already exists!")
            return True
        
        print("📋 Creating phone_directory table...")
        
        # Create phone_directory table
        cursor.execute("""
        CREATE TABLE phone_directory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            الاسم TEXT,
            الرقم TEXT,
            الجهه TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        """)
        
        print("📊 Creating indexes for phone_directory...")
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_phone_directory_name ON phone_directory(الاسم);")
        cursor.execute("CREATE INDEX idx_phone_directory_number ON phone_directory(الرقم);")
        cursor.execute("CREATE INDEX idx_phone_directory_organization ON phone_directory(الجهه);")
        
        # Commit changes
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print("📋 Phone directory table created with the following structure:")
        print("   - id (Primary Key)")
        print("   - الاسم (Name)")
        print("   - الرقم (Phone Number)")
        print("   - الجهه (Organization)")
        print("   - created_at, updated_at (Timestamps)")
        print("   - created_by, updated_by (Audit fields)")
        print("📊 Indexes created for better performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        
        # Restore backup if something went wrong
        if os.path.exists(backup_path):
            print(f"🔄 Restoring backup from: {backup_path}")
            try:
                with open(backup_path, 'rb') as src, open(db_path, 'wb') as dst:
                    dst.write(src.read())
                print("✅ Backup restored successfully")
            except Exception as restore_error:
                print(f"❌ Failed to restore backup: {restore_error}")
        
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def verify_migration(db_path="legal_cases.db"):
    """
    Verify that the migration was successful.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Verifying migration...")
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='phone_directory';
        """)
        
        if not cursor.fetchone():
            print("❌ phone_directory table not found!")
            return False
        
        # Check table structure
        cursor.execute("PRAGMA table_info(phone_directory);")
        columns = cursor.fetchall()
        
        expected_columns = ['id', 'الاسم', 'الرقم', 'الجهه', 'created_at', 'updated_at', 'created_by', 'updated_by']
        actual_columns = [col[1] for col in columns]
        
        print("📋 Table structure:")
        for col in columns:
            col_id, name, data_type, not_null, default, pk = col
            pk_text = " (PRIMARY KEY)" if pk else ""
            print(f"   - {name}: {data_type}{pk_text}")
        
        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='phone_directory';
        """)
        indexes = cursor.fetchall()
        
        print("📊 Indexes created:")
        for idx in indexes:
            print(f"   - {idx[0]}")
        
        print("✅ Migration verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Get the database path
    db_file = os.path.join(os.path.dirname(__file__), "legal_cases.db")
    
    print("🚀 Starting Phone Directory Migration...")
    print("="*50)
    
    # Run migration
    success = migrate_phone_directory(db_file)
    
    if success:
        # Verify migration
        verify_migration(db_file)
    else:
        print("❌ Migration failed!")
        exit(1)
    
    print("="*50)
    print("✅ Phone Directory feature ready!")
