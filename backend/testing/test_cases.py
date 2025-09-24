import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestCases:
    """Test cases endpoints"""
    
    async def test_get_cases_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting cases as admin"""
        headers = auth_headers(admin_token)
        response = await async_client.get("/api/v1/cases", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    async def test_get_cases_as_user(self, async_client: AsyncClient, test_user_token: str):
        """Test getting cases as regular user"""
        headers = auth_headers(test_user_token)
        response = await async_client.get("/api/v1/cases", headers=headers)
        
        assert response.status_code == 200
    
    async def test_create_case_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating case as admin"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        new_case = {
            "case_number": f"TEST/2025/ADMIN/{timestamp}",
            "plaintiff": "أحمد محمد علي الاختبار",
            "defendant": "شركة الاختبار والتطوير المحدودة",
            "case_type_id": 1,  # مدني
            "judgment_type": "حكم اول"
        }
        
        response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["case_number"] == new_case["case_number"]
        assert data["plaintiff"] == new_case["plaintiff"]
        assert data["defendant"] == new_case["defendant"]
        assert data["judgment_type"] == new_case["judgment_type"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_case_as_user(self, async_client: AsyncClient, test_user_token: str):
        """Test creating case as regular user"""
        import time
        headers = auth_headers(test_user_token)
        timestamp = int(time.time())
        new_case = {
            "case_number": f"TEST/2025/USER/{timestamp}",
            "plaintiff": "محمد أحمد الاختبار",
            "defendant": "شركة التجارب القانونية",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        
        response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        
        assert response.status_code == 201
    
    async def test_create_case_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test creating case with invalid data"""
        headers = auth_headers(admin_token)
        invalid_case = {
            "case_number": "12",  # Too short
            "plaintiff": "أ",     # Too short
            "defendant": "",      # Empty
            "case_type_id": 99999, # Non-existent
            "judgment_type": "حكم خاطئ"  # Invalid
        }
        
        response = await async_client.post("/api/v1/cases", json=invalid_case, headers=headers)
        
        assert response.status_code == 422
    
    async def test_create_case_with_duplicate_number(self, async_client: AsyncClient, admin_token: str):
        """Test creating case with duplicate case number"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        case_data = {
            "case_number": f"DUPLICATE/2025/{timestamp}",
            "plaintiff": "مدعي أول",
            "defendant": "مدعي عليه أول",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        
        # Create first case
        response1 = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
        assert response2.status_code == 400
    
    async def test_create_second_judgment_case(self, async_client: AsyncClient, admin_token: str):
        """Test creating second judgment case with reference to first"""
        headers = auth_headers(admin_token)
        
        # Create first judgment case
        import time
        timestamp = int(time.time())
        first_case = {
            "case_number": f"FIRST/2025/{timestamp}",
            "plaintiff": "مدعي الحكم الأول",
            "defendant": "مدعي عليه الحكم الأول",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        first_response = await async_client.post("/api/v1/cases", json=first_case, headers=headers)
        first_case_data = first_response.json()
        
        # Create second judgment case
        second_case = {
            "case_number": f"SECOND/2025/{timestamp+1}",
            "plaintiff": "مدعي الحكم الثاني",
            "defendant": "مدعي عليه الحكم الثاني",
            "case_type_id": 1,
            "judgment_type": "حكم ثان",
            "previous_judgment_id": first_case_data["id"]
        }
        
        response = await async_client.post("/api/v1/cases", json=second_case, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["judgment_type"] == "حكم ثان"
        assert data["previous_judgment_id"] == first_case_data["id"]
    
    async def test_get_case_by_id(self, async_client: AsyncClient, admin_token: str):
        """Test getting specific case by ID"""
        import time
        headers = auth_headers(admin_token)
        timestamp = int(time.time())
        
        # First create a case
        new_case = {
            "case_number": f"GET/2025/{timestamp}",
            "plaintiff": "مدعي للاستعلام",
            "defendant": "مدعي عليه للاستعلام",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        create_response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        created_case = create_response.json()
        
        # Then get the case
        response = await async_client.get(f"/api/v1/cases/{created_case['id']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_case["id"]
        assert data["case_number"] == new_case["case_number"]
    
    async def test_update_case_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test updating case as admin"""
        headers = auth_headers(admin_token)
        
        # First create a case
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"UPDATE/{timestamp}/001",
            "plaintiff": "مدعي للتحديث",
            "defendant": "مدعي عليه للتحديث",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        create_response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        created_case = create_response.json()
        
        # Update the case
        update_data = {
            "plaintiff": "مدعي محدث",
            "defendant": "مدعي عليه محدث",
            "judgment_type": "حكم ثان"
        }
        response = await async_client.put(f"/api/v1/cases/{created_case['id']}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["plaintiff"] == update_data["plaintiff"]
        assert data["defendant"] == update_data["defendant"]
        assert data["judgment_type"] == update_data["judgment_type"]
    
    async def test_delete_case_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test deleting case as admin"""
        headers = auth_headers(admin_token)
        
        # First create a case
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"DELETE/{timestamp}/001",
            "plaintiff": "مدعي للحذف",
            "defendant": "مدعي عليه للحذف",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        create_response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        created_case = create_response.json()
        
        # Delete the case
        response = await async_client.delete(f"/api/v1/cases/{created_case['id']}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify case is deleted
        get_response = await async_client.get(f"/api/v1/cases/{created_case['id']}", headers=headers)
        assert get_response.status_code == 404
    
    async def test_delete_case_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test deleting case as regular user (should fail)"""
        # First create a case as admin
        admin_headers = auth_headers(admin_token)
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"DELETE/USER/{timestamp}/001",
            "plaintiff": "مدعي للحذف من مستخدم",
            "defendant": "مدعي عليه للحذف من مستخدم",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        create_response = await async_client.post("/api/v1/cases", json=new_case, headers=admin_headers)
        created_case = create_response.json()
        
        # Try to delete as regular user
        user_headers = auth_headers(test_user_token)
        response = await async_client.delete(f"/api/v1/cases/{created_case['id']}", headers=user_headers)
        
        assert response.status_code == 403
    
    async def test_search_cases(self, async_client: AsyncClient, admin_token: str):
        """Test searching cases with Arabic text"""
        headers = auth_headers(admin_token)
        
        # First create a case with Arabic text
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"SEARCH/{timestamp}/001",
            "plaintiff": "أحمد محمد الباحث",
            "defendant": "شركة البحث والتطوير",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        
        # Search for the case
        response = await async_client.get("/api/v1/cases?search=أحمد", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        
        # Test search with variations (ه/ة normalization)
        response2 = await async_client.get("/api/v1/cases?search=شركة", headers=headers)
        assert response2.status_code == 200
    
    async def test_filter_cases_by_type(self, async_client: AsyncClient, admin_token: str):
        """Test filtering cases by case type"""
        headers = auth_headers(admin_token)
        
        response = await async_client.get("/api/v1/cases?case_type_id=1", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        for case in data["items"]:
            assert case["case_type_id"] == 1
    
    async def test_filter_cases_by_judgment_type(self, async_client: AsyncClient, admin_token: str):
        """Test filtering cases by judgment type"""
        headers = auth_headers(admin_token)
        
        response = await async_client.get("/api/v1/cases?judgment_type=حكم اول", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        for case in data["items"]:
            assert case["judgment_type"] == "حكم اول"
    
    async def test_cases_pagination(self, async_client: AsyncClient, admin_token: str):
        """Test cases pagination"""
        headers = auth_headers(admin_token)
        
        response = await async_client.get("/api/v1/cases?page=1&size=10", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 10
        assert len(data["items"]) <= 10
    
    async def test_get_case_with_full_details(self, async_client: AsyncClient, admin_token: str):
        """Test getting case with full details"""
        headers = auth_headers(admin_token)
        
        # First create a case
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"FULL/{timestamp}/001",
            "plaintiff": "مدعي كامل",
            "defendant": "مدعي عليه كامل",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        create_response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        created_case = create_response.json()
        
        # Get case with full details
        response = await async_client.get(f"/api/v1/cases/{created_case['id']}/full", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "case_type" in data
        assert "sessions_count" in data
        assert "notes_count" in data
