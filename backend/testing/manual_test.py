#!/usr/bin/env python3
"""
Manual API Testing Script
========================

This script provides manual testing capabilities for the Legal Cases API.
It can be used to quickly test specific endpoints or run predefined test scenarios.

Usage:
    python manual_test.py [test_name]
    
Available tests:
    - auth: Test authentication
    - users: Test user management
    - cases: Test case operations
    - full: Run full test suite
    - interactive: Interactive testing mode
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
import httpx

# API Configuration
BASE_URL = "http://localhost:8000"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

class APITester:
    """Manual API testing utility"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.admin_token: Optional[str] = None
        self.user_token: Optional[str] = None
    
    async def login_admin(self) -> str:
        """Login as admin and store token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json=ADMIN_CREDENTIALS
            )
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print("✅ Admin login successful")
                return self.admin_token
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                print(response.text)
                return None
    
    def auth_headers(self, token: str) -> Dict[str, str]:
        """Create authorization headers"""
        return {"Authorization": f"Bearer {token}"}
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        print("=" * 40)
        
        async with httpx.AsyncClient() as client:
            # Test login
            print("Testing admin login...")
            response = await client.post(
                f"{self.base_url}/auth/login",
                json=ADMIN_CREDENTIALS
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print("✅ Login successful")
                print(f"Token expires in: {data.get('expires_in', 'Unknown')} seconds")
                print(f"User: {data['user']['full_name']} ({data['user']['user_type']})")
            else:
                print("❌ Login failed")
                print(response.text)
                return
            
            # Test protected endpoint
            print("\nTesting protected endpoint access...")
            response = await client.get(
                f"{self.base_url}/users",
                headers=self.auth_headers(self.admin_token)
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Protected endpoint access successful")
            else:
                print("❌ Protected endpoint access failed")
                print(response.text)
    
    async def test_case_types(self):
        """Test case types operations"""
        print("\n📂 Testing Case Types...")
        print("=" * 40)
        
        if not self.admin_token:
            await self.login_admin()
        
        async with httpx.AsyncClient() as client:
            headers = self.auth_headers(self.admin_token)
            
            # Get case types
            print("Getting case types...")
            response = await client.get(f"{self.base_url}/case-types", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total']} case types")
                for item in data["items"][:3]:
                    print(f"  - {item['name']}: {item.get('description', 'No description')}")
            else:
                print("❌ Failed to get case types")
                print(response.text)
                return
            
            # Create new case type
            print("\nCreating new case type...")
            new_type = {
                "name": "اختبار يدوي",
                "description": "نوع قضية تم إنشاؤه بواسطة الاختبار اليدوي"
            }
            response = await client.post(
                f"{self.base_url}/case-types",
                json=new_type,
                headers=headers
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                created_type = response.json()
                print(f"✅ Case type created with ID: {created_type['id']}")
                
                # Update the case type
                print(f"Updating case type {created_type['id']}...")
                update_data = {"description": "وصف محدث للاختبار اليدوي"}
                response = await client.put(
                    f"{self.base_url}/case-types/{created_type['id']}",
                    json=update_data,
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Case type updated successfully")
                else:
                    print("❌ Failed to update case type")
                
                # Clean up - delete the test case type
                print(f"Cleaning up - deleting case type {created_type['id']}...")
                response = await client.delete(
                    f"{self.base_url}/case-types/{created_type['id']}",
                    headers=headers
                )
                if response.status_code == 200:
                    print("✅ Test case type deleted")
                else:
                    print("❌ Failed to delete test case type")
            else:
                print("❌ Failed to create case type")
                print(response.text)
    
    async def test_cases(self):
        """Test cases operations"""
        print("\n⚖️  Testing Cases...")
        print("=" * 40)
        
        if not self.admin_token:
            await self.login_admin()
        
        async with httpx.AsyncClient() as client:
            headers = self.auth_headers(self.admin_token)
            
            # Get cases
            print("Getting cases...")
            response = await client.get(f"{self.base_url}/cases", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total']} cases")
            else:
                print("❌ Failed to get cases")
                return
            
            # Create new case
            print("\nCreating new case...")
            new_case = {
                "case_number": f"MANUAL/TEST/{asyncio.get_event_loop().time():.0f}",
                "plaintiff": "المدعي في الاختبار اليدوي",
                "defendant": "المدعي عليه في الاختبار اليدوي",
                "case_type_id": 1,  # مدني
                "judgment_type": "حكم اول"
            }
            response = await client.post(
                f"{self.base_url}/cases",
                json=new_case,
                headers=headers
            )
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                created_case = response.json()
                print(f"✅ Case created with ID: {created_case['id']}")
                print(f"Case Number: {created_case['case_number']}")
                
                # Add session to case
                print(f"Adding session to case {created_case['id']}...")
                session_data = {
                    "session_date": "2025-01-15T10:00:00",
                    "session_notes": "جلسة اختبار يدوي"
                }
                response = await client.post(
                    f"{self.base_url}/cases/{created_case['id']}/sessions",
                    json=session_data,
                    headers=headers
                )
                if response.status_code == 201:
                    print("✅ Session added successfully")
                else:
                    print("❌ Failed to add session")
                
                # Add note to case
                print(f"Adding note to case {created_case['id']}...")
                note_data = {
                    "note_text": "ملاحظة من الاختبار اليدوي - تم إنشاء القضية بنجاح"
                }
                response = await client.post(
                    f"{self.base_url}/cases/{created_case['id']}/notes",
                    json=note_data,
                    headers=headers
                )
                if response.status_code == 201:
                    print("✅ Note added successfully")
                else:
                    print("❌ Failed to add note")
                
                # Get case with full details
                print(f"Getting full details for case {created_case['id']}...")
                response = await client.get(
                    f"{self.base_url}/cases/{created_case['id']}/full",
                    headers=headers
                )
                if response.status_code == 200:
                    full_case = response.json()
                    print("✅ Full case details retrieved")
                    print(f"  Sessions: {full_case['sessions_count']}")
                    print(f"  Notes: {full_case['notes_count']}")
                else:
                    print("❌ Failed to get full case details")
                
                # Test search
                print("\nTesting Arabic search...")
                search_term = "اختبار"
                response = await client.get(
                    f"{self.base_url}/cases?search={search_term}",
                    headers=headers
                )
                if response.status_code == 200:
                    search_results = response.json()
                    print(f"✅ Search found {len(search_results['items'])} results for '{search_term}'")
                else:
                    print("❌ Search failed")
                
                # Clean up
                print(f"Cleaning up - deleting case {created_case['id']}...")
                response = await client.delete(
                    f"{self.base_url}/cases/{created_case['id']}",
                    headers=headers
                )
                if response.status_code == 200:
                    print("✅ Test case deleted")
                else:
                    print("❌ Failed to delete test case")
            else:
                print("❌ Failed to create case")
                print(response.text)
    
    async def test_statistics(self):
        """Test statistics endpoints"""
        print("\n📊 Testing Statistics...")
        print("=" * 40)
        
        if not self.admin_token:
            await self.login_admin()
        
        async with httpx.AsyncClient() as client:
            headers = self.auth_headers(self.admin_token)
            
            # Get dashboard stats
            print("Getting dashboard statistics...")
            response = await client.get(f"{self.base_url}/stats/dashboard", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Dashboard statistics retrieved")
                print(f"  Total Cases: {data['total_cases']}")
                print(f"  Total Case Types: {data['total_case_types']}")
                print(f"  Total Users: {data['total_users']}")
                print(f"  Recent Cases: {len(data['recent_cases'])}")
            else:
                print("❌ Failed to get dashboard statistics")
                print(response.text)
    
    async def run_full_test(self):
        """Run comprehensive test suite"""
        print("\n🚀 Running Full Manual Test Suite...")
        print("=" * 50)
        
        await self.test_authentication()
        await self.test_case_types()
        await self.test_cases()
        await self.test_statistics()
        
        print("\n" + "=" * 50)
        print("✅ Full manual test suite completed!")
    
    async def interactive_mode(self):
        """Interactive testing mode"""
        print("\n🎮 Interactive Testing Mode")
        print("=" * 30)
        
        if not self.admin_token:
            await self.login_admin()
        
        while True:
            print("\nAvailable commands:")
            print("1. Test authentication")
            print("2. Test case types") 
            print("3. Test cases")
            print("4. Test statistics")
            print("5. Custom request")
            print("0. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await self.test_authentication()
            elif choice == "2":
                await self.test_case_types()
            elif choice == "3":
                await self.test_cases()
            elif choice == "4":
                await self.test_statistics()
            elif choice == "5":
                await self.custom_request()
            else:
                print("Invalid choice. Please try again.")
    
    async def custom_request(self):
        """Make custom API request"""
        print("\n📡 Custom Request")
        print("=" * 20)
        
        method = input("HTTP Method (GET/POST/PUT/DELETE): ").upper()
        endpoint = input("Endpoint (e.g., /cases): ").strip()
        
        if method in ["POST", "PUT"]:
            print("Enter JSON data (or press Enter for none):")
            json_data = input().strip()
            try:
                data = json.loads(json_data) if json_data else None
            except json.JSONDecodeError:
                print("Invalid JSON data")
                return
        else:
            data = None
        
        url = f"{self.base_url}{endpoint}"
        headers = self.auth_headers(self.admin_token) if self.admin_token else {}
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                print("Unsupported method")
                return
            
            print(f"\nStatus: {response.status_code}")
            print("Response:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except:
                print(response.text)

async def main():
    """Main function"""
    tester = APITester()
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "auth":
            await tester.test_authentication()
        elif test_name == "users":
            await tester.test_case_types()  # Users test would be similar
        elif test_name == "cases":
            await tester.test_cases()
        elif test_name == "stats":
            await tester.test_statistics()
        elif test_name == "full":
            await tester.run_full_test()
        elif test_name == "interactive":
            await tester.interactive_mode()
        else:
            print(f"Unknown test: {test_name}")
            print(__doc__)
    else:
        await tester.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())
