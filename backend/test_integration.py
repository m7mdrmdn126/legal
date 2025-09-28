#!/usr/bin/env python3
"""
Test Phone Directory Integration
================================

Test script to verify phone directory integration with FastAPI app.
"""

import sys
import os

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

def test_app_integration():
    """Test that the app can start with phone directory routes"""
    
    print("🧪 Testing Phone Directory Integration...")
    print("=" * 50)
    
    try:
        from main import app
        print("✅ FastAPI app imported successfully")
        
        # Check available routes
        routes = []
        phone_routes = []
        
        for route in app.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                route_info = f"{list(route.methods)} {route.path}"
                routes.append(route_info)
                
                if 'phone-directory' in route.path:
                    phone_routes.append(route_info)
        
        print(f"📋 Total routes: {len(routes)}")
        print(f"📋 Phone directory routes: {len(phone_routes)}")
        
        if phone_routes:
            print("📋 Phone Directory Endpoints:")
            for route in phone_routes:
                print(f"   {route}")
        else:
            print("❌ No phone directory routes found!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ App integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openapi_docs():
    """Test that phone directory appears in OpenAPI docs"""
    
    print("\n🧪 Testing OpenAPI Documentation...")
    print("=" * 50)
    
    try:
        from main import app
        
        # Get OpenAPI schema
        openapi_schema = app.openapi()
        
        # Check for phone directory paths
        phone_paths = []
        for path in openapi_schema.get('paths', {}):
            if 'phone-directory' in path:
                phone_paths.append(path)
        
        if phone_paths:
            print("✅ Phone Directory endpoints found in OpenAPI:")
            for path in phone_paths:
                methods = list(openapi_schema['paths'][path].keys())
                print(f"   {methods} {path}")
        else:
            print("❌ No phone directory endpoints in OpenAPI!")
            return False
            
        # Check tags
        tags = openapi_schema.get('tags', [])
        phone_tag = None
        for tag in tags:
            if tag.get('name') == 'Phone Directory':
                phone_tag = tag
                break
        
        if phone_tag:
            print(f"✅ Phone Directory tag found: {phone_tag}")
        else:
            print("⚠️  Phone Directory tag not found (but endpoints exist)")
            
        return True
        
    except Exception as e:
        print(f"❌ OpenAPI documentation test failed: {e}")
        return False

def test_database_connectivity():
    """Test database connectivity from app context"""
    
    print("\n🧪 Testing Database Connectivity...")
    print("=" * 50)
    
    try:
        from config.database import db_manager
        
        # Test phone directory table
        result = db_manager.execute_query("""
            SELECT COUNT(*) as count FROM phone_directory
        """)
        
        if result:
            count = result[0]['count']
            print(f"✅ Phone directory table accessible - {count} entries")
            return True
        else:
            print("❌ Could not access phone directory table")
            return False
            
    except Exception as e:
        print(f"❌ Database connectivity test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Phone Directory Integration Tests...")
    print("=" * 70)
    
    success = True
    
    # Test 1: App Integration
    if not test_app_integration():
        success = False
    
    # Test 2: OpenAPI Docs
    if not test_openapi_docs():
        success = False
    
    # Test 3: Database Connectivity
    if not test_database_connectivity():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✅ Phone Directory Integration Tests Passed!")
        print("🚀 Ready to start the server!")
    else:
        print("❌ Some integration tests failed!")
        
    print("\nTo test the API:")
    print("1. Start server: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("2. Visit: http://localhost:8000/docs")
    print("3. Look for 'Phone Directory' section")
