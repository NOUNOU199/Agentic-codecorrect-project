"""
Interactive demo showing the Judge's capabilities.
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import run_script, run_pytest, test_and_analyze, write_file

print("=" * 70)
print("THE JUDGE - Execution & Testing Demo")
print("=" * 70)

# Create a buggy script
buggy_script = """
def fibonacci(n):
    '''Calculate fibonacci number (with a bug!)'''
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-1)  # Bug: should be n-2!

if __name__ == "__main__":
    for i in range(8):
        print(f"fib({i}) = {fibonacci(i)}")
"""

# Create tests for it
fib_tests = """
from sandbox.fibonacci_buggy import fibonacci

def test_base_cases():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1

def test_sequence():
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(4) == 3
    assert fibonacci(5) == 5
"""

write_file("fibonacci_buggy.py", buggy_script)
write_file("test_fibonacci.py", fib_tests)

print("\n📝 Created fibonacci_buggy.py with intentional bug")
print("📝 Created test_fibonacci.py with test cases")

# Run the script first
print("\n" + "=" * 70)
print("STEP 1: Running the script")
print("=" * 70)

result = run_script("fibonacci_buggy.py", timeout=3)
print(f"\n{'✓' if result['success'] else '✗'} Execution: {result['summary']}")
if result['stdout']:
    print(f"\nOutput:\n{result['stdout']}")

# Run the tests
print("\n" + "=" * 70)
print("STEP 2: Running pytest")
print("=" * 70)

test_result = run_pytest("test_fibonacci.py", verbose=True)
print(f"\n{'✓' if test_result['success'] else '✗'} Tests: {test_result['summary']}")
print(f"  Passed: {test_result['passed']}")
print(f"  Failed: {test_result['failed']}")

if test_result['failed'] > 0:
    print(f"\n⚠️  Test output (excerpt):")
    # Show relevant parts
    lines = test_result['stdout'].split('\n')
    for line in lines:
        if 'FAILED' in line or 'AssertionError' in line or 'assert' in line:
            print(f"  {line}")

# Comprehensive analysis
print("\n" + "=" * 70)
print("STEP 3: Comprehensive Analysis")
print("=" * 70)

analysis = test_and_analyze("fibonacci_buggy.py", "test_fibonacci.py")

print(f"\n🎯 VERDICT: {analysis['overall_status'].upper()}")
print(f"\n📊 Details:")
print(f"  • Script executed: {analysis['script_execution']['success']}")
print(f"  • Code quality: {analysis['code_quality']['pylint_score']}/10")
print(f"  • Tests passed: {analysis['tests']['passed']}/{analysis['tests']['passed'] + analysis['tests']['failed']}")

if analysis['issues_found']:
    print(f"\n⚠️  Issues Found:")
    for issue in analysis['issues_found']:
        print(f"  • {issue}")

if analysis['recommendations']:
    print(f"\n💡 Recommendations:")
    for rec in analysis['recommendations']:
        print(f"  • {rec}")

# Demonstrate timeout protection
print("\n" + "=" * 70)
print("BONUS: Timeout Protection Demo")
print("=" * 70)

slow_script = """
import time
print("Starting slow operation...")
time.sleep(10)  # This will timeout!
print("Done!")
"""

write_file("slow_script.py", slow_script)
print("\n📝 Created slow_script.py (sleeps for 10 seconds)")

result = run_script("slow_script.py", timeout=2)
print(f"\n{'✓' if result['timeout'] else '✗'} Timeout Protection: {result['summary']}")
print(f"  Timed out: {result['timeout']}")
print(f"  Execution time: {result['execution_time']:.2f}s")

print("\n" + "=" * 70)
