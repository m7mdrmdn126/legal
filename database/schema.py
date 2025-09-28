"""
Legal Cases Database Schema
==========================

Database structure for legal cases management system.

Tables:
1. case_types - Types of legal cases
2. cases - Main cases table
3. case_sessions - Sessions and follow-ups for each case
4. case_notes - Notes and observations for cases
"""

import sqlite3
import os
from datetime import datetime

def create_database_schema(db_path="legal_cases.db"):
    """
    Create the database schema for the legal cases application.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # 1. Case Types Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 2. Cases Table (Main table)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT NOT NULL UNIQUE,
            plaintiff TEXT NOT NULL,
            defendant TEXT NOT NULL,
            case_type_id INTEGER NOT NULL,
            judgment_type TEXT NOT NULL CHECK (judgment_type IN ('حكم اول', 'حكم ثان', 'حكم ثالث')),
            previous_judgment_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_type_id) REFERENCES case_types(id),
            FOREIGN KEY (previous_judgment_id) REFERENCES cases(id)
        );
        """)
        
        # 3. Case Sessions Table (ميعاد الجلسه / المتابعة)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            session_date DATETIME,
            session_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );
        """)
        
        # 4. Case Notes Table (الملاحظات)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
        );
        """)
        
        # 5. Users Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('admin', 'user')),
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # 6. Phone Directory Table (دليل التليفونات)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS phone_directory (
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
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_type ON cases(case_type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_sessions_case_id ON case_sessions(case_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_notes_case_id ON case_notes(case_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_name ON phone_directory(الاسم);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_number ON phone_directory(الرقم);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_organization ON phone_directory(الجهه);")
        
        # Insert some default case types
        default_case_types = [
            ('مدني', 'قضايا مدنية'),
            ('جنائي', 'قضايا جنائية'),
            ('تجاري', 'قضايا تجارية'),
            ('عمالي', 'قضايا عمالية'),
            ('أحوال شخصية', 'قضايا الأحوال الشخصية'),
            ('إداري', 'قضايا إدارية')
        ]
        
        cursor.executemany("""
        INSERT OR IGNORE INTO case_types (name, description) VALUES (?, ?)
        """, default_case_types)
        
        # Insert default admin user (password: admin123 - should be changed in production)
        import hashlib
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, full_name, user_type) 
        VALUES (?, ?, ?, ?)
        """, ("admin", admin_password, "System Administrator", "admin"))
        
        # Commit changes
        conn.commit()
        print(f"Database schema created successfully at: {db_path}")
        print("Tables created:")
        print("- case_types")
        print("- cases") 
        print("- case_sessions")
        print("- case_notes")
        print("- users")
        print("- phone_directory (دليل التليفونات)")
        print("- Indexes created for performance optimization")
        print("- Default case types inserted")
        print("- Default admin user created (username: admin, password: admin123)")
        
    except Exception as e:
        print(f"Error creating database schema: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

def get_schema_info(db_path="legal_cases.db"):
    """
    Display schema information for all tables.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Database Schema Information:")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 30)
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                pk_text = " (PRIMARY KEY)" if pk else ""
                not_null_text = " NOT NULL" if not_null else ""
                default_text = f" DEFAULT {default}" if default else ""
                print(f"  {name}: {data_type}{not_null_text}{default_text}{pk_text}")
    
    except Exception as e:
        print(f"Error reading schema: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    # Create the database schema
    db_file = os.path.join(os.path.dirname(__file__), "legal_cases.db")
    create_database_schema(db_file)
    
    # Display schema information
    print("\n" + "="*50)
    get_schema_info(db_file)
