#!/usr/bin/env python3
"""
Test Phone Directory Routes
===========================

Test script for phone directory API routes.
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

def test_routes_import():
    """Test that the routes can be imported without errors"""
    
    print("🧪 Testing Phone Directory Routes Import...")
    print("=" * 50)
    
    try:
        from routes.phone_directory import router
        print("✅ Phone directory routes imported successfully")
        
        # Check router configuration
        print(f"📋 Router prefix: {router.prefix}")
        print(f"📋 Router tags: {router.tags}")
        
        # Check available routes
        routes = router.routes
        print(f"📋 Available routes: {len(routes)}")
        
        for route in routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = list(route.methods)
                print(f"   {methods} {router.prefix}{route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Routes import failed: {e}")
        return False

def test_models_integration():
    """Test that models integrate correctly with routes"""
    
    print("\n🧪 Testing Models Integration...")
    print("=" * 50)
    
    try:
        from models.phone_directory import (
            PhoneDirectoryCreate,
            PhoneDirectoryUpdate, 
            PhoneDirectoryResponse
        )
        
        # Test create model
        create_data = PhoneDirectoryCreate(
            الاسم="اختبار الاسم",
            الرقم="01234567890",
            الجهه="جهة اختبار"
        )
        print(f"✅ Create model: {create_data}")
        
        # Test update model
        update_data = PhoneDirectoryUpdate(الرقم="09876543210")
        print(f"✅ Update model: {update_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models integration failed: {e}")
        return False

def test_database_integration():
    """Test database connectivity"""
    
    print("\n🧪 Testing Database Integration...")
    print("=" * 50)
    
    try:
        from config.database import db_manager
        
        # Test basic query
        result = db_manager.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='phone_directory'
        """)
        
        if result:
            print("✅ Phone directory table found in database")
            
            # Test table structure
            structure = db_manager.execute_query("PRAGMA table_info(phone_directory)")
            print("📋 Table structure:")
            for col in structure:
                print(f"   - {col['name']}: {col['type']}")
            
            return True
        else:
            print("❌ Phone directory table not found")
            return False
            
    except Exception as e:
        print(f"❌ Database integration failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Phone Directory API Tests...")
    print("=" * 70)
    
    success = True
    
    # Test 1: Routes Import
    if not test_routes_import():
        success = False
    
    # Test 2: Models Integration
    if not test_models_integration():
        success = False
    
    # Test 3: Database Integration
    if not test_database_integration():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ All Phone Directory API Tests Passed!")
    else:
        print("❌ Some tests failed!")
        
    print("🚀 Phone Directory API Ready for Integration!")
