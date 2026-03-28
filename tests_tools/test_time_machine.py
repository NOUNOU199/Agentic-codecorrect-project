"""
Test script to verify the Time Machine (Increment 5) implementation.
Tests backup, restore, and backup management functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import (
    backup_sandbox,
    restore_sandbox,
    list_backups,
    delete_backup,
    write_file,
    read_file,
    list_files
)
import time

def test_time_machine():
    print("=" * 60)
    print("TESTING THE TIME MACHINE (Increment 5)")
    print("=" * 60)
    
    # Test 1: Create initial backup
    print("\nTest 1: backup_sandbox() - Create FIRST backup")
    try:
        result = backup_sandbox("test_backup_1")
        if result['success']:
            print(f"✓ Backup created successfully")
            print(f"  Path: {result['backup_path']}")
            print(f"  Files: {result['files_backed_up']}")
            print(f"  Size: {result['size_bytes'] / 1024:.2f} KB")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Failed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: List backups
    print("\nTest 2: list_backups() - View available backups")
    try:
        result = list_backups()
        if result['success']:
            print(f"✓ Found {result['total_backups']} backup(s)")
            print(f"  Total size: {result['total_size_bytes'] / (1024 * 1024):.2f} MB")
            for backup in result['backups']:
                print(f"  • {backup['name']}: {backup['files']} files, created {backup['created']}")
        else:
            print(f"✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Modify sandbox
    print("\nTest 3: Modify sandbox (create new files)")
    try:
        write_file("new_file_1.txt", "This file was created after backup")
        write_file("new_file_2.py", "print('Hello from new file')")
        print(f"✓ Created 2 new files in sandbox")
        
        current_files = len(list_files())
        print(f"  Current files in sandbox: {current_files}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Create second backup (with auto-timestamp)
    print("\nTest 4: backup_sandbox() - AUTO-TIMESTAMP backup")
    try:
        time.sleep(1)  # Ensure different timestamp
        result = backup_sandbox()  # No name = auto timestamp
        if result['success']:
            print(f"✓ Auto-timestamp backup created")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Failed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: List backups again
    print("\nTest 5: list_backups() - After creating multiple backups")
    try:
        result = list_backups()
        if result['success']:
            print(f"✓ Found {result['total_backups']} backup(s)")
            for i, backup in enumerate(result['backups'], 1):
                print(f"  {i}. {backup['name']} ({backup['files']} files, {backup['size_mb']:.2f} MB)")
        else:
            print(f"✗ Failed")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Try restore with safety check
    print("\nTest 6: restore_sandbox() - WITH safety check (should fail)")
    try:
        result = restore_sandbox("test_backup_1", confirm=True)
        if not result['success']:
            print(f"✓ Safety check working: {result['summary']}")
        else:
            print(f"✗ Should have been blocked by safety check!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Actual restore
    print("\nTest 7: restore_sandbox() - ACTUAL restore (confirm=False)")
    try:
        files_before = len(list_files())
        print(f"  Files before restore: {files_before}")
        
        result = restore_sandbox("test_backup_1", confirm=False)
        if result['success']:
            print(f"✓ Restore successful")
            print(f"  Backup used: {result['backup_used']}")
            print(f"  Files restored: {result['files_restored']}")
            print(f"  Summary: {result['summary']}")
            
            files_after = len(list_files())
            print(f"  Files after restore: {files_after}")
            
            # Verify new files are gone
            try:
                read_file("new_file_1.txt")
                print(f"  ✗ New file still exists (restore didn't work properly)")
            except FileNotFoundError:
                print(f"  ✓ Verified: new files removed by restore")
        else:
            print(f"✗ Failed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 8: Restore most recent backup (no name specified)
    print("\nTest 8: restore_sandbox() - MOST RECENT backup (auto-select)")
    try:
        # Create another file
        write_file("temp_file.txt", "Temporary")
        print(f"  Created temp file")
        
        result = restore_sandbox(confirm=False)  # No name = most recent
        if result['success']:
            print(f"✓ Restored most recent backup")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Failed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 9: Delete a backup
    print("\nTest 9: delete_backup() - Remove old backup")
    try:
        result = delete_backup("test_backup_1")
        if result['success']:
            print(f"✓ Backup deleted: {result['summary']}")
            
            # Verify it's gone
            backups = list_backups()
            remaining = [b['name'] for b in backups['backups']]
            print(f"  Remaining backups: {remaining}")
        else:
            print(f"✗ Failed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 10: Edge case - restore non-existent backup
    print("\nTest 10: restore_sandbox() - NON-EXISTENT backup")
    try:
        result = restore_sandbox("fake_backup_xyz", confirm=False)
        if not result['success']:
            print(f"✓ Correctly handled missing backup: {result['summary']}")
        else:
            print(f"✗ Should have failed with non-existent backup")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 11: Edge case - delete non-existent backup
    print("\nTest 11: delete_backup() - NON-EXISTENT backup")
    try:
        result = delete_backup("fake_backup_xyz")
        if not result['success']:
            print(f"✓ Correctly handled missing backup: {result['summary']}")
        else:
            print(f"✗ Should have failed")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 12: Comprehensive workflow
    print("\nTest 12: COMPLETE workflow simulation")
    try:
        print("  Step 1: Create initial state")
        write_file("workflow_test.py", "# Version 1")
        
        print("  Step 2: Backup")
        backup1 = backup_sandbox("workflow_v1")
        print(f"    Backup 1: {backup1['summary']}")
        
        print("  Step 3: Modify (simulate agent changes)")
        write_file("workflow_test.py", "# Version 2 - with bugs!")
        write_file("broken.py", "syntax error here (")
        
        print("  Step 4: Backup again")
        backup2 = backup_sandbox("workflow_v2")
        print(f"    Backup 2: {backup2['summary']}")
        
        print("  Step 5: Realize version 2 is broken, restore version 1")
        restore = restore_sandbox("workflow_v1", confirm=False)
        print(f"    Restore: {restore['summary']}")
        
        print("  Step 6: Verify restoration")
        content = read_file("workflow_test.py")
        if "Version 1" in content:
            print(f"    ✓ Successfully restored to version 1!")
        else:
            print(f"    ✗ Restore didn't work properly")
        
        try:
            read_file("broken.py")
            print(f"    ✗ Broken file still exists")
        except FileNotFoundError:
            print(f"    ✓ Broken file was removed")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TIME MACHINE TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_time_machine()
