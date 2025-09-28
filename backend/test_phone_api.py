#!/usr/bin/env python3
"""
Phone Directory API Integration Test
===================================

Test the phone directory API endpoints directly.
"""

import sys
import os
import requests
import json
import time

def test_api_endpoints():
    """Test phone directory API endpoints"""
    
    print("🌐 Testing Phone Directory API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # First check if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running or not healthy")
            print("   Please start the server first: uvicorn main:app --reload")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server")
        print("   Please start the server first: uvicorn main:app --reload")
        return False
    
    print("✅ Server is running")
    
    # Test authentication (get admin token)
    print("\n🔐 Testing authentication...")
    
    try:
        auth_response = requests.post(f"{base_url}/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"   Response: {auth_response.text}")
            return False
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test create phone entry
    print("\n📝 Testing create phone entry...")
    
    try:
        entry_data = {
            "الاسم": "اختبار محمد API",
            "الرقم": "01999888777",
            "الجهه": "وزارة الاختبار API"
        }
        
        create_response = requests.post(
            f"{base_url}/api/v1/phone-directory/",
            json=entry_data,
            headers=headers
        )
        
        if create_response.status_code != 200:
            print(f"❌ Create failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False
        
        created_entry = create_response.json()
        entry_id = created_entry["id"]
        
        print(f"✅ Create successful, ID: {entry_id}")
        print(f"   Entry: {created_entry['الاسم']} - {created_entry['الرقم']}")
        
    except Exception as e:
        print(f"❌ Create error: {e}")
        return False
    
    # Test get phone entry
    print("\n📖 Testing get phone entry...")
    
    try:
        get_response = requests.get(
            f"{base_url}/api/v1/phone-directory/{entry_id}",
            headers=headers
        )
        
        if get_response.status_code != 200:
            print(f"❌ Get failed: {get_response.status_code}")
            return False
        
        get_data = get_response.json()
        print(f"✅ Get successful: {get_data['الاسم']} - {get_data['الرقم']}")
        
    except Exception as e:
        print(f"❌ Get error: {e}")
        return False
    
    # Test list phone entries
    print("\n📋 Testing list phone entries...")
    
    try:
        list_response = requests.get(
            f"{base_url}/api/v1/phone-directory/",
            headers=headers
        )
        
        if list_response.status_code != 200:
            print(f"❌ List failed: {list_response.status_code}")
            return False
        
        list_data = list_response.json()
        print(f"✅ List successful: {list_data['total']} total entries")
        print(f"   Page {list_data['page']}, Size {list_data['size']}")
        
    except Exception as e:
        print(f"❌ List error: {e}")
        return False
    
    # Test search phone entries
    print("\n🔍 Testing search phone entries...")
    
    try:
        search_response = requests.get(
            f"{base_url}/api/v1/phone-directory/?search=اختبار",
            headers=headers
        )
        
        if search_response.status_code != 200:
            print(f"❌ Search failed: {search_response.status_code}")
            return False
        
        search_data = search_response.json()
        print(f"✅ Search successful: {search_data['total']} results for 'اختبار'")
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False
    
    # Test update phone entry
    print("\n✏️ Testing update phone entry...")
    
    try:
        update_data = {
            "الاسم": "اختبار محمد API محدث",
            "الجهه": "وزارة محدثة"
        }
        
        update_response = requests.put(
            f"{base_url}/api/v1/phone-directory/{entry_id}",
            json=update_data,
            headers=headers
        )
        
        if update_response.status_code != 200:
            print(f"❌ Update failed: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
            return False
        
        updated_entry = update_response.json()
        print(f"✅ Update successful: {updated_entry['الاسم']} - {updated_entry['الجهه']}")
        
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False
    
    # Test delete phone entry (admin only)
    print("\n🗑️ Testing delete phone entry...")
    
    try:
        delete_response = requests.delete(
            f"{base_url}/api/v1/phone-directory/{entry_id}",
            headers=headers
        )
        
        if delete_response.status_code != 200:
            print(f"❌ Delete failed: {delete_response.status_code}")
            print(f"   Response: {delete_response.text}")
            return False
        
        delete_data = delete_response.json()
        print(f"✅ Delete successful: {delete_data['message']}")
        
        # Verify entry is deleted
        verify_response = requests.get(
            f"{base_url}/api/v1/phone-directory/{entry_id}",
            headers=headers
        )
        
        if verify_response.status_code == 404:
            print("✅ Delete verification successful (entry not found)")
        else:
            print("⚠️ Delete verification: entry still exists")
        
    except Exception as e:
        print(f"❌ Delete error: {e}")
        return False
    
    return True

def main():
    """Run API integration test"""
    
    print("🚀 Phone Directory API Integration Test")
    print("=" * 60)
    
    success = test_api_endpoints()
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ All API Integration Tests Passed!")
        print("🎉 Phone Directory API is working correctly!")
    else:
        print("❌ Some API tests failed!")
        print("💡 Make sure the server is running: uvicorn main:app --reload")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
