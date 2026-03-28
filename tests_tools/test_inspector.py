"""
Test script to verify the Inspector (Increment 2) implementation.
Tests syntax checking and pylint analysis.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import check_syntax, run_pylint, analyze_code_quality, write_file

def test_inspector():
    print("=" * 60)
    print("TESTING THE INSPECTOR (Increment 2)")
    print("=" * 60)
    
    # Test 1: Valid Python syntax
    print("\nTest 1: check_syntax() with VALID code")
    valid_code = """
def hello_world():
    print("Hello, World!")
    return 42

if __name__ == "__main__":
    hello_world()
"""
    is_valid, msg = check_syntax(valid_code)
    if is_valid:
        print(f"✓ Valid code recognized: {msg}")
    else:
        print(f"✗ Failed: {msg}")
    
    # Test 2: Invalid Python syntax - missing colon
    print("\nTest 2: check_syntax() with INVALID code (missing colon)")
    invalid_code1 = """
def hello_world()
    print("Hello, World!")
"""
    is_valid, msg = check_syntax(invalid_code1)
    if not is_valid:
        print(f"✓ Syntax error detected:")
        print(f"  {msg}")
    else:
        print(f"✗ Failed to detect syntax error")
    
    # Test 3: Invalid Python syntax - indentation error
    print("\nTest 3: check_syntax() with INVALID code (indentation)")
    invalid_code2 = """
def hello_world():
print("Hello, World!")
"""
    is_valid, msg = check_syntax(invalid_code2)
    if not is_valid:
        print(f"✓ Syntax error detected:")
        print(f"  {msg}")
    else:
        print(f"✗ Failed to detect syntax error")
    
    # Test 4: Create test files for pylint
    print("\nTest 4: Creating test files for pylint analysis")
    
    # Good quality code
    good_code = """
\"\"\"Module docstring.\"\"\"

def calculate_sum(num1: int, num2: int) -> int:
    \"\"\"Calculate sum of two numbers.\"\"\"
    return num1 + num2

def main():
    \"\"\"Main function.\"\"\"
    result = calculate_sum(5, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
"""
    
    # Poor quality code
    poor_code = """
import os
import sys

def f(x,y):
    z=x+y
    return z

a=5
b=10
c=f(a,b)
print(c)

unused_var = "This is never used"
"""
    
    try:
        write_file("good_code.py", good_code)
        write_file("poor_code.py", poor_code)
        print("✓ Test files created")
    except Exception as e:
        print(f"✗ Failed to create test files: {e}")
        return
    
    # Test 5: Run pylint on good code
    print("\nTest 5: run_pylint() on GOOD quality code")
    try:
        results = run_pylint("good_code.py")
        if results['success']:
            print(f"✓ Pylint analysis completed")
            print(f"  Score: {results['score']}/10")
            print(f"  Errors: {results['error_count']}")
            print(f"  Warnings: {results['warning_count']}")
            print(f"  Conventions: {results['convention_count']}")
            if results['errors']:
                print(f"  Major issues: {results['errors']}")
        else:
            print(f"✗ Pylint failed: {results['errors']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Run pylint on poor code
    print("\nTest 6: run_pylint() on POOR quality code")
    try:
        results = run_pylint("poor_code.py")
        if results['success']:
            print(f"✓ Pylint analysis completed")
            print(f"  Score: {results['score']}/10")
            print(f"  Errors: {results['error_count']}")
            print(f"  Warnings: {results['warning_count']}")
            print(f"  Conventions: {results['convention_count']}")
            if results['errors']:
                print(f"  Major issues found:")
                for error in results['errors'][:3]:  # Show first 3
                    print(f"    - {error}")
            if results['by_category']['convention']:
                print(f"  Convention issues (sample):")
                for issue in results['by_category']['convention'][:3]:
                    print(f"    - {issue}")
        else:
            print(f"✗ Pylint failed: {results['errors']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Comprehensive analysis
    print("\nTest 7: analyze_code_quality() - Comprehensive analysis")
    try:
        analysis = analyze_code_quality("poor_code.py")
        print(f"✓ Analysis completed")
        print(f"  Syntax valid: {analysis['syntax_valid']}")
        print(f"  Pylint score: {analysis['pylint_score']}/10")
        print(f"  Total issues: {analysis['total_issues']}")
        print(f"  Critical issues: {len(analysis['critical_issues'])}")
        print(f"  Recommendations:")
        for rec in analysis['recommendations']:
            print(f"    - {rec}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 8: Analysis with syntax errors
    print("\nTest 8: analyze_code_quality() with SYNTAX ERRORS")
    broken_code = """
def broken_function()  # Missing colon
    print("This won't work")
"""
    try:
        write_file("broken_code.py", broken_code)
        analysis = analyze_code_quality("broken_code.py")
        print(f"✓ Analysis handled syntax errors gracefully")
        print(f"  Syntax valid: {analysis['syntax_valid']}")
        print(f"  Syntax message: {analysis['syntax_message']}")
        print(f"  Recommendations: {analysis['recommendations']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("INSPECTOR TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_inspector()
