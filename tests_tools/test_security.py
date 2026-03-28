"""
Test script to verify the secure file system implementation.
This will test that:
1. Files in sandbox can be read
2. Files can be written to sandbox
3. Files outside sandbox cannot be accessed
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import read_file, write_file, list_files, SANDBOX_DIR

def test_secure_file_system():
    print("=" * 60)
    print("TESTING SECURE FILE SYSTEM (Increment 1)")
    print("=" * 60)
    print(f"\nSandbox directory: {SANDBOX_DIR}\n")
    
    # Test 1: List files in sandbox
    print("Test 1: List files in sandbox")
    try:
        files = list_files()
        print(f"✓ Files found: {files}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Read existing file
    print("\nTest 2: Read existing file (sandbox/test.txt)")
    try:
        content = read_file("test.txt")
        print(f"✓ Successfully read file:")
        print(f"  Content preview: {content[:50]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Write new file
    print("\nTest 3: Write new file (sandbox/new_file.txt)")
    try:
        write_file("new_file.txt", "Hello from the secure file system!")
        print("✓ Successfully wrote file")
        content = read_file("new_file.txt")
        print(f"  Verification read: {content}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 4: Create file in subdirectory
    print("\nTest 4: Write file in subdirectory (sandbox/subdir/test2.txt)")
    try:
        write_file("subdir/test2.txt", "File in subdirectory")
        print("✓ Successfully wrote file in subdirectory")
        files = list_files()
        print(f"  Updated file list: {files}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 5: Try to escape sandbox with ../
    print("\nTest 5: SECURITY - Try to read ../.env (should FAIL)")
    try:
        content = read_file("../.env")
        print(f"✗ SECURITY BREACH! Was able to read: {content[:50]}")
    except ValueError as e:
        print(f"✓ Security working! Blocked with: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")
    
    # Test 6: Try to escape with absolute path
    print("\nTest 6: SECURITY - Try to read absolute path outside sandbox (should FAIL)")
    try:
        if sys.platform == "win32":
            dangerous_path = "C:/Windows/System32/config/sam"
        else:
            dangerous_path = "/etc/passwd"
        content = read_file(dangerous_path)
        print(f"✗ SECURITY BREACH! Was able to read: {dangerous_path}")
    except ValueError as e:
        print(f"✓ Security working! Blocked with: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")
    
    # Test 7: Try complex escape attempt
    print("\nTest 7: SECURITY - Try complex escape ../../requirements.txt (should FAIL)")
    try:
        content = read_file("../../requirements.txt")
        print(f"✗ SECURITY BREACH! Was able to read requirements.txt")
    except ValueError as e:
        print(f"✓ Security working! Blocked with: {e}")
    except Exception as e:
        print(f"? Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_secure_file_system()
