import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestUsers:
    """Test user management endpoints (admin only)"""
    
    async def test_get_users_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting users list as admin"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["size"] == 40  # Default page size
        assert len(data["items"]) >= 1  # At least admin user
    
    async def test_get_users_as_regular_user(self, async_client: AsyncClient, test_user_token: str):
        """Test getting users list as regular user (should fail)"""
        headers = auth_headers(test_user_token)
        response = await async_client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 403
    
    async def test_create_user_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating new user as admin"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        new_user = {
            "username": f"newuser{timestamp}",
            "password": "newpass123",
            "full_name": "مستخدم جديد للاختبار",
            "user_type": "user"
        }
        
        response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == new_user["username"]
        assert data["full_name"] == new_user["full_name"]
        assert data["user_type"] == new_user["user_type"]
        assert data["is_active"] == True
        assert "password_hash" not in data  # Password should not be returned
    
    async def test_create_user_with_duplicate_username(self, async_client: AsyncClient, admin_token: str):
        """Test creating user with duplicate username"""
        headers = auth_headers(admin_token)
        duplicate_user = {
            "username": "admin",  # This already exists
            "password": "password123",
            "full_name": "مستخدم مكرر",
            "user_type": "user"
        }
        
        response = await async_client.post("/api/v1/users", json=duplicate_user, headers=headers)
        
        assert response.status_code == 400
    
    async def test_create_user_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test creating user with invalid data"""
        headers = auth_headers(admin_token)
        invalid_user = {
            "username": "ab",  # Too short
            "password": "123",  # Too short
            "full_name": "",   # Empty
            "user_type": "invalid_type"
        }
        
        response = await async_client.post("/api/v1/users", json=invalid_user, headers=headers)
        
        assert response.status_code == 422
    
    async def test_get_user_by_id(self, async_client: AsyncClient, admin_token: str):
        """Test getting specific user by ID"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        
        # First create a user
        new_user = {
            "username": f"gettest{timestamp}",
            "password": "password123",
            "full_name": "مستخدم للاستعلام",
            "user_type": "user"
        }
        create_response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        created_user = create_response.json()
        
        # Then get the user
        response = await async_client.get(f"/api/v1/users/{created_user['id']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["username"] == new_user["username"]
    
    async def test_update_user(self, async_client: AsyncClient, admin_token: str):
        """Test updating user"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        
        # First create a user
        new_user = {
            "username": f"updatetest{timestamp}",
            "password": "password123",
            "full_name": "مستخدم للتحديث",
            "user_type": "user"
        }
        create_response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        created_user = create_response.json()
        
        # Update the user
        update_data = {
            "full_name": "اسم محدث",
            "user_type": "admin"
        }
        response = await async_client.put(f"/api/v1/users/{created_user['id']}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["user_type"] == update_data["user_type"]
    
    async def test_deactivate_user(self, async_client: AsyncClient, admin_token: str):
        """Test deactivating user"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        
        # First create a user
        new_user = {
            "username": f"deactivatetest{timestamp}",
            "password": "password123",
            "full_name": "مستخدم للإلغاء",
            "user_type": "user"
        }
        create_response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        created_user = create_response.json()
        
        # Deactivate the user
        response = await async_client.post(f"/api/v1/users/{created_user['id']}/deactivate", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == False
    
    async def test_activate_user(self, async_client: AsyncClient, admin_token: str):
        """Test activating user"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        
        # First create and deactivate a user
        new_user = {
            "username": f"activatetest{timestamp}",
            "password": "password123",
            "full_name": "مستخدم للتفعيل",
            "user_type": "user"
        }
        create_response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        created_user = create_response.json()
        
        await async_client.post(f"/api/v1/users/{created_user['id']}/deactivate", headers=headers)
        
        # Activate the user
        response = await async_client.post(f"/api/v1/users/{created_user['id']}/activate", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == True
    
    async def test_delete_user(self, async_client: AsyncClient, admin_token: str):
        """Test deleting user"""
        headers = auth_headers(admin_token)
        
        # First create a user
        new_user = {
            "username": "deletetest123",
            "password": "password123",
            "full_name": "مستخدم للحذف",
            "user_type": "user"
        }
        create_response = await async_client.post("/api/v1/users", json=new_user, headers=headers)
        created_user = create_response.json()
        
        # Delete the user
        response = await async_client.delete(f"/api/v1/users/{created_user['id']}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify user is deleted
        get_response = await async_client.get(f"/api/v1/users/{created_user['id']}", headers=headers)
        assert get_response.status_code == 404
