import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from .settings import settings

class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        # Get the backend directory (where this file is located)
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Construct absolute path to database
        if settings.database_path.startswith('../'):
            # Handle relative path from backend directory
            relative_path = settings.database_path[3:]  # Remove '../'
            self.db_path = os.path.abspath(os.path.join(backend_dir, '..', relative_path))
        else:
            # Handle absolute path or path relative to backend
            self.db_path = os.path.abspath(os.path.join(backend_dir, settings.database_path))
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute SELECT query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT, UPDATE, DELETE query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid or cursor.rowcount

# Global database manager instance
db_manager = DatabaseManager()
