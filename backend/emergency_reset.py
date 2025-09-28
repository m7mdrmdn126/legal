"""
EMERGENCY PASSWORD RESET SCRIPT
Run this on Windows to fix bcrypt login issues
"""
import sqlite3
import sys
import os
import platform
sys.path.append('.')
from utils.auth import AuthUtils

def emergency_reset():
    """Reset admin password to fix bcrypt issues"""
    print(f"🔧 Emergency Password Reset - {platform.system()}")
    print("=" * 50)
    
    # Database path
    db_path = os.path.join("database", "legal_cases.db")
    
    if not os.path.exists(db_path):
        print("❌ Database not found! Please ensure you're in the backend directory.")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table not found!")
            conn.close()
            return False
        
        # Reset admin password
        new_password = "admin123"
        print(f"🔑 Resetting admin password to: {new_password}")
        
        # Hash password using our fixed auth system
        try:
            hashed_password = AuthUtils.hash_password(new_password)
            print("✅ Password hashed successfully")
        except Exception as e:
            print(f"❌ Error hashing password: {e}")
            conn.close()
            return False
        
        # Update admin user
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE username = 'admin' OR is_admin = 1
        """, (hashed_password,))
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            print(f"✅ Admin password reset successfully! ({rows_affected} user(s) updated)")
            print("🔐 New credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            print("")
            print("⚠️  IMPORTANT: Change this password after login!")
        else:
            print("❌ No admin user found to update")
            conn.close()
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Starting emergency password reset...")
    success = emergency_reset()
    
    if success:
        print("\n🎉 Password reset completed successfully!")
        print("You can now login with admin/admin123")
    else:
        print("\n💥 Password reset failed!")
        print("Please check the error messages above.")
    
    input("\nPress Enter to exit...")
