import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestCaseTypes:
    """Test case types endpoints"""
    
    async def test_get_case_types_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting case types as admin"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/case-types", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 6  # Default case types
    
    async def test_get_case_types_as_user(self, async_client: AsyncClient, test_user_token: str):
        """Test getting case types as regular user"""
        headers = auth_headers(test_user_token)
        response = await async_client.get("/api/v1/case-types", headers=headers)
        
        assert response.status_code == 200
    
    async def test_create_case_type_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating case type as admin"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        new_case_type = {
            "name": f"نوع قضية تجريبي فريد {timestamp}",
            "description": "وصف نوع القضية التجريبي"
        }
        
        response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == new_case_type["name"]
        assert data["description"] == new_case_type["description"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_case_type_as_user(self, async_client: AsyncClient, test_user_token: str):
        """Test creating case type as regular user"""
        import time
        headers = auth_headers(test_user_token)
        timestamp = int(time.time())
        new_case_type = {
            "name": f"نوع قضية من مستخدم عادي فريد {timestamp}",
            "description": "وصف من مستخدم عادي"
        }
        
        response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=headers)
        
        assert response.status_code == 201
    
    async def test_create_case_type_with_duplicate_name(self, async_client: AsyncClient, admin_token: str):
        """Test creating case type with duplicate name"""
        headers = auth_headers(admin_token)
        duplicate_case_type = {
            "name": "مدني",  # This already exists
            "description": "وصف مكرر"
        }
        
        response = await async_client.post("/api/v1/case-types", json=duplicate_case_type, headers=headers)
        
        assert response.status_code == 400
    
    async def test_create_case_type_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test creating case type with invalid data"""
        headers = auth_headers(admin_token)
        invalid_case_type = {
            "name": "ا",  # Too short
            "description": None
        }
        
        response = await async_client.post("/api/v1/case-types", json=invalid_case_type, headers=headers)
        
        assert response.status_code == 422
    
    async def test_get_case_type_by_id(self, async_client: AsyncClient, admin_token: str):
        """Test getting specific case type by ID"""
        headers = auth_headers(admin_token)
        
        # First create a case type
        import time
        timestamp = int(time.time() * 1000)
        new_case_type = {
            "name": f"نوع قضية للاستعلام فريد {timestamp}",
            "description": "نوع قضية للاستعلام"
        }
        create_response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=headers)
        created_case_type = create_response.json()
        
        # Then get the case type
        response = await async_client.get(f"/api/v1/case-types/{created_case_type['id']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_case_type["id"]
        assert data["name"] == new_case_type["name"]
    
    async def test_update_case_type_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test updating case type as admin"""
        headers = auth_headers(admin_token)
        
        # First create a case type
        import time
        timestamp = int(time.time() * 1000)
        new_case_type = {
            "name": f"نوع قضية للتحديث فريد {timestamp}",
            "description": "نوع قضية للتحديث"
        }
        create_response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=headers)
        created_case_type = create_response.json()
        
        # Update the case type
        update_data = {
            "name": f"محدث {timestamp}",
            "description": "وصف محدث"
        }
        response = await async_client.put(f"/api/v1/case-types/{created_case_type['id']}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    async def test_update_case_type_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test updating case type as regular user"""
        # First create a case type as admin
        admin_headers = auth_headers(admin_token)
        import time
        timestamp = int(time.time() * 1000)
        new_case_type = {
            "name": f"نوع قضية للتحديث من مستخدم فريد {timestamp}",
            "description": "نوع قضية للتحديث من مستخدم"
        }
        create_response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=admin_headers)
        created_case_type = create_response.json()
        
        # Try to update as regular user
        user_headers = auth_headers(test_user_token)
        update_data = {
            "name": f"محدث من مستخدم {timestamp}",
            "description": "وصف محدث من مستخدم"
        }
        response = await async_client.put(f"/api/v1/case-types/{created_case_type['id']}", json=update_data, headers=user_headers)
        
        assert response.status_code == 200  # Users can update
    
    async def test_delete_case_type_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test deleting case type as admin"""
        headers = auth_headers(admin_token)
        
        # First create a case type
        import time
        timestamp = int(time.time() * 1000)
        new_case_type = {
            "name": f"نوع قضية للحذف فريد {timestamp}",
            "description": "نوع قضية للحذف"
        }
        create_response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=headers)
        created_case_type = create_response.json()
        
        # Delete the case type
        response = await async_client.delete(f"/api/v1/case-types/{created_case_type['id']}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify case type is deleted
        get_response = await async_client.get(f"/api/v1/case-types/{created_case_type['id']}", headers=headers)
        assert get_response.status_code == 404
    
    async def test_delete_case_type_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test deleting case type as regular user (should fail)"""
        # First create a case type as admin
        admin_headers = auth_headers(admin_token)
        import time
        timestamp = int(time.time() * 1000)
        new_case_type = {
            "name": f"نوع قضية للحذف من مستخدم فريد {timestamp}",
            "description": "نوع قضية للحذف من مستخدم"
        }
        create_response = await async_client.post("/api/v1/case-types", json=new_case_type, headers=admin_headers)
        created_case_type = create_response.json()
        
        # Try to delete as regular user
        user_headers = auth_headers(test_user_token)
        response = await async_client.delete(f"/api/v1/case-types/{created_case_type['id']}", headers=user_headers)
        
        assert response.status_code == 403
    
    async def test_get_nonexistent_case_type(self, async_client: AsyncClient, admin_token: str):
        """Test getting non-existent case type"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/case-types/99999", headers=headers)
        
        assert response.status_code == 404
    
    async def test_case_types_pagination(self, async_client: AsyncClient, admin_token: str):
        """Test case types pagination"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/case-types?page=1&size=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
        assert len(data["items"]) <= 5
