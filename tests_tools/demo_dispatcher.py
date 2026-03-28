"""
Interactive demo showing the Dispatcher's unified tool execution.
Demonstrates how orchestrators can call tools without if/else statements.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import (
    execute_tool,
    list_available_tools,
    get_tool_info,
    get_tools_by_category,
    validate_tool_call
)
import json

print("=" * 70)
print("THE DISPATCHER - Unified Tool Execution Demo")
print("One Function to Rule Them All")
print("=" * 70)

print("\n📖 PROBLEM: Orchestrator needs to call tools dynamically")
print("   Without Dispatcher: 20+ if/else statements")
print("   With Dispatcher: ONE function call!")

# Show available tools
print("\n" + "=" * 70)
print("AVAILABLE TOOLS")
print("=" * 70)

categories = get_tools_by_category()
print(f"\n📚 {sum(len(tools) for tools in categories.values())} tools across {len(categories)} categories:\n")

for category, tools in sorted(categories.items()):
    print(f"  {category.upper()}:")
    for tool in tools:
        info = get_tool_info(tool)
        print(f"    • {tool}: {info['description']}")

# Demonstrate the old way vs new way
print("\n" + "=" * 70)
print("OLD WAY: Manual if/else for each tool")
print("=" * 70)

print("""
❌ NIGHTMARE CODE (what orchestrators would write without Dispatcher):

def call_tool(tool_name, **kwargs):
    if tool_name == 'read_file':
        return read_file(**kwargs)
    elif tool_name == 'write_file':
        return write_file(**kwargs)
    elif tool_name == 'run_pylint':
        return run_pylint(**kwargs)
    elif tool_name == 'run_script':
        return run_script(**kwargs)
    # ... 13 more elif statements ...
    else:
        raise ValueError("Unknown tool!")
        # 💥 CRASHES if LLM hallucinates a tool name!
""")

print("\n" + "=" * 70)
print("NEW WAY: Unified Dispatcher")
print("=" * 70)

print("""
✅ CLEAN CODE (with Dispatcher):

def call_tool(tool_name, **kwargs):
    return execute_tool(tool_name, **kwargs)
    # That's it! One line!
    # ✓ Never crashes
    # ✓ Auto error handling
    # ✓ Standardized output
