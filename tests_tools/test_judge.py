"""
Test script to verify the Judge (Increment 3) implementation.
Tests script execution, pytest running, and timeout protection.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import run_script, run_pytest, test_and_analyze, write_file

def test_judge():
    print("=" * 60)
    print("TESTING THE JUDGE (Increment 3)")
    print("=" * 60)
    
    # Test 1: Run a simple working script
    print("\nTest 1: run_script() with WORKING script")
    working_script = """
print("Hello from script!")
result = 2 + 2
print(f"Result: {result}")
"""
    try:
        write_file("working_script.py", working_script)
        result = run_script("working_script.py")
        if result['success']:
            print(f"✓ Script executed successfully")
            print(f"  Exit code: {result['exit_code']}")
            print(f"  Execution time: {result['execution_time']:.3f}s")
            print(f"  Output: {result['stdout'].strip()}")
        else:
            print(f"✗ Script failed: {result['stderr']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Run a script with errors
    print("\nTest 2: run_script() with FAILING script")
    failing_script = """
print("Starting...")
x = 1 / 0  # ZeroDivisionError
print("This won't print")
"""
    try:
        write_file("failing_script.py", failing_script)
        result = run_script("failing_script.py")
        if not result['success']:
            print(f"✓ Correctly detected script failure")
            print(f"  Exit code: {result['exit_code']}")
            print(f"  Error preview: {result['stderr'][:100]}...")
        else:
            print(f"✗ Should have failed but didn't")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: CRITICAL - Infinite loop detection
    print("\nTest 3: run_script() with INFINITE LOOP (timeout test)")
    infinite_loop_script = """
print("Starting infinite loop...")
while True:
    pass
print("This will never print")
"""
    try:
        write_file("infinite_loop.py", infinite_loop_script)
        result = run_script("infinite_loop.py", timeout=2)
        if result['timeout']:
            print(f"✓ Correctly detected and stopped infinite loop!")
            print(f"  Timeout: {result['timeout']}")
            print(f"  Execution time: {result['execution_time']:.3f}s")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Should have timed out but didn't")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Script with command-line arguments
    print("\nTest 4: run_script() with ARGUMENTS")
    args_script = """
import sys
print(f"Script name: {sys.argv[0]}")
if len(sys.argv) > 1:
    print(f"Arguments: {sys.argv[1:]}")
    print(f"Sum: {sum(int(x) for x in sys.argv[1:])}")
"""
    try:
        write_file("args_script.py", args_script)
        result = run_script("args_script.py", args=["5", "10", "15"])
        if result['success']:
            print(f"✓ Script with arguments executed")
            print(f"  Output: {result['stdout'].strip()}")
        else:
            print(f"✗ Failed: {result['stderr']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Create and run pytest tests
    print("\nTest 5: run_pytest() with PASSING tests")
    passing_tests = """
def test_addition():
    assert 2 + 2 == 4

def test_subtraction():
    assert 5 - 3 == 2

def test_multiplication():
    assert 3 * 4 == 12
"""
    try:
        write_file("test_passing.py", passing_tests)
        result = run_pytest("test_passing.py", verbose=True)
        if result['success']:
            print(f"✓ All tests passed")
            print(f"  Passed: {result['passed']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Tests should have passed: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: pytest with failing tests
    print("\nTest 6: run_pytest() with FAILING tests")
    failing_tests = """
def test_will_pass():
    assert 1 + 1 == 2

def test_will_fail():
    assert 2 + 2 == 5  # This is wrong!

def test_another_fail():
    assert "hello".upper() == "GOODBYE"
"""
    try:
        write_file("test_failing.py", failing_tests)
        result = run_pytest("test_failing.py", verbose=False)
        if not result['success']:
            print(f"✓ Correctly detected failing tests")
            print(f"  Passed: {result['passed']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Should have detected failures")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Comprehensive test_and_analyze
    print("\nTest 7: test_and_analyze() - COMPREHENSIVE analysis")
    complete_script = """
\"\"\"A simple calculator module.\"\"\"

def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(a: int, b: int) -> int:
    \"\"\"Multiply two numbers.\"\"\"
    return a * b

if __name__ == "__main__":
    print(f"5 + 3 = {add(5, 3)}")
    print(f"5 * 3 = {multiply(5, 3)}")
"""
    
    complete_tests = """
from sandbox.calculator import add, multiply

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
"""
    
    try:
        write_file("calculator.py", complete_script)
        write_file("test_calculator.py", complete_tests)
        
        result = test_and_analyze("calculator.py", "test_calculator.py")
        
        print(f"✓ Comprehensive analysis completed")
        print(f"  Overall status: {result['overall_status']}")
        print(f"  Script success: {result['script_execution']['success']}")
        print(f"  Quality score: {result['code_quality']['pylint_score']}/10")
        print(f"  Tests passed: {result['tests']['passed']}")
        print(f"  Tests failed: {result['tests']['failed']}")
        print(f"  Issues found: {len(result['issues_found'])}")
        if result['recommendations']:
            print(f"  Recommendations:")
            for rec in result['recommendations'][:2]:
                print(f"    - {rec}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 8: test_and_analyze with infinite loop
    print("\nTest 8: test_and_analyze() detects INFINITE LOOP")
    try:
        result = test_and_analyze("infinite_loop.py")
        print(f"✓ Analysis completed")
        print(f"  Overall status: {result['overall_status']}")
        print(f"  Timeout detected: {result['script_execution']['timeout']}")
        if 'infinite loop' in ' '.join(result['issues_found']).lower():
            print(f"  ✓ Infinite loop issue identified")
        print(f"  Issues: {result['issues_found'][:2]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("JUDGE TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_judge()
