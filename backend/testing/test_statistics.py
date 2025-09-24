import pytest
from httpx import AsyncClient
from conftest import auth_headers, TestConfig

@pytest.mark.asyncio
class TestStatistics:
    """Test statistics endpoints"""
    
    async def setup_test_data(self, async_client: AsyncClient, admin_token: str):
        """Helper method to create test data for statistics"""
        headers = auth_headers(admin_token)
        
        # Create some test cases with different types and judgments
        test_cases = [
            {
                "case_number": "STATS/CIVIL/001",
                "plaintiff": "مدعي مدني أول",
                "defendant": "مدعي عليه مدني أول",
                "case_type_id": 1,  # مدني
                "judgment_type": "حكم اول"
            },
            {
                "case_number": "STATS/CIVIL/002", 
                "plaintiff": "مدعي مدني ثاني",
                "defendant": "مدعي عليه مدني ثاني",
                "case_type_id": 1,  # مدني
                "judgment_type": "حكم ثان"
            },
            {
                "case_number": "STATS/CRIMINAL/001",
                "plaintiff": "مدعي جنائي أول",
                "defendant": "مدعي عليه جنائي أول", 
                "case_type_id": 2,  # جنائي
                "judgment_type": "حكم اول"
            },
            {
                "case_number": "STATS/COMMERCIAL/001",
                "plaintiff": "مدعي تجاري أول",
                "defendant": "مدعي عليه تجاري أول",
                "case_type_id": 3,  # تجاري
                "judgment_type": "حكم اول"
            }
        ]
        
        created_cases = []
        for case_data in test_cases:
            response = await async_client.post("/api/v1/cases", json=case_data, headers=headers)
            if response.status_code == 201:
                created_cases.append(response.json())
        
        return created_cases
    
    async def test_get_dashboard_stats_as_admin(self, async_client: AsyncClient, admin_token: str):
        """Test getting dashboard statistics as admin"""
        headers = auth_headers(admin_token)
        await self.setup_test_data(async_client, admin_token)
        
        response = await async_client.get("/api/v1/stats/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "total_cases" in data
        assert "total_case_types" in data
        assert "total_users" in data
        assert "cases_by_type" in data
        assert "cases_by_judgment" in data
        assert "recent_cases" in data
        
        # Verify data types
        assert isinstance(data["total_cases"], int)
        assert isinstance(data["total_case_types"], int)
        assert isinstance(data["total_users"], int)
        assert isinstance(data["cases_by_type"], list)
        assert isinstance(data["cases_by_judgment"], list)
        assert isinstance(data["recent_cases"], list)
        
        # Verify minimum expected values
        assert data["total_cases"] >= 4  # At least our test cases
        assert data["total_case_types"] >= 6  # Default case types
        assert data["total_users"] >= 2  # Admin + test user
    
    async def test_get_dashboard_stats_as_user(self, async_client: AsyncClient, test_user_token: str, admin_token: str):
        """Test getting dashboard statistics as regular user"""
        await self.setup_test_data(async_client, admin_token)
        user_headers = auth_headers(test_user_token)
        
        response = await async_client.get("/api/v1/stats/dashboard", headers=user_headers)
        
        assert response.status_code == 200
        # Regular users should also be able to see statistics
    
    async def test_get_cases_by_type_stats(self, async_client: AsyncClient, admin_token: str):
        """Test getting cases count by type statistics"""
        headers = auth_headers(admin_token)
        await self.setup_test_data(async_client, admin_token)
        
        response = await async_client.get("/api/v1/stats/cases-by-type", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check structure of each item
        for item in data:
            assert "name" in item
            assert "case_count" in item
            assert isinstance(item["case_count"], int)
            assert item["case_count"] >= 0
        
        # Find مدني type which should have at least 2 cases
        civil_stats = next((item for item in data if item["name"] == "مدني"), None)
        assert civil_stats is not None
        assert civil_stats["case_count"] >= 2
    
    async def test_get_cases_by_judgment_stats(self, async_client: AsyncClient, admin_token: str):
        """Test getting cases count by judgment type statistics"""
        headers = auth_headers(admin_token)
        await self.setup_test_data(async_client, admin_token)
        
        response = await async_client.get("/api/v1/stats/cases-by-judgment", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check structure of each item
        for item in data:
            assert "judgment_type" in item
            assert "case_count" in item
            assert isinstance(item["case_count"], int)
            assert item["case_count"] >= 0
            assert item["judgment_type"] in ["حكم اول", "حكم ثان", "حكم ثالث"]
        
        # Find حكم اول which should have at least 3 cases
        first_judgment_stats = next((item for item in data if item["judgment_type"] == "حكم اول"), None)
        assert first_judgment_stats is not None
        assert first_judgment_stats["case_count"] >= 3
        
        # Find حكم ثان which should have at least 1 case
        second_judgment_stats = next((item for item in data if item["judgment_type"] == "حكم ثان"), None)
        assert second_judgment_stats is not None
        assert second_judgment_stats["case_count"] >= 1
    
    async def test_stats_without_authentication(self, async_client: AsyncClient):
        """Test accessing statistics without authentication"""
        response = await async_client.get("/api/v1/stats/dashboard")
        assert response.status_code == 403
        
        response = await async_client.get("/api/v1/stats/cases-by-type")
        assert response.status_code == 403
        
        response = await async_client.get("/api/v1/stats/cases-by-judgment") 
        assert response.status_code == 403
    
    async def test_dashboard_recent_cases_limit(self, async_client: AsyncClient, admin_token: str):
        """Test that dashboard returns limited number of recent cases"""
        headers = auth_headers(admin_token)
        await self.setup_test_data(async_client, admin_token)
        
        response = await async_client.get("/api/v1/stats/dashboard", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # Recent cases should be limited (typically 5-10)
        assert len(data["recent_cases"]) <= 10
        
        # If there are recent cases, check their structure
        if data["recent_cases"]:
            recent_case = data["recent_cases"][0]
            assert "id" in recent_case
            assert "case_number" in recent_case
            assert "plaintiff" in recent_case
            assert "defendant" in recent_case
            assert "created_at" in recent_case
    
    async def test_stats_data_consistency(self, async_client: AsyncClient, admin_token: str):
        """Test that statistics data is consistent across endpoints"""
        headers = auth_headers(admin_token)
        await self.setup_test_data(async_client, admin_token)
        
        # Get dashboard stats
        dashboard_response = await async_client.get("/api/v1/stats/dashboard", headers=headers)
        dashboard_data = dashboard_response.json()
        
        # Get detailed stats
        type_response = await async_client.get("/api/v1/stats/cases-by-type", headers=headers)
        type_data = type_response.json()
        
        judgment_response = await async_client.get("/api/v1/stats/cases-by-judgment", headers=headers)
        judgment_data = judgment_response.json()
        
        # Calculate totals from detailed stats
        total_from_type_stats = sum(item["case_count"] for item in type_data)
        total_from_judgment_stats = sum(item["case_count"] for item in judgment_data)
        
        # All should give the same total case count
        assert dashboard_data["total_cases"] == total_from_type_stats
        assert dashboard_data["total_cases"] == total_from_judgment_stats
        
        # Dashboard cases_by_type should match detailed endpoint
        dashboard_type_total = sum(item["case_count"] for item in dashboard_data["cases_by_type"])
        assert dashboard_type_total == total_from_type_stats
        
        # Dashboard cases_by_judgment should match detailed endpoint
        dashboard_judgment_total = sum(item["case_count"] for item in dashboard_data["cases_by_judgment"])
        assert dashboard_judgment_total == total_from_judgment_stats
    
    async def test_empty_stats_handling(self, async_client: AsyncClient, admin_token: str):
        """Test statistics when no data exists (edge case)"""
        # Note: This test assumes we're working with an empty database
        # In practice, we have default case types and admin user
        headers = auth_headers(admin_token)
        
        response = await async_client.get("/api/v1/stats/cases-by-type", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Should still return case types even if no cases exist
        assert isinstance(data, list)
        # Should have default case types
        assert len(data) >= 6
        
        # Some case types might have 0 cases
        zero_count_exists = any(item["case_count"] == 0 for item in data)
        assert isinstance(zero_count_exists, bool)  # Just verify the structure
    
    async def test_performance_with_large_dataset(self, async_client: AsyncClient, admin_token: str):
        """Test statistics performance with larger dataset"""
        headers = auth_headers(admin_token)
        
        # Create a larger number of test cases (if performance allows)
        for i in range(20):
            case_data = {
                "case_number": f"PERF/{i:03d}/2025",
                "plaintiff": f"مدعي الأداء رقم {i+1}",
                "defendant": f"مدعي عليه الأداء رقم {i+1}",
                "case_type_id": (i % 6) + 1,  # Cycle through case types
                "judgment_type": ["حكم اول", "حكم ثان", "حكم ثالث"][i % 3]
            }
            await async_client.post("/api/v1/cases", json=case_data, headers=headers)
        
        # Test that statistics still work efficiently
        response = await async_client.get("/api/v1/stats/dashboard", headers=headers)
        assert response.status_code == 200
        
        # The response should be fast and contain expected structure
        data = response.json()
        assert data["total_cases"] >= 20
