#!/usr/bin/env python3
"""
Test Phone Directory Models
===========================

Test script for phone directory Pydantic models.
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from models.phone_directory import (
    PhoneDirectoryBase,
    PhoneDirectoryCreate, 
    PhoneDirectoryUpdate,
    PhoneDirectoryResponse,
    PhoneDirectoryListResponse,
    PhoneDirectorySearchRequest
)
from datetime import datetime

def test_phone_directory_models():
    """Test all phone directory models"""
    
    print("🧪 Testing Phone Directory Models...")
    print("=" * 50)
    
    # Test 1: PhoneDirectoryBase
    print("📋 Test 1: PhoneDirectoryBase")
    try:
        base_data = PhoneDirectoryBase(
            الاسم="أحمد محمد",
            الرقم="01234567890", 
            الجهه="وزارة العدل"
        )
        print(f"✅ Base model created: {base_data}")
    except Exception as e:
        print(f"❌ Base model failed: {e}")
    
    # Test 2: Empty/Optional fields
    print("\n📋 Test 2: Optional Fields")
    try:
        empty_data = PhoneDirectoryBase()
        print(f"✅ Empty model created: {empty_data}")
        
        partial_data = PhoneDirectoryBase(الاسم="محمد فقط")
        print(f"✅ Partial model created: {partial_data}")
    except Exception as e:
        print(f"❌ Optional fields failed: {e}")
    
    # Test 3: PhoneDirectoryCreate
    print("\n📋 Test 3: PhoneDirectoryCreate")
    try:
        create_data = PhoneDirectoryCreate(
            الاسم="فاطمة أحمد",
            الرقم="01111111111",
            الجهه="المحكمة الإبتدائية"
        )
        print(f"✅ Create model: {create_data}")
    except Exception as e:
        print(f"❌ Create model failed: {e}")
    
    # Test 4: PhoneDirectoryUpdate  
    print("\n📋 Test 4: PhoneDirectoryUpdate")
    try:
        update_data = PhoneDirectoryUpdate(الرقم="01555555555")
        print(f"✅ Update model: {update_data}")
    except Exception as e:
        print(f"❌ Update model failed: {e}")
    
    # Test 5: PhoneDirectoryResponse
    print("\n📋 Test 5: PhoneDirectoryResponse")
    try:
        response_data = PhoneDirectoryResponse(
            id=1,
            الاسم="خالد عبد الله",
            الرقم="01666666666",
            الجهه="النيابة العامة",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=1
        )
        print(f"✅ Response model: {response_data}")
    except Exception as e:
        print(f"❌ Response model failed: {e}")
    
    # Test 6: PhoneDirectorySearchRequest
    print("\n📋 Test 6: PhoneDirectorySearchRequest")
    try:
        search_data = PhoneDirectorySearchRequest(
            search_term="محمد",
            page=1,
            size=10
        )
        print(f"✅ Search model: {search_data}")
        
        specific_search = PhoneDirectorySearchRequest(
            الاسم="أحمد",
            الجهه="وزارة"
        )
        print(f"✅ Specific search model: {specific_search}")
    except Exception as e:
        print(f"❌ Search model failed: {e}")
    
    # Test 7: Validation
    print("\n📋 Test 7: Field Validation")
    try:
        # Test whitespace trimming
        trimmed = PhoneDirectoryBase(
            الاسم="  محمد علي  ",
            الرقم="  01234567890  ",
            الجهه="  المحكمة  "
        )
        print(f"✅ Whitespace trimming: {trimmed}")
        
        # Test empty string handling
        empty_strings = PhoneDirectoryBase(
            الاسم="",
            الرقم="   ",
            الجهه="صالح"
        )
        print(f"✅ Empty string handling: {empty_strings}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Phone Directory Models Test Completed!")

if __name__ == "__main__":
    test_phone_directory_models()
