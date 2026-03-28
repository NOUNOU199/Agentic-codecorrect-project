"""
Interactive demo showing the Time Machine's backup and restore capabilities.
Demonstrates the self-healing loop workflow.
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
    list_files,
    analyze_code_quality
)
import time

print("=" * 70)
print("THE TIME MACHINE - Backup & Restore Demo")
print("Self-Healing Loop Workflow")
print("=" * 70)

print("\n📖 SCENARIO: AI Agent is fixing code but might break things")
print("   We need a safety net to restore working states!")

# Step 1: Create initial working code
print("\n" + "=" * 70)
print("STEP 1: Initial Working Code")
print("=" * 70)

working_code = '''"""Calculator module - working version."""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    print(f"5 + 3 = {add(5, 3)}")
    print(f"5 - 3 = {subtract(5, 3)}")
    print(f"5 * 3 = {multiply(5, 3)}")
'''

write_file("calculator_demo.py", working_code)
print("\n✓ Created calculator_demo.py (working version)")

# Analyze initial quality
quality = analyze_code_quality("calculator_demo.py")
initial_score = quality.get('pylint_score', 0)
print(f"  Quality score: {initial_score}/10")

# Step 2: Create backup of working state
print("\n" + "=" * 70)
print("STEP 2: Backup Working State")
print("=" * 70)

backup_result = backup_sandbox("working_state")
print(f"\n💾 {backup_result['summary']}")
print(f"   Backup path: {backup_result['backup_path']}")

# Step 3: Agent attempts fix (but breaks it)
print("\n" + "=" * 70)
print("STEP 3: Agent Attempts 'Improvement' (but breaks code)")
print("=" * 70)

broken_code = '''"""Calculator module - broken version."""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b + 1  # BUG: Added 1 by mistake!


def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    result = a - b
    print(f"Debug: {result}")  # Forgot to remove debug print
    return result


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    # CRITICAL BUG: Wrong operation!
    return a + b  


if __name__ == "__main__":
    print(f"5 + 3 = {add(5, 3)}")  # Will print 9 instead of 8!
    print(f"5 - 3 = {subtract(5, 3)}")
    print(f"5 * 3 = {multiply(5, 3)}")  # Will print 8 instead of 15!
'''

write_file("calculator_demo.py", broken_code)
print("\n⚠️  Agent 'improved' the code (introduced 3 bugs!)")
print("   • add() returns wrong result")
print("   • subtract() has debug print")
print("   • multiply() uses wrong operation!")

# Analyze broken quality
quality_broken = analyze_code_quality("calculator_demo.py")
broken_score = quality_broken.get('pylint_score', 0)
print(f"  Quality score: {broken_score}/10")

# Step 4: Backup broken state (for comparison)
print("\n" + "=" * 70)
print("STEP 4: Backup Broken State (for analysis)")
print("=" * 70)

time.sleep(1)  # Ensure different timestamp
backup_result2 = backup_sandbox("broken_state")
print(f"\n💾 {backup_result2['summary']}")

# Step 5: List all backups
print("\n" + "=" * 70)
print("STEP 5: Available Backups")
print("=" * 70)

backups = list_backups()
print(f"\n📚 Found {backups['total_backups']} backup(s):")
for i, backup in enumerate(backups['backups'], 1):
    print(f"   {i}. {backup['name']}")
    print(f"      • Created: {backup['created']}")
    print(f"      • Files: {backup['files']}")
    print(f"      • Size: {backup['size_mb']:.3f} MB")

# Step 6: Realize code is broken, restore working state
print("\n" + "=" * 70)
print("STEP 6: RESTORE Working State (Time Travel!)")
print("=" * 70)

print("\n⏪ Agent realizes code is broken, initiating restore...")
print("   Restoring from backup: 'working_state'")

restore_result = restore_sandbox("working_state", confirm=False)
print(f"\n✓ {restore_result['summary']}")
print(f"  Files restored: {restore_result['files_restored']}")

# Verify restoration
restored_code = read_file("calculator_demo.py")
if "BUG" not in restored_code:
    print("\n✅ Verification: Code restored to working state!")
    quality_restored = analyze_code_quality("calculator_demo.py")
    restored_score = quality_restored.get('pylint_score', 0)
    print(f"   Quality score: {restored_score}/10 (back to {initial_score}/10)")
else:
    print("\n❌ Restoration failed - bugs still present")

# Step 7: Self-healing loop workflow
print("\n" + "=" * 70)
print("SELF-HEALING LOOP WORKFLOW")
print("=" * 70)

print("""
🔄 The complete self-healing loop with Time Machine:

1. 📸 BACKUP: Create checkpoint before attempting fixes
   └─> backup_sandbox("before_fix")

2. 🔧 FIX: Agent attempts to fix code
   └─> modify files, format, analyze

3. 🧪 TEST: Run tests and quality checks
   └─> run_pytest(), analyze_code_quality()

4. ✅ If tests pass:
   └─> Keep changes, create new backup
   └─> backup_sandbox("after_fix")

5. ❌ If tests fail:
   └─> Restore previous working state
   └─> restore_sandbox("before_fix", confirm=False)
   └─> Try different fix approach

6. 🔁 ITERATE: Repeat until quality threshold met
   └─> Each iteration has a restore point!
""")

# Step 8: Clean up old backups
print("\n" + "=" * 70)
print("STEP 8: Cleanup Old Backups")
print("=" * 70)

print("\n🧹 Removing 'broken_state' backup (we don't need it anymore)")
delete_result = delete_backup("broken_state")
print(f"   {delete_result['summary']}")

# Final backup list
final_backups = list_backups()
print(f"\n📚 Remaining backups: {final_backups['total_backups']}")
for backup in final_backups['backups']:
    print(f"   • {backup['name']}")

# Summary
print("\n" + "=" * 70)
print("KEY TAKEAWAYS")
print("=" * 70)

print("""
🎯 Why the Time Machine is Critical:

1. 💾 SAFETY: Never lose working code during experiments
2. 🔄 UNDO: Instantly revert broken changes
3. 📊 COMPARISON: Keep multiple states for A/B testing
4. 🛡️ PROTECTION: Safety check prevents accidental overwrites
5. 🤖 AUTOMATION: Perfect for AI agent self-healing loops

⚠️  Without this: Students will email you during finals asking
    "How do I undo the agent's changes?!" 😅

✅ With this: Agent can safely experiment, knowing it can always
    restore to the last working state!
""")

print("=" * 70)
