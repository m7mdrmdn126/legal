import pytest
import asyncio
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

@pytest.fixture
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

# Separate scope for token fixtures to ensure they work properly with async_client
@pytest.fixture(scope="function")
async def admin_token(async_client):
    """Get admin token"""
    return await login_admin(async_client)

@pytest.fixture(scope="function") 
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
