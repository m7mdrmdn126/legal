#!/usr/bin/env python3
"""
Quick Phone Directory Test
=========================

Simple test to verify phone directory functionality works.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the backend directory to Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from models.phone_directory import (
    PhoneDirectoryCreate, 
    PhoneDirectoryUpdate,
    PhoneDirectoryResponse,
    PhoneDirectorySearchRequest
)

def test_models():
    """Test phone directory models"""
    
    print("🧪 Testing Phone Directory Models...")
    
    try:
        # Test create model
        create_model = PhoneDirectoryCreate(
            الاسم="أحمد محمد",
            الرقم="01234567890",
            الجهه="وزارة العدل"
        )
        print(f"✅ Create model: {create_model}")
        
        # Test update model
        update_model = PhoneDirectoryUpdate(الاسم="أحمد محمد المحدث")
        print(f"✅ Update model: {update_model}")
        
        # Test search model
        search_model = PhoneDirectorySearchRequest(
            search_term="محمد",
            page=1,
            size=10
        )
        print(f"✅ Search model: {search_model}")
        
        # Test validation
        empty_model = PhoneDirectoryCreate()
        print(f"✅ Empty model: {empty_model}")
        
        # Test whitespace handling
        whitespace_model = PhoneDirectoryCreate(
            الاسم="  محمد علي  ",
            الرقم="  01111111111  "
        )
        print(f"✅ Whitespace model: {whitespace_model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    
    print("\n🗄️ Testing Database Operations...")
    
    try:
        # Connect to database
        db_path = os.path.join(os.path.dirname(__file__), "../database/legal_cases.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='phone_directory'
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists:
            print("❌ Phone directory table does not exist!")
            return False
        
        print("✅ Phone directory table exists")
        
        # Test table structure
        cursor.execute("PRAGMA table_info(phone_directory)")
        columns = cursor.fetchall()
        
        expected_columns = ['id', 'الاسم', 'الرقم', 'الجهه', 'created_at', 'updated_at', 'created_by', 'updated_by']
        actual_columns = [col[1] for col in columns]
        
        for expected_col in expected_columns:
            if expected_col not in actual_columns:
                print(f"❌ Missing column: {expected_col}")
                return False
        
        print(f"✅ All columns present: {actual_columns}")
        
        # Test insert
        cursor.execute("""
            INSERT INTO phone_directory (الاسم, الرقم, الجهه, created_by)
            VALUES (?, ?, ?, ?)
        """, ("اختبار محمد", "01234567890", "وزارة الاختبار", 1))
        
        entry_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Insert successful, ID: {entry_id}")
        
        # Test select
        cursor.execute("""
            SELECT id, الاسم, الرقم, الجهه FROM phone_directory WHERE id = ?
        """, (entry_id,))
        
        row = cursor.fetchone()
        if row:
            print(f"✅ Select successful: {row}")
        else:
            print("❌ Select failed")
            return False
        
        # Test update
        cursor.execute("""
            UPDATE phone_directory 
            SET الاسم = ?, updated_at = CURRENT_TIMESTAMP, updated_by = ?
            WHERE id = ?
        """, ("اختبار محمد المحدث", 1, entry_id))
        
        conn.commit()
        print("✅ Update successful")
        
        # Test search
        cursor.execute("""
            SELECT COUNT(*) FROM phone_directory 
            WHERE الاسم LIKE ? OR الرقم LIKE ? OR الجهه LIKE ?
        """, ("%محمد%", "%محمد%", "%محمد%"))
        
        count = cursor.fetchone()[0]
        print(f"✅ Search successful, found {count} entries")
        
        # Cleanup
        cursor.execute("DELETE FROM phone_directory WHERE id = ?", (entry_id,))
        conn.commit()
        print("✅ Cleanup successful")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

def main():
    """Run all tests"""
    
    print("🚀 Quick Phone Directory Test")
    print("=" * 50)
    
    # Test models
    model_success = test_models()
    
    # Test database
    db_success = test_database()
    
    print("\n" + "=" * 50)
    
    if model_success and db_success:
        print("✅ All Quick Tests Passed!")
        print("🎉 Phone Directory feature is working correctly!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
