import pytest
from httpx import AsyncClient
from conftest import auth_headers, test_config, TestConfig

@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints"""
    
    async def test_login_success(self, async_client: AsyncClient):
        """Test successful admin login"""
        response = await async_client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == 43200  # 12 hours
        assert "user" in data
        assert data["user"]["username"] == "admin"
        assert data["user"]["user_type"] == "admin"
    
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        response = await async_client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Test login with missing fields"""
        response = await async_client.post("/api/v1/auth/login", json={
            "username": "admin"
        })
        
        assert response.status_code == 422
    
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Test login with non-existent user"""
        response = await async_client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_without_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint without token"""
        response = await async_client.get("/api/v1/users")
        
        assert response.status_code == 403  # HTTPBearer returns 403 for missing Authorization header
    
    async def test_protected_endpoint_with_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected endpoint with invalid token"""
        headers = auth_headers("invalid_token")
        response = await async_client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_with_valid_token(self, async_client: AsyncClient, admin_token: str):
        """Test accessing protected endpoint with valid token"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 200
    
    async def test_admin_endpoint_with_user_token(self, async_client: AsyncClient, test_user_token: str):
        """Test accessing admin endpoint with user token"""
        headers = auth_headers(test_user_token)
        response = await async_client.post("/api/v1/users", 
            json={
                "username": "newuser",
                "password": "password123",
                "full_name": "مستخدم جديد"
            },
            headers=headers
        )
        
        assert response.status_code == 403
