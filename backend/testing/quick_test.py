#!/usr/bin/env python3
"""
Quick Test - Verify API is working
==================================

This script performs a quick smoke test to verify the API is accessible.
"""

import asyncio
import httpx
import sys

async def quick_test():
    """Perform quick smoke test"""
    base_url = "http://localhost:8000"
    
    print("🔍 Quick API Test")
    print("=" * 20)
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health check (docs endpoint)
            print("Testing API accessibility...")
            response = await client.get(f"{base_url}/docs")
            
            if response.status_code == 200:
                print("✅ API is accessible")
            else:
                print(f"❌ API not accessible (Status: {response.status_code})")
                return False
            
            # Test login
            print("Testing authentication...")
            response = await client.post(
                f"{base_url}/api/v1/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            
            if response.status_code == 200:
                print("✅ Authentication working")
                token = response.json()["access_token"]
                
                # Test protected endpoint
                print("Testing protected endpoint...")
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(f"{base_url}/api/v1/users", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Protected endpoints working")
                    data = response.json()
                    print(f"   Found {data['total']} users")
                    return True
                else:
                    print(f"❌ Protected endpoint failed (Status: {response.status_code})")
                    return False
            else:
                print(f"❌ Authentication failed (Status: {response.status_code})")
                return False
                
    except httpx.ConnectError:
        print("❌ Cannot connect to API server")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def main():
    success = await quick_test()
    
    if success:
        print("\n🎉 API is working correctly!")
        print("You can now run the full test suite:")
        print("   cd testing && ./run_tests.sh")
        sys.exit(0)
    else:
        print("\n💥 API test failed!")
        print("Please check that:")
        print("1. The server is running (python main.py)")
        print("2. The server is accessible on localhost:8000")
        print("3. The database is properly configured")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
