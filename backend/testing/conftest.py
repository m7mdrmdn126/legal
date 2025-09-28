import pytest
import pytest_asyncio
import sys
import os
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app

# Test configuration
TEST_BASE_URL = "http://test"
TEST_DATABASE = "test_legal_cases.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before running tests"""
    import sqlite3
    from passlib.context import CryptContext
    
    # Set environment variable for test database path
    os.environ["DATABASE_PATH"] = TEST_DATABASE
    
    # Remove existing test database
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)
    
    # Create test database and schema
    conn = sqlite3.connect(TEST_DATABASE)
    cursor = conn.cursor()
    
    try:
        # Enable foreign key support
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        """)
        
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
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (case_type_id) REFERENCES case_types(id),
            FOREIGN KEY (previous_judgment_id) REFERENCES cases(id),
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            session_date DATETIME,
            session_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            note_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK (user_type IN ('admin', 'user')),
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER
        );
        """)
        
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
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_type ON cases(case_type_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_sessions_case_id ON case_sessions(case_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_notes_case_id ON case_notes(case_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_name ON phone_directory(الاسم);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_number ON phone_directory(الرقم);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_phone_directory_organization ON phone_directory(الجهه);")
        
        # Insert default case types
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
        
        # Insert default admin user
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        admin_password = pwd_context.hash("admin123")
        cursor.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, full_name, user_type) 
        VALUES (?, ?, ?, ?)
        """, ("admin", admin_password, "System Administrator", "admin"))
        
        conn.commit()
        
    except Exception as e:
        print(f"Error setting up test database: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    yield
    
    # Cleanup
    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)

class TestConfig:
    """Test configuration"""
    admin_credentials = {"username": "admin", "password": "admin123"}
    test_user_credentials = {"username": "testuser", "password": "testpass123"}
    
    # Test data
    test_case_type = {
        "name": "تجريبي",
        "description": "نوع قضية تجريبي للاختبار"
    }
    
    test_case = {
        "case_number": "TEST/2025/001",
        "plaintiff": "أحمد محمد الاختبار",
        "defendant": "شركة الاختبار المحدودة",
        "case_type_id": 1,
        "judgment_type": "حكم اول"
    }
    
    test_session = {
        "session_date": "2025-01-15T10:00:00",
        "session_notes": "جلسة اختبار أولى"
    }
    
    test_note = {
        "note_text": "هذه ملاحظة تجريبية للاختبار"
    }

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_client():
    """Create async test client"""
    async with AsyncClient(app=app, base_url=TEST_BASE_URL) as client:
        yield client

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return TestConfig()

# Helper functions
async def login_admin(client: AsyncClient) -> str:
    """Login as admin and return token"""
    response = await client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

async def login_user(client: AsyncClient, username: str, password: str) -> str:
    """Login as user and return token"""
    response = await client.post("/api/v1/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def auth_headers(token: str) -> dict:
    """Create authorization headers"""
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def admin_token(async_client):
    """Get admin token"""
    return await login_admin(async_client)

@pytest_asyncio.fixture
async def test_user_token(async_client, admin_token):
    """Create test user and get token"""
    # First create a test user as admin
    await async_client.post("/api/v1/users", 
        json={
            "username": "testuser",
            "password": "testpass123",
            "full_name": "مستخدم الاختبار",
            "user_type": "user"
        },
        headers=auth_headers(admin_token)
    )
    
    # Then login as that user
    return await login_user(async_client, "testuser", "testpass123")
