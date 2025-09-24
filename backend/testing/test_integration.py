import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for complete workflows"""
    
    async def test_complete_case_workflow(self, async_client: AsyncClient, admin_token: str):
        """Test complete case management workflow"""
        headers = auth_headers(admin_token)
        
        # 1. Create a case type
        import time
        timestamp = int(time.time() * 1000)
        case_type_data = {
            "name": f"تكامل {timestamp}",
            "description": "نوع قضية للاختبار التكاملي"
        }
        type_response = await async_client.post("/api/v1/case-types", json=case_type_data, headers=headers)
        assert type_response.status_code == 201
        case_type = type_response.json()
        
        # 2. Create a case
        case_data = {
            "case_number": f"INTEGRATION/{timestamp}/2025",
            "plaintiff": "مدعي التكامل",
            "defendant": "مدعي عليه التكامل",
            "case_type_id": case_type["id"],
            "judgment_type": "حكم اول"
        }
        case_response = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
        assert case_response.status_code == 201
        case = case_response.json()
        
        # 3. Add sessions to the case
        session_data = {
            "session_date": "2025-01-15T10:00:00",
            "session_notes": "الجلسة الأولى للقضية التكاملية"
        }
        session_response = await async_client.post(f"/api/v1/cases/{case['id']}/sessions", json=session_data, headers=headers)
        assert session_response.status_code == 201
        session = session_response.json()
        
        # 4. Add notes to the case
        note_data = {
            "note_text": "ملاحظة تكاملية مهمة للقضية"
        }
        note_response = await async_client.post(f"/api/v1/cases/{case['id']}/notes", json=note_data, headers=headers)
        assert note_response.status_code == 201
        note = note_response.json()
        
        # 5. Update the case
        update_data = {
            "judgment_type": "حكم ثان"
        }
        update_response = await async_client.put(f"/api/v1/cases/{case['id']}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        
        # 6. Get case with full details
        full_response = await async_client.get(f"/api/v1/cases/{case['id']}/full", headers=headers)
        assert full_response.status_code == 200
        full_case = full_response.json()
        
        # Verify all data is connected properly
        assert full_case["judgment_type"] == "حكم ثان"
        assert full_case["case_type"]["id"] == case_type["id"]
        assert full_case["sessions_count"] >= 1
        assert full_case["notes_count"] >= 1
        
        # 7. Check statistics reflect the new data
        stats_response = await async_client.get("/api/v1/stats/dashboard", headers=headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        # Should include our new case in statistics
        assert stats["total_cases"] >= 1
        
        # Find our case type in statistics
        our_type_stats = next((item for item in stats["cases_by_type"] if item["name"] == "تكامل"), None)
        assert our_type_stats is not None
        assert our_type_stats["case_count"] >= 1
    
    async def test_user_permissions_workflow(self, async_client: AsyncClient, admin_token: str, test_user_token: str):
        """Test complete workflow respecting user permissions"""
        admin_headers = auth_headers(admin_token)
        user_headers = auth_headers(test_user_token)
        
        # 1. Admin creates case type
        import time
        timestamp = int(time.time() * 1000)
        case_type_data = {
            "name": f"صلاحيات {timestamp}",
            "description": "نوع قضية لاختبار الصلاحيات"
        }
        type_response = await async_client.post("/api/v1/case-types", json=case_type_data, headers=admin_headers)
        assert type_response.status_code == 201
        case_type = type_response.json()
        
        # 2. Regular user creates case
        case_data = {
            "case_number": f"PERMS/{timestamp}/2025",
            "plaintiff": "مدعي الصلاحيات",
            "defendant": "مدعي عليه الصلاحيات",
            "case_type_id": case_type["id"],
            "judgment_type": "حكم اول"
        }
        case_response = await async_client.post("/api/v1/cases", json=case_data, headers=user_headers)
        assert case_response.status_code == 201
        case = case_response.json()
        
        # 3. Regular user adds session and note
        session_response = await async_client.post(f"/api/v1/cases/{case['id']}/sessions", 
            json={"session_notes": "جلسة من المستخدم"}, headers=user_headers)
        assert session_response.status_code == 201
        
        note_response = await async_client.post(f"/api/v1/cases/{case['id']}/notes",
            json={"note_text": "ملاحظة من المستخدم العادي"}, headers=user_headers)
        assert note_response.status_code == 201
        
        # 4. Regular user tries to delete case (should fail)
        delete_response = await async_client.delete(f"/api/v1/cases/{case['id']}", headers=user_headers)
        assert delete_response.status_code == 403
        
        # 5. Admin can delete the case
        admin_delete_response = await async_client.delete(f"/api/v1/cases/{case['id']}", headers=admin_headers)
        assert admin_delete_response.status_code == 200
        
        # 6. Verify case is deleted
        get_response = await async_client.get(f"/api/v1/cases/{case['id']}", headers=admin_headers)
        assert get_response.status_code == 404
    
    async def test_search_and_filtering_workflow(self, async_client: AsyncClient, admin_token: str):
        """Test complete search and filtering workflow"""
        headers = auth_headers(admin_token)
        
        # Create multiple cases with different attributes
        import time
        timestamp = int(time.time() * 1000)
        cases_data = [
            {
                "case_number": f"SEARCH/CIVIL/{timestamp}",
                "plaintiff": "أحمد البحث المدني",
                "defendant": "شركة البحث المدنية",
                "case_type_id": 1,  # مدني
                "judgment_type": "حكم اول"
            },
            {
                "case_number": f"SEARCH/CRIMINAL/{timestamp}",
                "plaintiff": "محمد البحث الجنائي",
                "defendant": "المتهم في القضية الجنائية",
                "case_type_id": 2,  # جنائي
                "judgment_type": "حكم ثان"
            },
            {
                "case_number": f"SEARCH/COMMERCIAL/{timestamp}",
                "plaintiff": "علي البحث التجاري",
                "defendant": "الشركة التجارية المدعى عليها",
                "case_type_id": 3,  # تجاري
                "judgment_type": "حكم اول"
            }
        ]
        
        created_cases = []
        for case_data in cases_data:
            response = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
            assert response.status_code == 201
            created_cases.append(response.json())
        
        # Test various search and filter combinations
        
        # 1. Search by plaintiff name
        search_response = await async_client.get("/api/v1/cases?search=أحمد", headers=headers)
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results["items"]) >= 1
        found_ahmed = any("أحمد" in case["plaintiff"] for case in search_results["items"])
        assert found_ahmed
        
        # 2. Filter by case type
        filter_response = await async_client.get("/api/v1/cases?case_type_id=1", headers=headers)
        assert filter_response.status_code == 200
        filter_results = filter_response.json()
        for case in filter_results["items"]:
            assert case["case_type_id"] == 1
        
        # 3. Filter by judgment type
        judgment_response = await async_client.get("/api/v1/cases?judgment_type=حكم اول", headers=headers)
        assert judgment_response.status_code == 200
        judgment_results = judgment_response.json()
        for case in judgment_results["items"]:
            assert case["judgment_type"] == "حكم اول"
        
        # 4. Combined search and filter
        combined_response = await async_client.get("/api/v1/cases?search=البحث&case_type_id=1", headers=headers)
        assert combined_response.status_code == 200
        combined_results = combined_response.json()
        for case in combined_results["items"]:
            assert case["case_type_id"] == 1
            assert "البحث" in case["plaintiff"] or "البحث" in case["defendant"]
        
        # 5. Pagination with filters
        paginated_response = await async_client.get("/api/v1/cases?case_type_id=1&page=1&size=2", headers=headers)
        assert paginated_response.status_code == 200
        paginated_results = paginated_response.json()
        assert paginated_results["size"] == 2
        assert len(paginated_results["items"]) <= 2
    
    async def test_error_handling_workflow(self, async_client: AsyncClient, admin_token: str):
        """Test comprehensive error handling"""
        headers = auth_headers(admin_token)
        
        # 1. Try to create case with invalid case type
        import time
        timestamp = int(time.time() * 1000)
        invalid_case = {
            "case_number": f"ERROR/{timestamp}/2025",
            "plaintiff": "مدعي خطأ",
            "defendant": "مدعي عليه خطأ",
            "case_type_id": 99999,  # Non-existent
            "judgment_type": "حكم اول"
        }
        response = await async_client.post("/api/v1/cases", json=invalid_case, headers=headers)
        assert response.status_code in [400, 422]
        
        # 2. Try to add session to non-existent case
        session_data = {
            "session_notes": "جلسة لقضية غير موجودة"
        }
        response = await async_client.post("/api/v1/cases/99999/sessions", json=session_data, headers=headers)
        assert response.status_code == 404
        
        # 3. Try to access non-existent resources
        endpoints_to_test = [
            "/api/v1/cases/99999",
            "/api/v1/case-types/99999", 
            "/case-sessions/99999",
            "/case-notes/99999",
            "/api/v1/users/99999"
        ]
        
        for endpoint in endpoints_to_test:
            response = await async_client.get(endpoint, headers=headers)
            assert response.status_code == 404
        
        # 4. Try to update non-existent resources
        update_endpoints = [
            ("/api/v1/cases/99999", {"plaintiff": "محدث"}),
            ("/api/v1/case-types/99999", {"name": "محدث"}),
            ("/case-sessions/99999", {"session_notes": "محدث"}),
            ("/case-notes/99999", {"note_text": "ملاحظة محدثة"}),
            ("/api/v1/users/99999", {"full_name": "محدث"})
        ]
        
        for endpoint, data in update_endpoints:
            response = await async_client.put(endpoint, json=data, headers=headers)
            assert response.status_code == 404
        
        # 5. Try invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/cases", headers=invalid_headers)
        assert response.status_code == 401
    
    async def test_cascade_operations(self, async_client: AsyncClient, admin_token: str):
        """Test cascade operations (e.g., deleting case should handle related data)"""
        headers = auth_headers(admin_token)
        
        # 1. Create complete case with sessions and notes
        import time
        timestamp = int(time.time() * 1000)
        case_data = {
            "case_number": f"CASCADE/{timestamp}/2025",
            "plaintiff": "مدعي الحذف المتسلسل",
            "defendant": "مدعي عليه الحذف المتسلسل",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        case_response = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
        case = case_response.json()
        
        # 2. Add sessions and notes
        session_response = await async_client.post(f"/api/v1/cases/{case['id']}/sessions",
            json={"session_notes": "جلسة للحذف المتسلسل"}, headers=headers)
        session = session_response.json()
        
        note_response = await async_client.post(f"/api/v1/cases/{case['id']}/notes",
            json={"note_text": "ملاحظة للحذف المتسلسل"}, headers=headers)
        note = note_response.json()
        
        # 3. Verify all created successfully
        assert case_response.status_code == 201
        assert session_response.status_code == 201
        assert note_response.status_code == 201
        
        # 4. Delete the case
        delete_response = await async_client.delete(f"/api/v1/cases/{case['id']}", headers=headers)
        assert delete_response.status_code == 200
        
        # 5. Verify case and related data are deleted
        case_check = await async_client.get(f"/api/v1/cases/{case['id']}", headers=headers)
        assert case_check.status_code == 404
        
        session_check = await async_client.get(f"/case-sessions/{session['id']}", headers=headers)
        assert session_check.status_code == 404
        
        note_check = await async_client.get(f"/case-notes/{note['id']}", headers=headers)
        assert note_check.status_code == 404
