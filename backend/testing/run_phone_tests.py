#!/usr/bin/env python3
"""
Phone Directory Test Runner
===========================

Run unit tests for the phone directory feature.
"""

import sys
import os
import subprocess

def main():
    """Run phone directory tests"""
    
    # Change to testing directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    print("🧪 Running Phone Directory Tests...")
    print("=" * 50)
    
    # Run tests with verbose output
    cmd = [
        sys.executable, "-m", "pytest", 
        "test_phone_directory.py", 
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ All Phone Directory Tests Passed!")
        else:
            print("\n" + "=" * 50)
            print("❌ Some Tests Failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
