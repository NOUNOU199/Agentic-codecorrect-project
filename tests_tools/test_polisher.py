"""
Test script to verify the Polisher (Increment 4) implementation.
Tests Black formatting and project structure visualization.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import apply_black_formatting, get_project_structure, format_and_analyze, write_file

def test_polisher():
    print("=" * 60)
    print("TESTING THE POLISHER (Increment 4)")
    print("=" * 60)
    
    # Test 1: Format already well-formatted code
    print("\nTest 1: apply_black_formatting() on WELL-FORMATTED code")
    well_formatted = '''"""Module docstring."""


def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b


if __name__ == "__main__":
    result = calculate_sum(5, 3)
    print(f"Result: {result}")
'''
    
    try:
        write_file("well_formatted.py", well_formatted)
        result = apply_black_formatting("well_formatted.py")
        if result['success']:
            print(f"✓ Black executed successfully")
            print(f"  Reformatted: {result['reformatted']}")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Failed: {result['stderr']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Format poorly formatted code
    print("\nTest 2: apply_black_formatting() on POORLY FORMATTED code")
    poorly_formatted = '''def bad_function(x,y,z):
    result=x+y+z
    return result

a=5;b=10;c=15
print(bad_function(a,b,c))

def another_bad(  x,  y  ):
        return x+y
'''
    
    try:
        write_file("poorly_formatted.py", poorly_formatted)
        result = apply_black_formatting("poorly_formatted.py")
        if result['success']:
            print(f"✓ Black executed successfully")
            print(f"  Reformatted: {result['reformatted']}")
            print(f"  Summary: {result['summary']}")
            if result['reformatted']:
                print(f"  ✓ Code was automatically reformatted!")
        else:
            print(f"✗ Failed: {result['stderr']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Check-only mode
    print("\nTest 3: apply_black_formatting() in CHECK-ONLY mode")
    messy_code = '''def messy(x,y):
    return x+y
'''
    
    try:
        write_file("messy.py", messy_code)
        result = apply_black_formatting("messy.py", check_only=True)
        print(f"✓ Check-only mode executed")
        print(f"  Would be reformatted: {result['reformatted']}")
        print(f"  Summary: {result['summary']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Custom line length
    print("\nTest 4: apply_black_formatting() with CUSTOM line length")
    long_line_code = '''def function_with_long_line():
    very_long_variable_name = "This is a very long string that exceeds the default line length"
    return very_long_variable_name
'''
    
    try:
        write_file("long_lines.py", long_line_code)
        result = apply_black_formatting("long_lines.py", line_length=50)
        if result['success']:
            print(f"✓ Custom line length applied")
            print(f"  Reformatted: {result['reformatted']}")
            print(f"  Summary: {result['summary']}")
        else:
            print(f"✗ Failed: {result['stderr']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Get project structure
    print("\nTest 5: get_project_structure() - Directory tree")
    try:
        tree = get_project_structure()
        print(f"✓ Project structure retrieved")
        print(f"\n{tree}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Get project structure with limited depth
    print("\nTest 6: get_project_structure() with MAX DEPTH=2")
    try:
        tree = get_project_structure(max_depth=2)
        print(f"✓ Limited depth tree retrieved")
        lines = tree.split('\n')
        print(f"  Tree has {len(lines)} lines")
        print(f"  Sample:\n{chr(10).join(lines[:10])}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Get structure of subdirectory
    print("\nTest 7: get_project_structure() of SUBDIRECTORY")
    try:
        # Create a subdirectory structure
        write_file("project/module1.py", "# Module 1")
        write_file("project/module2.py", "# Module 2")
        write_file("project/tests/test_module.py", "# Tests")
        
        tree = get_project_structure("project")
        print(f"✓ Subdirectory structure retrieved")
        print(f"\n{tree}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 8: Comprehensive format_and_analyze
    print("\nTest 8: format_and_analyze() - COMPLETE workflow")
    ugly_code = '''import os
import sys

def bad_func(x,y):
    z=x+y
    return z

a=5
b=10
result=bad_func(a,b)
print(result)
'''
    
    try:
        write_file("ugly_code.py", ugly_code)
        result = format_and_analyze("ugly_code.py")
        
        print(f"✓ Complete analysis finished")
        print(f"  Formatted: {result['formatting']['reformatted']}")
        
        if result['analysis_before'] and result['analysis_after']:
            before_score = result['analysis_before']['pylint_score']
            after_score = result['analysis_after']['pylint_score']
            print(f"  Score before: {before_score}/10")
            print(f"  Score after: {after_score}/10")
            
            if result['improvement'] is not None:
                print(f"  Improvement: {result['improvement']:+.2f} points")
        
        print(f"  Recommendations:")
        for rec in result['recommendations']:
            print(f"    - {rec}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 9: format_and_analyze on already good code
    print("\nTest 9: format_and_analyze() on HIGH-QUALITY code")
    good_code = '''"""High quality module."""


def calculate(value_a: int, value_b: int) -> int:
    """Calculate sum of two values."""
    return value_a + value_b


def main() -> None:
    """Main function."""
    result = calculate(10, 20)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
'''
    
    try:
        write_file("good_quality.py", good_code)
        result = format_and_analyze("good_quality.py")
        
        print(f"✓ Analysis completed")
        if result['analysis_after']:
            score = result['analysis_after']['pylint_score']
            print(f"  Quality score: {score}/10")
        
        print(f"  Recommendations:")
        for rec in result['recommendations']:
            print(f"    - {rec}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("POLISHER TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_polisher()
