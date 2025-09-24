import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestCaseSessions:
    """Test case sessions endpoints"""
    
    async def setup_test_case(self, async_client: AsyncClient, admin_token: str):
        """Helper method to create a test case"""
        headers = auth_headers(admin_token)
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"SESSION/{timestamp}/001",
            "plaintiff": "مدعي للجلسات",
            "defendant": "مدعي عليه للجلسات",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        return response.json()
    
    async def test_get_case_sessions_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting case sessions as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/sessions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    async def test_get_case_sessions_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test getting case sessions as regular user"""
        test_case = await self.setup_test_case(async_client, admin_token)
        user_headers = auth_headers(test_user_token)
        
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/sessions", headers=user_headers)
        
        assert response.status_code == 200
    
    async def test_create_case_session_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating case session as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة اختبار أولى - تم تحديد موعد الجلسة القادمة"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] == test_case["id"]
        assert data["session_notes"] == new_session["session_notes"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_case_session_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test creating case session as regular user"""
        test_case = await self.setup_test_case(async_client, admin_token)
        user_headers = auth_headers(test_user_token)
        
        new_session = {
            "session_date": "2025-01-16T14:00:00",
            "session_notes": "جلسة من مستخدم عادي"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=user_headers)
        
        assert response.status_code == 201
    
    async def test_create_session_for_nonexistent_case(self, async_client: AsyncClient, admin_token: str):
        """Test creating session for non-existent case"""
        headers = auth_headers(admin_token)
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة لقضية غير موجودة"
        }
        
        response = await async_client.post("/api/v1/cases/99999/sessions", json=new_session, headers=headers)
        
        assert response.status_code == 404
    
    async def test_create_session_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test creating session with invalid data"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        invalid_session = {
            "session_date": "invalid-date",
            "session_notes": "ا" * 1001  # Too long
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=invalid_session, headers=headers)
        
        assert response.status_code == 422
    
    async def test_get_session_by_id(self, async_client: AsyncClient, admin_token: str):
        """Test getting specific session by ID"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a session
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة للاستعلام"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        created_session = create_response.json()
        
        # Then get the session
        response = await async_client.get(f"/api/v1/sessions/{created_session['id']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_session["id"]
        assert data["session_notes"] == new_session["session_notes"]
    
    async def test_update_session_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test updating session as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a session
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة للتحديث"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        created_session = create_response.json()
        
        # Update the session
        update_data = {
            "session_date": "2025-01-16T11:00:00",
            "session_notes": "جلسة محدثة - تم تغيير الموعد"
        }
        response = await async_client.put(f"/api/v1/sessions/{created_session['id']}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_notes"] == update_data["session_notes"]
    
    async def test_update_session_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test updating session as regular user"""
        # First create a session as admin
        admin_headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة للتحديث من مستخدم"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=admin_headers)
        created_session = create_response.json()
        
        # Try to update as regular user
        user_headers = auth_headers(test_user_token)
        update_data = {
            "session_notes": "جلسة محدثة من مستخدم عادي"
        }
        response = await async_client.put(f"/api/v1/sessions/{created_session['id']}", json=update_data, headers=user_headers)
        
        assert response.status_code == 200  # Users can update
    
    async def test_delete_session_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test deleting session as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a session
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة للحذف"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        created_session = create_response.json()
        
        # Delete the session
        response = await async_client.delete(f"/api/v1/sessions/{created_session['id']}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify session is deleted
        get_response = await async_client.get(f"/api/v1/sessions/{created_session['id']}", headers=headers)
        assert get_response.status_code == 404
    
    async def test_delete_session_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test deleting session as regular user (should fail)"""
        # First create a session as admin
        admin_headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_session = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "جلسة للحذف من مستخدم"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=admin_headers)
        created_session = create_response.json()
        
        # Try to delete as regular user
        user_headers = auth_headers(test_user_token)
        response = await async_client.delete(f"/api/v1/sessions/{created_session['id']}", headers=user_headers)
        
        assert response.status_code == 403
    
    async def test_create_session_without_date(self, async_client: AsyncClient, admin_token: str):
        """Test creating session without date (only notes)"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_session = {
            "session_notes": "ملاحظات فقط بدون تاريخ"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_date"] is None
        assert data["session_notes"] == new_session["session_notes"]
    
    async def test_create_session_without_notes(self, async_client: AsyncClient, admin_token: str):
        """Test creating session without notes (only date)"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_session = {
            "session_date": "2025-01-15T10:00:00"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["session_date"] is not None
        assert data["session_notes"] is None
    
    async def test_sessions_pagination(self, async_client: AsyncClient, admin_token: str):
        """Test sessions pagination"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # Create multiple sessions
        for i in range(5):
            new_session = {
                "session_date": f"2025-01-{15+i:02d}T10:00:00",
                "session_notes": f"جلسة رقم {i+1}"
            }
            await async_client.post(f"/api/v1/cases/{test_case['id']}/sessions", json=new_session, headers=headers)
        
        # Test pagination
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/sessions?page=1&size=3", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 3
        assert len(data["items"]) <= 3
        assert data["total"] >= 5
