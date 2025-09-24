import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestArabicSearch:
    """Test Arabic text search functionality"""
    
    async def setup_arabic_test_data(self, async_client: AsyncClient, admin_token: str):
        """Create test data with various Arabic text patterns"""
        headers = auth_headers(admin_token)
        
        import time
        timestamp = int(time.time() * 1000)
        
        test_cases = [
            {
                "case_number": f"ARABIC/{timestamp}/001",
                "plaintiff": "أحمد محمد الاختبار",
                "defendant": "شركة التطوير العقارية",
                "case_type_id": 1,
                "judgment_type": "حكم اول"
            },
            {
                "case_number": f"ARABIC/{timestamp}/002", 
                "plaintiff": "إبراهيم علي السعودي",
                "defendant": "مؤسسة البناء الحديثة",
                "case_type_id": 1,
                "judgment_type": "حكم اول"
            },
            {
                "case_number": f"ARABIC/{timestamp}/003",
                "plaintiff": "فاطمة الزهراء",
                "defendant": "شركة الأدوية المتقدمة",
                "case_type_id": 2,
                "judgment_type": "حكم اول"
            }
        ]
        
        created_cases = []
        for case_data in test_cases:
            response = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
            if response.status_code == 201:
                created_cases.append(response.json())
        
        return created_cases
    
    async def test_search_with_alef_variations(self, async_client: AsyncClient, admin_token: str):
        """Test search with different Alef forms (أ، إ، آ، ا)"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search with different Alef forms should all return the same results
        search_terms = ["أحمد", "احمد", "إحمد", "آحمد"]
        
        results = []
        for term in search_terms:
            response = await async_client.get(f"/api/v1/cases?search={term}", headers=headers)
            assert response.status_code == 200
            results.append(len(response.json()["items"]))
        
        # All searches should return the same number of results
        assert len(set(results)) <= 1, "Different Alef forms should return same results"
        assert results[0] >= 1, "Should find at least one case with أحمد"
    
    async def test_search_with_haa_taa_variations(self, async_client: AsyncClient, admin_token: str):
        """Test search with Haa and Taa Marbuta variations (ه، ة)"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search with both ه and ة should find "شركة" 
        search_with_haa = await async_client.get("/api/v1/cases?search=شركه", headers=headers)
        search_with_taa = await async_client.get("/api/v1/cases?search=شركة", headers=headers)
        
        assert search_with_haa.status_code == 200
        assert search_with_taa.status_code == 200
        
        haa_results = len(search_with_haa.json()["items"])
        taa_results = len(search_with_taa.json()["items"])
        
        # Both should return similar results
        assert abs(haa_results - taa_results) <= 1
        assert taa_results >= 2, "Should find at least 2 cases with شركة"
    
    async def test_search_with_yaa_variations(self, async_client: AsyncClient, admin_token: str):
        """Test search with Yaa variations (ي، ى)"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search with both ي and ى
        search_with_yaa = await async_client.get("/api/v1/cases?search=علي", headers=headers)
        search_with_alef_maksura = await async_client.get("/api/v1/cases?search=على", headers=headers)
        
        assert search_with_yaa.status_code == 200
        assert search_with_alef_maksura.status_code == 200
        
        yaa_results = len(search_with_yaa.json()["items"])
        maksura_results = len(search_with_alef_maksura.json()["items"])
        
        # Both should return the same results
        assert yaa_results == maksura_results
        assert yaa_results >= 1, "Should find at least 1 case with علي"
    
    async def test_search_case_insensitive(self, async_client: AsyncClient, admin_token: str):
        """Test that search is case insensitive"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search with different cases (though Arabic doesn't have much case variation)
        search_normal = await async_client.get("/api/v1/cases?search=أحمد", headers=headers)
        search_in_sentence = await async_client.get("/api/v1/cases?search=احمد", headers=headers)
        
        assert search_normal.status_code == 200
        assert search_in_sentence.status_code == 200
        
        normal_results = len(search_normal.json()["items"])
        sentence_results = len(search_in_sentence.json()["items"])
        
        assert normal_results == sentence_results
    
    async def test_search_partial_matching(self, async_client: AsyncClient, admin_token: str):
        """Test partial text matching"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search with partial names
        response = await async_client.get("/api/v1/cases?search=أحمد", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should find "أحمد محمد الاختبار"
        assert len(data["items"]) >= 1
        found_case = next((case for case in data["items"] if "أحمد" in case["plaintiff"]), None)
        assert found_case is not None
    
    async def test_search_across_multiple_fields(self, async_client: AsyncClient, admin_token: str):
        """Test search across case number, plaintiff, and defendant fields"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Search for terms that appear in different fields
        searches = [
            ("ARABIC", "case_number"),  # Should find in case numbers
            ("أحمد", "plaintiff"),      # Should find in plaintiff
            ("شركة", "defendant"),      # Should find in defendant
        ]
        
        for search_term, expected_field in searches:
            response = await async_client.get(f"/api/v1/cases?search={search_term}", headers=headers)
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) >= 1, f"Should find results for {search_term}"
    
    async def test_search_with_diacritics(self, async_client: AsyncClient, admin_token: str):
        """Test search ignoring diacritics (tashkeel)"""
        headers = auth_headers(admin_token)
        
        # Create a case with diacritics
        import time
        timestamp = int(time.time() * 1000)
        case_with_diacritics = {
            "case_number": f"DIAC/{timestamp}/2025",
            "plaintiff": "مُحَمَّد الأَحْمَد",
            "defendant": "شَرِكَة التَّطْوِير",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        
        admin_headers = auth_headers(admin_token)
        create_response = await async_client.post("/api/v1/cases", json=case_with_diacritics, headers=admin_headers)
        assert create_response.status_code == 201
        
        # Search without diacritics should still find the case
        search_response = await async_client.get("/api/v1/cases?search=محمد", headers=admin_headers)
        assert search_response.status_code == 200
        data = search_response.json()
        
        # Should find the case even though search term has no diacritics
        assert len(data["items"]) >= 1
        found_case = next((case for case in data["items"] if case["case_number"] == case_with_diacritics["case_number"]), None)
        assert found_case is not None
    
    async def test_search_empty_and_whitespace(self, async_client: AsyncClient, admin_token: str):
        """Test search with empty string and whitespace"""
        headers = auth_headers(admin_token)
        await self.setup_arabic_test_data(async_client, admin_token)
        
        # Empty search should return all cases
        response = await async_client.get("/api/v1/cases?search=", headers=headers)
        assert response.status_code == 200
        
        # Whitespace search should be handled gracefully
        response = await async_client.get("/api/v1/cases?search=   ", headers=headers)
        assert response.status_code == 200
    
    async def test_search_special_characters(self, async_client: AsyncClient, admin_token: str):
        """Test search with special characters"""
        headers = auth_headers(admin_token)
        
        # Create case with special characters
        special_case = {
            "case_number": "SPEC/001/2025",
            "plaintiff": "أحمد (المدعي الأول)",
            "defendant": "شركة ABC - الفرع الرئيسي",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        
        admin_headers = auth_headers(admin_token)
        await async_client.post("/api/v1/cases", json=special_case, headers=admin_headers)
        
        # Search should handle special characters
        searches = ["ABC", "الفرع", "(المدعي"]
        for search_term in searches:
            response = await async_client.get(f"/api/v1/cases?search={search_term}", headers=admin_headers)
            assert response.status_code == 200
            # Should not crash and should return valid JSON
            data = response.json()
            assert "items" in data
    
    async def test_search_performance_with_large_text(self, async_client: AsyncClient, admin_token: str):
        """Test search performance with large Arabic text"""
        headers = auth_headers(admin_token)
        
        # Create case with large Arabic text
        large_text = "أحمد محمد علي الباحث في مجال القانون والعدالة " * 20
        large_case = {
            "case_number": "LARGE/001/2025",
            "plaintiff": large_text,
            "defendant": "شركة كبيرة للتطوير والاستثمار العقاري المتقدم",
            "case_type_id": 1,
            "judgment_type": "حكم اول"
        }
        
        await async_client.post("/api/v1/cases", json=large_case, headers=headers)
        
        # Search in large text should still work
        response = await async_client.get("/api/v1/cases?search=الباحث", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