""")

# Demonstration 1: Simulated LLM output
print("\n" + "=" * 70)
print("DEMO 1: Handling LLM Tool Calls")
print("=" * 70)

# Simulate what an LLM might output
llm_tool_calls = [
    {'tool': 'write_file', 'args': {'path': 'hello.py', 'content': 'print("Hello!")'}},
    {'tool': 'check_syntax', 'args': {'code_string': 'print("Hello!")'}},
    {'tool': 'make_coffee', 'args': {'cups': 2}},  # Hallucinated!
    {'tool': 'apply_black_formatting', 'args': {'path': 'hello.py'}},
    {'tool': 'analyze_code_quality', 'args': {'path': 'hello.py'}},
]

print("\n🤖 LLM wants to call 5 tools (one is hallucinated):\n")

for i, call in enumerate(llm_tool_calls, 1):
    print(f"  {i}. {call['tool']}({', '.join(f'{k}={repr(v)}' for k, v in call['args'].items())})")

print("\n⚙️  Executing all tool calls...")

results = []
for call in llm_tool_calls:
    result = execute_tool(call['tool'], **call['args'])
    results.append(result)
    
    status_icon = '✅' if result['status'] == 'success' else '❌'
    print(f"\n  {status_icon} {call['tool']}: {result['status']}")
    
    if result['status'] == 'error':
        print(f"     Error: {result['error_type']}")
        print(f"     Message: {result['error'][:60]}...")
    else:
        if 'score' in str(result['output']):
            output_str = f"Score: {result['output'].get('pylint_score', 'N/A')}"
        elif isinstance(result['output'], (str, int, float)):
            output_str = str(result['output'])[:50]
        else:
            output_str = type(result['output']).__name__
        print(f"     Output: {output_str}")

successes = sum(1 for r in results if r['status'] == 'success')
print(f"\n✓ Program didn't crash! {successes}/{len(results)} succeeded")

# Demonstration 2: Validation before execution
print("\n" + "=" * 70)
print("DEMO 2: Validating Before Execution")
print("=" * 70)

print("\n🔍 LLM can validate calls before executing:\n")

test_calls = [
    {'tool': 'write_file', 'args': {'path': 'test.py', 'content': '# test'}},
    {'tool': 'write_file', 'args': {'path': 'test.py'}},  # Missing content
    {'tool': 'super_tool', 'args': {'power': 9000}},  # Doesn't exist
]

for call in test_calls:
    validation = validate_tool_call(call['tool'], **call['args'])
    
    status = '✅ VALID' if validation['valid'] else '❌ INVALID'
    print(f"  {status}: {call['tool']}")
    
    if not validation['valid']:
        print(f"     Error: {validation['error']}")

# Demonstration 3: Tool discovery
print("\n" + "=" * 70)
print("DEMO 3: Dynamic Tool Discovery")
print("=" * 70)

print("\n🔎 LLM can discover tools at runtime:\n")

# Orchestrator wants to find analysis tools
print("  Query: 'Show me all analysis tools'")
analysis_tools = list_available_tools(category='analysis')
print(f"  Found {len(analysis_tools)} tools: {analysis_tools}")

# Get details about one
print(f"\n  Query: 'Tell me about run_pylint'")
info = get_tool_info('run_pylint')
print(f"  Description: {info['description']}")
print(f"  Required args: {info['required_args']}")
print(f"  Optional args: {info['optional_args']}")

# Demonstration 4: Complete self-healing workflow
print("\n" + "=" * 70)
print("DEMO 4: Self-Healing Loop Using Only execute_tool()")
print("=" * 70)

print("\n🔄 Orchestrator executes entire workflow via Dispatcher:\n")

workflow = [
    ("Create backup", 'backup_sandbox', {'backup_name': 'demo_backup'}),
    ("Write code", 'write_file', {'path': 'demo.py', 'content': 'def add(a,b):\n    return a+b'}),
    ("Check syntax", 'check_syntax', {'code_string': 'def add(a,b):\n    return a+b'}),
    ("Format code", 'apply_black_formatting', {'path': 'demo.py'}),
    ("Analyze quality", 'analyze_code_quality', {'path': 'demo.py'}),
    ("List files", 'list_files', {}),
]

for i, (desc, tool, args) in enumerate(workflow, 1):
    result = execute_tool(tool, **args)
    status = '✅' if result['status'] == 'success' else '❌'
    print(f"  {i}. {status} {desc} → {tool}()")
    
    if result['status'] == 'error':
        print(f"     ⚠️  {result['error_type']}: {result['error'][:50]}...")

# Summary
print("\n" + "=" * 70)
print("KEY BENEFITS")
print("=" * 70)

print("""
🎯 Why the Dispatcher is Critical:

1. 🛡️  CRASH PREVENTION: Never crashes on invalid tool names
2. 🔧 NO IF/ELSE HELL: One function instead of 20+ conditionals
3. 📊 STANDARDIZED OUTPUT: Always returns {'status', 'output', 'error'}
4. ✅ AUTO VALIDATION: Built-in argument and type checking
5. 🔍 DISCOVERY: LLMs can list and learn about available tools
6. 🐛 ERROR HANDLING: All exceptions caught and categorized
7. 📝 DOCUMENTATION: Auto-generated tool info from metadata

💡 Perfect for LLM orchestrators that need to:
   • Call tools dynamically based on LLM output
   • Handle hallucinated tool names gracefully
   • Validate calls before executing
   • Discover available capabilities
   • Never crash the main program

⚠️  Without Dispatcher: Students write brittle if/else chains that
    crash when LLM hallucinates "make_sandwich" tool 🥪

✅ With Dispatcher: Robust, maintainable, crash-proof tool execution!
""")

print("=" * 70)

# Show example output structure
print("\n" + "=" * 70)
print("STANDARDIZED OUTPUT FORMAT")
print("=" * 70)

print("\n📦 All execute_tool() calls return this structure:\n")

example_success = {
    'status': 'success',
    'tool': 'read_file',
    'output': '<tool output here>',
    'error': None,
    'error_type': None
}

example_error = {
    'status': 'error',
    'tool': 'fake_tool',
    'output': None,
    'error': 'Tool not found...',
    'error_type': 'ToolNotFoundError'
}

print("SUCCESS:")
print(json.dumps(example_success, indent=2))

print("\nERROR:")
print(json.dumps(example_error, indent=2))

print("\n✅ Orchestrator can always check result['status'] to handle outcomes!")

print("\n" + "=" * 70)
