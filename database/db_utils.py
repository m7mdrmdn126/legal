"""
Database utilities for legal cases management system.
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class LegalCasesDB:
    """Database utility class for legal cases management."""
    
    def __init__(self, db_path="legal_cases.db"):
        """
        Initialize database connection.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection with foreign keys enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute a SELECT query and return results as list of dictionaries.
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
            
        Returns:
            List[Dict]: Query results
        """
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query (str): SQL query
            params (tuple): Query parameters
            
        Returns:
            int: Last row ID for INSERT operations
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
    
    # Case Types Methods
    def get_case_types(self) -> List[Dict]:
        """Get all case types."""
        return self.execute_query("SELECT * FROM case_types ORDER BY name")
    
    def add_case_type(self, name: str, description: str = None) -> int:
        """Add a new case type."""
        return self.execute_write(
            "INSERT INTO case_types (name, description) VALUES (?, ?)",
            (name, description)
        )
    
    # Cases Methods
    def get_cases(self, limit: int = None) -> List[Dict]:
        """Get all cases with case type information."""
        query = """
        SELECT c.*, ct.name as case_type_name, ct.description as case_type_description
        FROM cases c
        JOIN case_types ct ON c.case_type_id = ct.id
        ORDER BY c.created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        return self.execute_query(query)
    
    def get_case_by_id(self, case_id: int) -> Optional[Dict]:
        """Get a specific case by ID."""
        query = """
        SELECT c.*, ct.name as case_type_name, ct.description as case_type_description
        FROM cases c
        JOIN case_types ct ON c.case_type_id = ct.id
        WHERE c.id = ?
        """
        results = self.execute_query(query, (case_id,))
        return results[0] if results else None
    
    def add_case(self, case_number: str, plaintiff: str, defendant: str, 
                 case_type_id: int, judgment_type: str, 
                 previous_judgment_id: Optional[int] = None) -> int:
        """Add a new case."""
        return self.execute_write(
            """INSERT INTO cases 
               (case_number, plaintiff, defendant, case_type_id, judgment_type, previous_judgment_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (case_number, plaintiff, defendant, case_type_id, judgment_type, previous_judgment_id)
        )
    
    def search_cases(self, search_term: str) -> List[Dict]:
        """Search cases by case number, plaintiff, or defendant."""
        query = """
        SELECT c.*, ct.name as case_type_name
        FROM cases c
        JOIN case_types ct ON c.case_type_id = ct.id
        WHERE c.case_number LIKE ? OR c.plaintiff LIKE ? OR c.defendant LIKE ?
        ORDER BY c.created_at DESC
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern))
    
    # Case Sessions Methods
    def get_case_sessions(self, case_id: int) -> List[Dict]:
        """Get all sessions for a specific case."""
        return self.execute_query(
            "SELECT * FROM case_sessions WHERE case_id = ? ORDER BY session_date DESC",
            (case_id,)
        )
    
    def add_case_session(self, case_id: int, session_date: str, session_notes: str = None) -> int:
        """Add a new case session."""
        return self.execute_write(
            "INSERT INTO case_sessions (case_id, session_date, session_notes) VALUES (?, ?, ?)",
            (case_id, session_date, session_notes)
        )
    
    # Case Notes Methods
    def get_case_notes(self, case_id: int) -> List[Dict]:
        """Get all notes for a specific case."""
        return self.execute_query(
            "SELECT * FROM case_notes WHERE case_id = ? ORDER BY created_at DESC",
            (case_id,)
        )
    
    def add_case_note(self, case_id: int, note_text: str) -> int:
        """Add a new case note."""
        return self.execute_write(
            "INSERT INTO case_notes (case_id, note_text) VALUES (?, ?)",
            (case_id, note_text)
        )
    
    # Statistics Methods
    def get_cases_count_by_type(self) -> List[Dict]:
        """Get count of cases by type."""
        return self.execute_query("""
        SELECT ct.name, COUNT(c.id) as case_count
        FROM case_types ct
        LEFT JOIN cases c ON ct.id = c.case_type_id
        GROUP BY ct.id, ct.name
        ORDER BY case_count DESC
        """)
    
    def get_cases_count_by_judgment_type(self) -> List[Dict]:
        """Get count of cases by judgment type."""
        return self.execute_query("""
        SELECT judgment_type, COUNT(*) as case_count
        FROM cases
        GROUP BY judgment_type
        ORDER BY case_count DESC
        """)
    
    # User Management Methods
    def get_users(self) -> List[Dict]:
        """Get all users (excluding password hash)."""
        return self.execute_query("""
        SELECT id, username, full_name, user_type, is_active, created_at, updated_at
        FROM users
        ORDER BY created_at DESC
        """)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username (including password hash for authentication)."""
        results = self.execute_query(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        return results[0] if results else None
    
    def add_user(self, username: str, password: str, full_name: str, user_type: str = "user") -> int:
        """Add a new user with hashed password."""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.execute_write(
            "INSERT INTO users (username, password_hash, full_name, user_type) VALUES (?, ?, ?, ?)",
            (username, password_hash, full_name, user_type)
        )
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user info (without password hash)."""
        user = self.get_user_by_username(username)
        if user and user['is_active']:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] == password_hash:
                # Remove password hash from returned data
                user_data = user.copy()
                del user_data['password_hash']
                return user_data
        return None
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update user password."""
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        rows_affected = self.execute_write(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, user_id)
        )
        return rows_affected > 0
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        rows_affected = self.execute_write(
            "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        return rows_affected > 0
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account."""
        rows_affected = self.execute_write(
            "UPDATE users SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        return rows_affected > 0

# Example usage and testing
if __name__ == "__main__":
    # Initialize database
    db_file = os.path.join(os.path.dirname(__file__), "legal_cases.db")
    db = LegalCasesDB(db_file)
    
    print("Legal Cases Database Utilities")
    print("=" * 40)
    
    # Display case types
    print("\nAvailable Case Types:")
    case_types = db.get_case_types()
    for ct in case_types:
        print(f"- {ct['name']} (ID: {ct['id']})")
    
    # Display statistics
    print("\nCases Count by Type:")
    stats = db.get_cases_count_by_type()
    for stat in stats:
        print(f"- {stat['name']}: {stat['case_count']} cases")
    
    # Display users
    print("\nRegistered Users:")
    users = db.get_users()
    for user in users:
        status = "Active" if user['is_active'] else "Inactive"
        print(f"- {user['username']} ({user['full_name']}) - {user['user_type']} - {status}")
    
    print("\nDatabase utilities initialized successfully!")
    print("You can now use the LegalCasesDB class to interact with the database.")
