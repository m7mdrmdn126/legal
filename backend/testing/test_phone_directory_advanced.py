"""
Phone Directory Performance & Edge Case Tests
============================================

Additional tests for phone directory feature including performance,
edge cases, and stress testing.
"""

import pytest
import time
from httpx import AsyncClient
from fastapi.testclient import TestClient

class TestPhoneDirectoryPerformance:
    """Performance and stress tests for phone directory"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, test_client, admin_token):
        """Setup method run before each test"""
        self.client = test_client
        self.admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Clear phone directory
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
    
    def test_create_many_entries_performance(self):
        """Test creating many entries and measure performance"""
        
        entry_count = 50
        start_time = time.time()
        
        # Create many entries
        for i in range(entry_count):
            entry_data = {
                "الاسم": f"شخص رقم {i+1}",
                "الرقم": f"01{i:08d}",
                "الجهه": f"جهة رقم {(i % 5) + 1}"
            }
            
            response = self.client.post(
                "/phone-directory/", 
                json=entry_data,
                headers=self.admin_headers
            )
            assert response.status_code == 200
        
        elapsed_time = time.time() - start_time
        avg_time_per_entry = elapsed_time / entry_count
        
        print(f"\n📊 Performance Results:")
        print(f"   Created {entry_count} entries in {elapsed_time:.2f} seconds")
        print(f"   Average time per entry: {avg_time_per_entry:.3f} seconds")
        
        # Performance assertion (should be less than 100ms per entry)
        assert avg_time_per_entry < 0.1, f"Performance too slow: {avg_time_per_entry:.3f}s per entry"
    
    def test_search_performance_with_many_entries(self):
        """Test search performance with many entries"""
        
        # Create 100 test entries
        entry_count = 100
        for i in range(entry_count):
            entry_data = {
                "الاسم": f"اسم{i:03d} محمد" if i % 2 == 0 else f"فاطمة علي{i:03d}",
                "الرقم": f"01{i:08d}",
                "الجهه": f"جهة{i % 10}"
            }
            
            response = self.client.post(
                "/phone-directory/", 
                json=entry_data,
                headers=self.admin_headers
            )
            assert response.status_code == 200
        
        # Test search performance
        search_terms = ["محمد", "فاطمة", "جهة5", "01000"]
        
        for search_term in search_terms:
            start_time = time.time()
            
            response = self.client.get(
                f"/phone-directory/?search={search_term}", 
                headers=self.admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            
            print(f"   Search '{search_term}': {elapsed_time:.3f}s, {data['total']} results")
            
            # Search should be fast (less than 500ms)
            assert elapsed_time < 0.5, f"Search too slow: {elapsed_time:.3f}s"
    
    def test_pagination_performance(self):
        """Test pagination performance"""
        
        # Create 50 entries
        for i in range(50):
            entry_data = {
                "الاسم": f"شخص {i+1:02d}",
                "الرقم": f"01{i:08d}"
            }
            self.client.post(
                "/phone-directory/", 
                json=entry_data,
                headers=self.admin_headers
            )
        
        # Test different page sizes
        page_sizes = [5, 10, 25]
        
        for size in page_sizes:
            start_time = time.time()
            
            response = self.client.get(
                f"/phone-directory/?page=1&size={size}", 
                headers=self.admin_headers
            )
            
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            data = response.json()
            
            assert len(data["items"]) == size
            assert data["total"] == 50
            
            print(f"   Page size {size}: {elapsed_time:.3f}s")
            
            # Pagination should be fast
            assert elapsed_time < 0.2

class TestPhoneDirectoryEdgeCases:
    """Edge cases and boundary tests"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self, test_client, admin_token):
        """Setup method run before each test"""
        self.client = test_client
        self.admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    def test_arabic_text_handling(self):
        """Test proper handling of Arabic text"""
        
        # Test various Arabic text scenarios
        arabic_entries = [
            {
                "الاسم": "محمد أحمد عبد الرحمن الطويل الاسم",
                "الرقم": "٠١٢٣٤٥٦٧٨٩٠",  # Arabic-Indic digits
                "الجهه": "وزارة العدل والشؤون الإسلامية والأوقاف"
            },
            {
                "الاسم": "أ.د. محمد عبد الله (أستاذ القانون)",
                "الرقم": "+20-12-3456-7890",  # International format
                "الجهه": "جامعة الأزهر - كلية الحقوق"
            },
            {
                "الاسم": "شركة المحاماة المتحدة ش.م.م",
                "الرقم": "02-123-456-78 تحويلة 123",
                "الجهه": "القطاع الخاص"
            }
        ]
        
        created_ids = []
        
        # Create entries
        for entry in arabic_entries:
            response = self.client.post(
                "/phone-directory/", 
                json=entry,
                headers=self.admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            created_ids.append(data["id"])
            
            # Verify Arabic text is preserved
            assert data["الاسم"] == entry["الاسم"]
            assert data["الرقم"] == entry["الرقم"]
            assert data["الجهه"] == entry["الجهه"]
        
        # Test searching Arabic text
        search_tests = [
            ("محمد", 2),  # Should find 2 entries
            ("وزارة", 1),  # Should find 1 entry
            ("القانون", 1),  # Should find 1 entry
            ("ش.م.م", 1)   # Should find 1 entry
        ]
        
        for search_term, expected_count in search_tests:
            response = self.client.get(
                f"/phone-directory/?search={search_term}", 
                headers=self.admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == expected_count, f"Search '{search_term}' expected {expected_count}, got {data['total']}"
    
    def test_special_characters_handling(self):
        """Test handling of special characters"""
        
        special_entries = [
            {
                "الاسم": "John Smith (English Name)",
                "الرقم": "+1-555-123-4567",
                "الجهه": "US Embassy"
            },
            {
                "الاسم": "Marie Dupont",
                "الرقم": "+33-1-42-34-56-78",
                "الجهه": "French Consulate"
            },
            {
                "الاسم": "测试用户",  # Chinese characters
                "الرقم": "+86-138-0013-8000",
                "الجهه": "Chinese Embassy"
            }
        ]
        
        for entry in special_entries:
            response = self.client.post(
                "/phone-directory/", 
                json=entry,
                headers=self.admin_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify special characters are preserved
            assert data["الاسم"] == entry["الاسم"]
            assert data["الرقم"] == entry["الرقم"]
            assert data["الجهه"] == entry["الجهه"]
    
    def test_very_long_text_fields(self):
        """Test handling of very long text in fields"""
        
        # Test with very long strings
        long_name = "محمد " * 50  # Very long name
        long_phone = "01234567890" * 10  # Very long phone
        long_org = "وزارة العدل " * 20  # Very long organization
        
        entry_data = {
            "الاسم": long_name,
            "الرقم": long_phone,
            "الجهه": long_org
        }
        
        response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify long text is preserved
        assert data["الاسم"] == long_name
        assert data["الرقم"] == long_phone
        assert data["الجهه"] == long_org
        
        # Test searching in long text
        response = self.client.get(
            "/phone-directory/?search=محمد", 
            headers=self.admin_headers
        )
        
        assert response.status_code == 200
        search_data = response.json()
        assert search_data["total"] >= 1
    
    def test_null_and_empty_handling(self):
        """Test proper handling of null and empty values"""
        
        test_cases = [
            {"الاسم": None, "الرقم": None, "الجهه": None},
            {"الاسم": "", "الرقم": "", "الجهه": ""},
            {"الاسم": "   ", "الرقم": "   ", "الجهه": "   "},
            {"الاسم": "Valid", "الرقم": None, "الجهه": ""},
        ]
        
        for i, case in enumerate(test_cases):
            response = self.client.post(
                "/phone-directory/", 
                json=case,
                headers=self.admin_headers
            )
            
            assert response.status_code == 200, f"Case {i} failed: {case}"
            data = response.json()
            
            # Verify empty strings are converted to None
            if case["الاسم"] in [None, "", "   "]:
                assert data["الاسم"] is None or data["الاسم"] == "Valid"
            
            if case["الرقم"] in [None, "", "   "]:
                assert data["الرقم"] is None
                
            if case["الجهه"] in [None, "", "   "]:
                assert data["الجهه"] is None
    
    def test_concurrent_operations(self):
        """Test handling of concurrent operations"""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_entry(entry_num):
            try:
                entry_data = {
                    "الاسم": f"مستخدم متزامن {entry_num}",
                    "الرقم": f"0123456{entry_num:04d}",
                    "الجهه": f"جهة {entry_num}"
                }
                
                response = self.client.post(
                    "/phone-directory/", 
                    json=entry_data,
                    headers=self.admin_headers
                )
                
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    errors.append(f"Entry {entry_num}: {response.status_code}")
                    
            except Exception as e:
                errors.append(f"Entry {entry_num}: {str(e)}")
        
        # Create 10 entries concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_entry, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent operation errors: {errors}"
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        
        # Verify all entries were created with unique IDs
        ids = [result["id"] for result in results]
        assert len(set(ids)) == 10, "Duplicate IDs found in concurrent operations"
    
    def test_database_integrity_after_operations(self):
        """Test database integrity after various operations"""
        
        # Create entry
        entry_data = {"الاسم": "اختبار التكامل", "الرقم": "01111111111"}
        create_response = self.client.post(
            "/phone-directory/", 
            json=entry_data,
            headers=self.admin_headers
        )
        assert create_response.status_code == 200
        
        entry_id = create_response.json()["id"]
        
        # Update entry
        update_response = self.client.put(
            f"/phone-directory/{entry_id}", 
            json={"الاسم": "محدث"},
            headers=self.admin_headers
        )
        assert update_response.status_code == 200
        
        # Verify database consistency
        get_response = self.client.get(
            f"/phone-directory/{entry_id}", 
            headers=self.admin_headers
        )
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["الاسم"] == "محدث"
        assert data["الرقم"] == "01111111111"  # Should remain unchanged
        
        # Verify in list
        list_response = self.client.get(
            "/phone-directory/", 
            headers=self.admin_headers
        )
        assert list_response.status_code == 200
        
        list_data = list_response.json()
        found_entry = None
        for item in list_data["items"]:
            if item["id"] == entry_id:
                found_entry = item
                break
        
        assert found_entry is not None
        assert found_entry["الاسم"] == "محدث"
        
        print("\n✅ Database integrity verified after all operations")
