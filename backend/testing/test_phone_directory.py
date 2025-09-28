"""
Phone Directory Tests
====================

Comprehensive unit tests for phone directory (دليل التليفونات) feature.
Tests all CRUD operations and role-based access control.
"""

import pytest
from httpx import AsyncClient
from conftest import auth_headers

@pytest.mark.asyncio
class TestPhoneDirectory:
    """Test class for phone directory functionality"""
    
    @pytest.fixture(autouse=True)
    async def setup_method(self, async_client, admin_token, test_user_token):
        """Setup method run before each test"""
        self.client = async_client
        self.admin_headers = auth_headers(admin_token)
        self.user_headers = auth_headers(test_user_token)
        
        # Clear phone directory before each test
        self._cleanup_phone_directory()
    
    def _cleanup_phone_directory(self):
        """Remove all phone directory entries"""
        import sqlite3
        import os
        
        db_path = os.environ.get("DATABASE_PATH", "test_legal_cases.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM phone_directory")
        conn.commit()
        conn.close()
    
    async def test_create_phone_entry_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating phone directory entry as admin"""
        
        entry_data = {
            "الاسم": "أحمد محمد علي",
            "الرقم": "01234567890",
            "الجهه": "وزارة العدل"
        }
        
        headers = auth_headers(admin_token)
        response = await async_client.post(
            "/api/v1/phone-directory/", 
            json=entry_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["الاسم"] == entry_data["الاسم"]
        assert data["الرقم"] == entry_data["الرقم"]
        assert data["الجهه"] == entry_data["الجهه"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["created_by"] is not None
    
    def test_create_phone_entry_user(self):
        """Test creating phone directory entry as regular user"""
        
        entry_data = {
            "الاسم": "فاطمة أحمد",
            "الرقم": "01111111111",
            "الجهه": "المحكمة الابتدائية"
        }
        
        response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["الاسم"] == entry_data["الاسم"]
        assert data["الرقم"] == entry_data["الرقم"]
        assert data["الجهه"] == entry_data["الجهه"]
    
    def test_create_phone_entry_optional_fields(self):
        """Test creating phone entry with optional fields"""
        
        # Test with only name
        entry_data = {"الاسم": "محمد فقط"}
        
        response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["الاسم"] == "محمد فقط"
        assert data["الرقم"] is None
        assert data["الجهه"] is None
        
        # Test with empty object
        response = self.client.post(
            "/phone-directory/", 
            json={},
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["الاسم"] is None
        assert data["الرقم"] is None
        assert data["الجهه"] is None
    
    def test_create_phone_entry_unauthorized(self):
        """Test creating phone entry without authentication"""
        
        entry_data = {
            "الاسم": "Test User",
            "الرقم": "01234567890"
        }
        
        response = self.client.post("/phone-directory/", json=entry_data)
        assert response.status_code == 401
    
    def test_get_phone_entries_list(self):
        """Test listing phone directory entries"""
        
        # Create test entries
        test_entries = [
            {"الاسم": "أحمد محمد", "الرقم": "01111111111", "الجهه": "وزارة العدل"},
            {"الاسم": "فاطمة علي", "الرقم": "01222222222", "الجهه": "المحكمة"},
            {"الاسم": "محمد أحمد", "الرقم": "01333333333", "الجهه": "النيابة"}
        ]
        
        # Create entries
        for entry in test_entries:
            self.client.post(
                "/phone-directory/", 
                json=entry,
                headers=self.admin_headers
            )
        
        # Get entries list
        response = self.client.get("/phone-directory/", headers=self.admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "pages" in data
        
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["size"] == 10
    
    def test_get_phone_entries_pagination(self):
        """Test pagination in phone directory listing"""
        
        # Create 5 test entries
        for i in range(5):
            entry_data = {
                "الاسم": f"شخص رقم {i+1}",
                "الرقم": f"0123456789{i}",
                "الجهه": f"جهة رقم {i+1}"
            }
            self.client.post(
                "/phone-directory/", 
                json=entry_data,
                headers=self.admin_headers
            )
        
        # Test first page with size 2
        response = self.client.get(
            "/phone-directory/?page=1&size=2", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 5
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["pages"] == 3
        
        # Test second page
        response = self.client.get(
            "/phone-directory/?page=2&size=2", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["items"]) == 2
    
    def test_search_phone_entries(self):
        """Test searching phone directory entries"""
        
        # Create test entries
        test_entries = [
            {"الاسم": "أحمد محمد", "الرقم": "01111111111", "الجهه": "وزارة العدل"},
            {"الاسم": "محمد أحمد", "الرقم": "01222222222", "الجهه": "المحكمة"},
            {"الاسم": "فاطمة علي", "الرقم": "01333333333", "الجهه": "النيابة العامة"}
        ]
        
        for entry in test_entries:
            self.client.post(
                "/phone-directory/", 
                json=entry,
                headers=self.admin_headers
            )
        
        # Test general search
        response = self.client.get(
            "/phone-directory/?search=محمد", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Both "أحمد محمد" and "محمد أحمد"
        
        # Test name-specific search
        response = self.client.get(
            "/phone-directory/?الاسم=فاطمة", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["الاسم"] == "فاطمة علي"
        
        # Test organization search
        response = self.client.get(
            "/phone-directory/?الجهه=وزارة", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["الجهه"] == "وزارة العدل"
    
    def test_get_phone_entry_by_id(self):
        """Test getting specific phone directory entry by ID"""
        
        # Create entry
        entry_data = {
            "الاسم": "خالد عبد الله",
            "الرقم": "01555555555",
            "الجهه": "محكمة الاستئناف"
        }
        
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        created_entry = create_response.json()
        entry_id = created_entry["id"]
        
        # Get entry by ID
        response = self.client.get(
            f"/phone-directory/{entry_id}", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == entry_id
        assert data["الاسم"] == entry_data["الاسم"]
        assert data["الرقم"] == entry_data["الرقم"]
        assert data["الجهه"] == entry_data["الجهه"]
    
    def test_get_nonexistent_phone_entry(self):
        """Test getting non-existent phone directory entry"""
        
        response = self.client.get(
            "/phone-directory/99999", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_update_phone_entry_admin(self):
        """Test updating phone directory entry as admin"""
        
        # Create entry
        entry_data = {
            "الاسم": "سعد محمد",
            "الرقم": "01666666666",
            "الجهه": "المحكمة العليا"
        }
        
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        entry_id = create_response.json()["id"]
        
        # Update entry
        update_data = {
            "الاسم": "سعد محمد المحدث",
            "الرقم": "01777777777"
        }
        
        response = self.client.put(
            f"/phone-directory/{entry_id}", 
            json=update_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["الاسم"] == update_data["الاسم"]
        assert data["الرقم"] == update_data["الرقم"]
        assert data["الجهه"] == entry_data["الجهه"]  # Should remain unchanged
        assert data["updated_by"] is not None
    
    def test_update_phone_entry_user(self):
        """Test updating phone directory entry as regular user"""
        
        # Create entry as user
        entry_data = {
            "الاسم": "مريم أحمد",
            "الرقم": "01888888888",
            "الجهه": "النيابة"
        }
        
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.user_headers
        )
        
        entry_id = create_response.json()["id"]
        
        # Update entry as user
        update_data = {"الاسم": "مريم أحمد المحدثة"}
        
        response = self.client.put(
            f"/phone-directory/{entry_id}", 
            json=update_data,
            headers=self.user_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["الاسم"] == update_data["الاسم"]
    
    def test_update_nonexistent_phone_entry(self):
        """Test updating non-existent phone directory entry"""
        
        update_data = {"الاسم": "غير موجود"}
        
        response = self.client.put(
            "/phone-directory/99999", 
            json=update_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 404
    
    def test_update_phone_entry_empty_data(self):
        """Test updating phone entry with no data"""
        
        # Create entry
        entry_data = {"الاسم": "Test User"}
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        entry_id = create_response.json()["id"]
        
        # Try to update with empty data
        response = self.client.put(
            f"/phone-directory/{entry_id}", 
            json={},
            headers=self.admin_headers
        )
        
        assert response.status_code == 400
        assert "No fields to update" in response.json()["detail"]
    
    def test_delete_phone_entry_admin(self):
        """Test deleting phone directory entry as admin"""
        
        # Create entry
        entry_data = {
            "الاسم": "للحذف",
            "الرقم": "01999999999"
        }
        
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        entry_id = create_response.json()["id"]
        
        # Delete entry
        response = self.client.delete(
            f"/phone-directory/{entry_id}", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "deleted successfully" in data["message"]
        
        # Verify entry is deleted
        get_response = self.client.get(
            f"/phone-directory/{entry_id}", 
            headers=self.admin_headers
        )
        assert get_response.status_code == 404
    
    def test_delete_phone_entry_user_forbidden(self):
        """Test that regular users cannot delete phone directory entries"""
        
        # Create entry as admin
        entry_data = {"الاسم": "لا يمكن حذفه"}
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        entry_id = create_response.json()["id"]
        
        # Try to delete as user
        response = self.client.delete(
            f"/phone-directory/{entry_id}", 
            headers=self.user_headers
        )
        
        assert response.status_code == 403
        assert "Only admin users can delete" in response.json()["detail"]
    
    def test_delete_nonexistent_phone_entry(self):
        """Test deleting non-existent phone directory entry"""
        
        response = self.client.delete(
            "/phone-directory/99999", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 404
    
    def test_advanced_search_endpoint(self):
        """Test the advanced search POST endpoint"""
        
        # Create test entries
        test_entries = [
            {"الاسم": "أحمد محمد", "الرقم": "01111111111", "الجهه": "وزارة العدل"},
            {"الاسم": "محمد علي", "الرقم": "01222222222", "الجهه": "المحكمة"},
        ]
        
        for entry in test_entries:
            self.client.post(
                "/phone-directory/", 
                json=entry,
                headers=self.admin_headers
            )
        
        # Test advanced search
        search_data = {
            "search_term": "محمد",
            "page": 1,
            "size": 10
        }
        
        response = self.client.post(
            "/phone-directory/search", 
            json=search_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
    
    def test_phone_entry_validation(self):
        """Test validation of phone directory fields"""
        
        # Test whitespace trimming
        entry_data = {
            "الاسم": "  أحمد محمد  ",
            "الرقم": "  01234567890  ",
            "الجهه": "  وزارة العدل  "
        }
        
        response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["الاسم"] == "أحمد محمد"
        assert data["الرقم"] == "01234567890"
        assert data["الجهه"] == "وزارة العدل"
        
        # Test empty string handling
        entry_data_empty = {
            "الاسم": "",
            "الرقم": "   ",
            "الجهه": "صالح"
        }
        
        response = self.client.post(
            "/phone-directory/", 
            json=entry_data_empty,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["الاسم"] is None
        assert data["الرقم"] is None
        assert data["الجهه"] == "صالح"
    
    def test_unauthorized_access(self):
        """Test that all endpoints require authentication"""
        
        endpoints = [
            ("GET", "/phone-directory/"),
            ("POST", "/phone-directory/"),
            ("GET", "/phone-directory/1"),
            ("PUT", "/phone-directory/1"),
            ("DELETE", "/phone-directory/1"),
            ("POST", "/phone-directory/search")
        ]
        
        for method, endpoint in endpoints:
            if method == "GET":
                response = self.client.get(endpoint)
            elif method == "POST":
                response = self.client.post(endpoint, json={})
            elif method == "PUT":
                response = self.client.put(endpoint, json={})
            elif method == "DELETE":
                response = self.client.delete(endpoint)
            
            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"


class TestPhoneDirectoryModels:
    """Test phone directory Pydantic models"""
    
    def test_phone_directory_base_model(self):
        """Test PhoneDirectoryBase model"""
        from models.phone_directory import PhoneDirectoryBase
        
        # Test with all fields
        model = PhoneDirectoryBase(
            الاسم="أحمد محمد",
            الرقم="01234567890",
            الجهه="وزارة العدل"
        )
        
        assert model.الاسم == "أحمد محمد"
        assert model.الرقم == "01234567890"
        assert model.الجهه == "وزارة العدل"
        
        # Test with optional fields
        model_empty = PhoneDirectoryBase()
        assert model_empty.الاسم is None
        assert model_empty.الرقم is None
        assert model_empty.الجهه is None
    
    def test_phone_directory_validation(self):
        """Test field validation in models"""
        from models.phone_directory import PhoneDirectoryBase
        
        # Test whitespace trimming
        model = PhoneDirectoryBase(
            الاسم="  محمد علي  ",
            الرقم="  01111111111  ",
            الجهه="  المحكمة  "
        )
        
        assert model.الاسم == "محمد علي"
        assert model.الرقم == "01111111111"
        assert model.الجهه == "المحكمة"
        
        # Test empty string conversion to None
        model_empty = PhoneDirectoryBase(
            الاسم="",
            الرقم="   ",
            الجهه="صالح"
        )
        
        assert model_empty.الاسم is None
        assert model_empty.الرقم is None
        assert model_empty.الجهه == "صالح"
    
    def test_search_request_model(self):
        """Test PhoneDirectorySearchRequest model"""
        from models.phone_directory import PhoneDirectorySearchRequest
        
        # Test with search term
        search = PhoneDirectorySearchRequest(
            search_term="محمد",
            page=1,
            size=20
        )
        
        assert search.search_term == "محمد"
        assert search.page == 1
        assert search.size == 20
        
        # Test with specific fields
        specific_search = PhoneDirectorySearchRequest(
            الاسم="أحمد",
            الجهه="وزارة",
            page=2
        )
        
        assert specific_search.الاسم == "أحمد"
        assert specific_search.الجهه == "وزارة"
        assert specific_search.page == 2
        assert specific_search.size == 10  # Default value
    
    def test_search_request_validation(self):
        """Test validation in search request model"""
        from models.phone_directory import PhoneDirectorySearchRequest
        import pytest
        
        # Test invalid page number
        with pytest.raises(ValueError):
            PhoneDirectorySearchRequest(page=0)
        
        # Test invalid size
        with pytest.raises(ValueError):
            PhoneDirectorySearchRequest(size=0)
        
        with pytest.raises(ValueError):
            PhoneDirectorySearchRequest(size=101)  # Max is 100
