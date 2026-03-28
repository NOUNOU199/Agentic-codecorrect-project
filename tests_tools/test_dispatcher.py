"""
Test script to verify the Dispatcher (Increment 6) implementation.
Tests unified tool execution and error handling.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import (
    execute_tool,
    list_available_tools,
    get_tool_info,
    get_tools_by_category,
    validate_tool_call,
    write_file
)
import json

def test_dispatcher():
    print("=" * 60)
    print("TESTING THE DISPATCHER (Increment 6)")
    print("=" * 60)
    
    # Test 1: List available tools
    print("\nTest 1: list_available_tools() - View all tools")
    try:
        tools = list_available_tools()
        print(f"✓ Found {len(tools)} tools")
        print(f"  Sample tools: {tools[:5]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: List tools by category
    print("\nTest 2: get_tools_by_category() - Organize by category")
    try:
        categories = get_tools_by_category()
        print(f"✓ Found {len(categories)} categories")
        for category, tools in categories.items():
            print(f"  • {category}: {len(tools)} tools")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get tool info
    print("\nTest 3: get_tool_info() - Detailed tool information")
    try:
        info = get_tool_info('read_file')
        if info['exists']:
            print(f"✓ Tool info retrieved")
            print(f"  Name: {info['name']}")
            print(f"  Category: {info['category']}")
            print(f"  Description: {info['description']}")
            print(f"  Required args: {info['required_args']}")
            print(f"  Optional args: {info['optional_args']}")
        else:
            print(f"✗ Tool not found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Execute a successful tool call
    print("\nTest 4: execute_tool() - SUCCESSFUL call")
    try:
        # Create a test file first
        write_file("dispatcher_test.txt", "Hello from dispatcher!")
        
        result = execute_tool('read_file', path='dispatcher_test.txt')
        if result['status'] == 'success':
            print(f"✓ Tool executed successfully")
            print(f"  Tool: {result['tool']}")
            print(f"  Output preview: {result['output'][:30]}...")
        else:
            print(f"✗ Unexpected error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Execute with hallucinated tool name
    print("\nTest 5: execute_tool() - HALLUCINATED tool name")
    try:
        result = execute_tool('make_coffee', cups=2)
        if result['status'] == 'error':
            print(f"✓ Correctly handled non-existent tool")
            print(f"  Error type: {result['error_type']}")
            print(f"  Error message: {result['error'][:80]}...")
        else:
            print(f"✗ Should have returned error status")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Execute with missing required arguments
    print("\nTest 6: execute_tool() - MISSING required arguments")
    try:
        result = execute_tool('write_file', path='test.txt')  # Missing 'content'
        if result['status'] == 'error':
            print(f"✓ Correctly handled missing arguments")
            print(f"  Error type: {result['error_type']}")
            print(f"  Error preview: {result['error'][:60]}...")
        else:
            print(f"✗ Should have returned error status")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Execute with invalid argument types
    print("\nTest 7: execute_tool() - INVALID argument types")
    try:
        result = execute_tool('run_script', script_path='test.py', timeout='not_a_number')
        if result['status'] == 'error':
            print(f"✓ Handled invalid argument type")
            print(f"  Error type: {result['error_type']}")
        else:
            # Some tools might convert strings to numbers, so this might succeed
            print(f"⚠ Tool handled conversion automatically")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 8: Execute tool that raises FileNotFoundError
    print("\nTest 8: execute_tool() - FileNotFoundError handling")
    try:
        result = execute_tool('read_file', path='nonexistent_file.txt')
        if result['status'] == 'error' and result['error_type'] == 'FileNotFoundError':
            print(f"✓ Correctly caught FileNotFoundError")
            print(f"  Error: {result['error']}")
        else:
            print(f"✗ Expected FileNotFoundError")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 9: Execute tool that raises ValueError (sandbox escape)
    print("\nTest 9: execute_tool() - ValueError handling (sandbox escape)")
    try:
        result = execute_tool('read_file', path='../../etc/passwd')
        if result['status'] == 'error' and result['error_type'] == 'ValueError':
            print(f"✓ Correctly caught ValueError")
            print(f"  Error preview: {result['error'][:60]}...")
        else:
            print(f"✗ Expected ValueError for sandbox escape")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 10: Validate tool call before execution
    print("\nTest 10: validate_tool_call() - VALID call")
    try:
        validation = validate_tool_call('write_file', path='test.txt', content='data')
        if validation['valid']:
            print(f"✓ Validation passed")
            print(f"  Tool: {validation['tool']}")
            print(f"  Arguments: {list(validation['arguments'].keys())}")
        else:
            print(f"✗ Should be valid: {validation.get('error')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 11: Validate tool call with missing args
    print("\nTest 11: validate_tool_call() - INVALID (missing args)")
    try:
        validation = validate_tool_call('write_file', path='test.txt')  # Missing content
        if not validation['valid']:
            print(f"✓ Validation correctly failed")
            print(f"  Error: {validation['error']}")
        else:
            print(f"✗ Should have failed validation")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 12: Validate non-existent tool
    print("\nTest 12: validate_tool_call() - NON-EXISTENT tool")
    try:
        validation = validate_tool_call('magic_tool', param='value')
        if not validation['valid']:
            print(f"✓ Validation correctly failed")
            print(f"  Error: {validation['error']}")
            print(f"  Suggestions available: {len(validation.get('suggestions', []))} tools")
        else:
            print(f"✗ Should have failed validation")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 13: Chain multiple tool calls
    print("\nTest 13: Chain MULTIPLE tool calls")
    try:
        print("  Step 1: Create file")
        r1 = execute_tool('write_file', path='chain_test.py', content='print("Hello")')
        
        print("  Step 2: Format file")
        r2 = execute_tool('apply_black_formatting', path='chain_test.py')
        
        print("  Step 3: Analyze quality")
        r3 = execute_tool('analyze_code_quality', path='chain_test.py')
        
        if all(r['status'] == 'success' for r in [r1, r2, r3]):
            print(f"✓ All 3 tools executed successfully")
            print(f"  Quality score: {r3['output']['pylint_score']}/10")
        else:
            failures = [r['tool'] for r in [r1, r2, r3] if r['status'] != 'success']
            print(f"✗ Some tools failed: {failures}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 14: Get info for non-existent tool
    print("\nTest 14: get_tool_info() - NON-EXISTENT tool")
    try:
        info = get_tool_info('fake_tool')
        if not info['exists']:
            print(f"✓ Correctly reported tool doesn't exist")
            print(f"  Error: {info['error']}")
        else:
            print(f"✗ Should have reported non-existence")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 15: List tools by specific category
    print("\nTest 15: list_available_tools() - FILTER by category")
    try:
        filesystem_tools = list_available_tools(category='filesystem')
        analysis_tools = list_available_tools(category='analysis')
        
        print(f"✓ Category filtering works")
        print(f"  Filesystem: {filesystem_tools}")
        print(f"  Analysis: {analysis_tools}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 16: Comprehensive workflow using only execute_tool
    print("\nTest 16: COMPLETE workflow using ONLY execute_tool()")
    try:
        workflow_steps = [
            ('backup_sandbox', {'backup_name': 'workflow_test'}),
            ('write_file', {'path': 'workflow.py', 'content': 'def test(): pass'}),
            ('check_syntax', {'code_string': 'def test(): pass'}),
            ('apply_black_formatting', {'path': 'workflow.py'}),
            ('list_files', {}),
        ]
        
        results = []
        for tool_name, kwargs in workflow_steps:
            result = execute_tool(tool_name, **kwargs)
            results.append((tool_name, result['status']))
        
        successes = sum(1 for _, status in results if status == 'success')
        print(f"✓ Workflow completed: {successes}/{len(results)} steps succeeded")
        for tool, status in results:
            symbol = '✓' if status == 'success' else '✗'
            print(f"  {symbol} {tool}: {status}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("DISPATCHER TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_dispatcher()
