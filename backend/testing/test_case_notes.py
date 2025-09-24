import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestCaseNotes:
    """Test case notes endpoints"""
    
    async def setup_test_case(self, async_client: AsyncClient, admin_token: str):
        """Helper method to create a test case"""
        headers = auth_headers(admin_token)
        import time
        timestamp = int(time.time() * 1000)
        new_case = {
            "case_number": f"NOTES/{timestamp}/001",
            "plaintiff": "مدعي للملاحظات",
            "defendant": "مدعي عليه للملاحظات",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        response = await async_client.post("/api/v1/cases", json=new_case, headers=headers)
        return response.json()
    
    async def test_get_case_notes_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting case notes as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/notes", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    async def test_get_case_notes_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test getting case notes as regular user"""
        test_case = await self.setup_test_case(async_client, admin_token)
        user_headers = auth_headers(test_user_token)
        
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/notes", headers=user_headers)
        
        assert response.status_code == 200
    
    async def test_create_case_note_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test creating case note as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_note = {
            "note_text": "هذه ملاحظة تجريبية مهمة للقضية - تحتاج إلى متابعة خاصة"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["case_id"] == test_case["id"]
        assert data["note_text"] == new_note["note_text"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_case_note_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test creating case note as regular user"""
        test_case = await self.setup_test_case(async_client, admin_token)
        user_headers = auth_headers(test_user_token)
        
        new_note = {
            "note_text": "ملاحظة من مستخدم عادي - تم مراجعة الأوراق المطلوبة"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=user_headers)
        
        assert response.status_code == 201
    
    async def test_create_note_for_nonexistent_case(self, async_client: AsyncClient, admin_token: str):
        """Test creating note for non-existent case"""
        headers = auth_headers(admin_token)
        new_note = {
            "note_text": "ملاحظة لقضية غير موجودة"
        }
        
        response = await async_client.post("/api/v1/cases/99999/notes", json=new_note, headers=headers)
        
        assert response.status_code == 404
    
    async def test_create_note_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test creating note with invalid data"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # Test with too short text
        short_note = {
            "note_text": "قصير"  # Less than 5 characters
        }
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=short_note, headers=headers)
        assert response.status_code == 422
        
        # Test with too long text
        long_note = {
            "note_text": "ا" * 2001  # More than 2000 characters
        }
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=long_note, headers=headers)
        assert response.status_code == 422
        
        # Test with empty text
        empty_note = {
            "note_text": ""
        }
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=empty_note, headers=headers)
        assert response.status_code == 422
    
    async def test_get_note_by_id(self, async_client: AsyncClient, admin_token: str):
        """Test getting specific note by ID"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a note
        new_note = {
            "note_text": "ملاحظة للاستعلام - معلومات مهمة عن القضية"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        created_note = create_response.json()
        
        # Then get the note
        response = await async_client.get(f"/api/v1/notes/{created_note['id']}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_note["id"]
        assert data["note_text"] == new_note["note_text"]
    
    async def test_update_note_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test updating note as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a note
        new_note = {
            "note_text": "ملاحظة للتحديث - النص الأصلي"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        created_note = create_response.json()
        
        # Update the note
        update_data = {
            "note_text": "ملاحظة محدثة - تم تعديل المحتوى بنجاح"
        }
        response = await async_client.put(f"/api/v1/notes/{created_note['id']}", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["note_text"] == update_data["note_text"]
    
    async def test_update_note_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test updating note as regular user"""
        # First create a note as admin
        admin_headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_note = {
            "note_text": "ملاحظة للتحديث من مستخدم - النص الأصلي"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=admin_headers)
        created_note = create_response.json()
        
        # Try to update as regular user
        user_headers = auth_headers(test_user_token)
        update_data = {
            "note_text": "ملاحظة محدثة من مستخدم عادي - تم التعديل"
        }
        response = await async_client.put(f"/api/v1/notes/{created_note['id']}", json=update_data, headers=user_headers)
        
        assert response.status_code == 200  # Users can update
    
    async def test_delete_note_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test deleting note as admin"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a note
        new_note = {
            "note_text": "ملاحظة للحذف - سيتم حذف هذه الملاحظة"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        created_note = create_response.json()
        
        # Delete the note
        response = await async_client.delete(f"/api/v1/notes/{created_note['id']}", headers=headers)
        
        assert response.status_code == 200
        
        # Verify note is deleted
        get_response = await async_client.get(f"/api/v1/notes/{created_note['id']}", headers=headers)
        assert get_response.status_code == 404
    
    async def test_delete_note_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test deleting note as regular user (should fail)"""
        # First create a note as admin
        admin_headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        new_note = {
            "note_text": "ملاحظة للحذف من مستخدم - لا يجب أن تُحذف"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=admin_headers)
        created_note = create_response.json()
        
        # Try to delete as regular user
        user_headers = auth_headers(test_user_token)
        response = await async_client.delete(f"/api/v1/notes/{created_note['id']}", headers=user_headers)
        
        assert response.status_code == 403
    
    async def test_create_multiple_notes_for_same_case(self, async_client: AsyncClient, admin_token: str):
        """Test creating multiple notes for the same case"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        notes_data = [
            {"note_text": "الملاحظة الأولى - تم استلام الأوراق"},
            {"note_text": "الملاحظة الثانية - تم مراجعة المستندات"},
            {"note_text": "الملاحظة الثالثة - تحديد موعد الجلسة القادمة"}
        ]
        
        created_notes = []
        for note_data in notes_data:
            response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=note_data, headers=headers)
            assert response.status_code == 201
            created_notes.append(response.json())
        
        # Verify all notes are associated with the same case
        for note in created_notes:
            assert note["case_id"] == test_case["id"]
        
        # Get all notes for the case
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/notes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
    
    async def test_notes_pagination(self, async_client: AsyncClient, admin_token: str):
        """Test notes pagination"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # Create multiple notes
        for i in range(7):
            new_note = {
                "note_text": f"ملاحظة رقم {i+1} - محتوى الملاحظة للاختبار"
            }
            await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        
        # Test pagination
        response = await async_client.get(f"/api/v1/cases/{test_case['id']}/notes?page=1&size=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
        assert len(data["items"]) <= 5
        assert data["total"] >= 7
        
        # Test second page
        response2 = await async_client.get(f"/api/v1/cases/{test_case['id']}/notes?page=2&size=5", headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["page"] == 2
        assert len(data2["items"]) >= 2  # At least 2 remaining notes
    
    async def test_create_note_with_arabic_content(self, async_client: AsyncClient, admin_token: str):
        """Test creating note with complex Arabic content"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        arabic_note = {
            "note_text": "ملاحظة باللغة العربية تتضمن تشكيل: الحُكْمُ النِّهائِيُّ، وأرقام: ١٢٣٤٥، ورموز خاصة: @#$%"
        }
        
        response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=arabic_note, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["note_text"] == arabic_note["note_text"]
    
    async def test_update_note_with_invalid_data(self, async_client: AsyncClient, admin_token: str):
        """Test updating note with invalid data"""
        headers = auth_headers(admin_token)
        test_case = await self.setup_test_case(async_client, admin_token)
        
        # First create a note
        new_note = {
            "note_text": "ملاحظة للتحديث ببيانات خاطئة"
        }
        create_response = await async_client.post(f"/api/v1/cases/{test_case['id']}/notes", json=new_note, headers=headers)
        created_note = create_response.json()
        
        # Try to update with too short text
        short_update = {
            "note_text": "قصير"
        }
        response = await async_client.put(f"/api/v1/notes/{created_note['id']}", json=short_update, headers=headers)
        assert response.status_code == 422
        
        # Try to update with too long text
        long_update = {
            "note_text": "ا" * 2001
        }
        response = await async_client.put(f"/api/v1/notes/{created_note['id']}", json=long_update, headers=headers)
        assert response.status_code == 422
