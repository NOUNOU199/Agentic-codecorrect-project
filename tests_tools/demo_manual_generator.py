"""
Interactive demo for Increment 7: The Manual Generator
Shows automatic documentation generation for Prompt Engineers.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import get_tools_documentation, execute_tool
import json

print("=" * 80)
print("THE MANUAL GENERATOR - Automatic Tool Documentation")
print("For the Prompt Engineer")
print("=" * 80)

print("\n📖 THE PROBLEM:")
print("   Prompt Engineer needs to tell LLMs what tools are available.")
print("   Questions like:")
print("   • 'What are the exact arguments for run_pylint?'")
print("   • 'Which tools can analyze code?'")
print("   • 'How do I use the backup functions?'")
print("")
print("   ❌ Old way: Manually write and maintain documentation")
print("   ✅ New way: Auto-generate from the code itself!")

# Demo 1: Detailed Documentation
print("\n" + "=" * 80)
print("DEMO 1: Detailed Documentation (Default)")
print("=" * 80)

print("\n📝 Usage: get_tools_documentation()")
print("\nGenerating detailed documentation...\n")

detailed_docs = get_tools_documentation()
print(detailed_docs[:1500] + "\n... (truncated for demo)")

# Demo 2: Compact Format
print("\n" + "=" * 80)
print("DEMO 2: Compact Format (Quick Reference)")
print("=" * 80)

print("\n📝 Usage: get_tools_documentation(format_type='compact')")
print("\n")

compact_docs = get_tools_documentation(format_type='compact')
print(compact_docs)

# Demo 3: JSON Format
print("\n" + "=" * 80)
print("DEMO 3: JSON Format (Machine-Readable)")
print("=" * 80)

print("\n📝 Usage: get_tools_documentation(format_type='json')")
print("\n")

json_docs = get_tools_documentation(format_type='json')
json_obj = json.loads(json_docs)

# Show a sample tool
print("Sample tool documentation (read_file):")
print(json.dumps(json_obj['read_file'], indent=2))

print(f"\n✅ Generated JSON for {len(json_obj)} tools")
print(f"   Total size: {len(json_docs)} characters")

# Demo 4: Markdown Format
print("\n" + "=" * 80)
print("DEMO 4: Markdown Format (For README/Docs)")
print("=" * 80)

print("\n📝 Usage: get_tools_documentation(format_type='markdown')")
print("\n")

markdown_docs = get_tools_documentation(format_type='markdown')
print(markdown_docs[:800] + "\n... (truncated for demo)")

# Demo 5: Category Filtering
print("\n" + "=" * 80)
print("DEMO 5: Category Filtering")
print("=" * 80)

print("\n📝 Only show analysis tools:")
print("   get_tools_documentation(category='analysis')\n")

analysis_docs = get_tools_documentation(format_type='compact', category='analysis')
print(analysis_docs)

print("\n📝 Only show filesystem tools:")
print("   get_tools_documentation(category='filesystem')\n")

filesystem_docs = get_tools_documentation(format_type='compact', category='filesystem')
print(filesystem_docs)

# Demo 6: Use Case - System Prompt Generation
print("\n" + "=" * 80)
print("DEMO 6: Real Use Case - System Prompt for LLM")
print("=" * 80)

print("\n🤖 Prompt Engineer creates a system prompt:\n")

system_prompt = f"""You are an AI assistant helping developers write Python code.

You have access to the following tools in a sandboxed environment:

{get_tools_documentation(format_type='compact')}

When the user asks you to create, modify, or test code:
1. Use write_file() to create/update files
2. Use check_syntax() and run_pylint() to analyze code quality
3. Use run_script() to test execution
4. Use backup_sandbox() before making risky changes
5. Use restore_sandbox() if something goes wrong

Always work within the sandbox for safety!
"""

print(system_prompt)

print("\n✅ System prompt generated automatically!")
print(f"   Contains documentation for all {len(json_obj)} tools")

# Demo 7: Callable via Dispatcher
print("\n" + "=" * 80)
print("DEMO 7: Callable via Dispatcher")
print("=" * 80)

print("\n🔧 The manual generator is itself a tool!")
print("   LLMs can call it to learn about available tools\n")

# LLM calls the tool
result = execute_tool('get_tools_documentation', 
                     format_type='compact', 
                     category='backup')

print("LLM query: 'What backup tools are available?'")
print("LLM calls: execute_tool('get_tools_documentation', category='backup')\n")
print(f"Result status: {result['status']}")
print(f"\nDocumentation returned:")
print(result['output'])

# Demo 8: Comparing Formats
print("\n" + "=" * 80)
print("DEMO 8: Format Comparison")
print("=" * 80)

formats = {
    'detailed': get_tools_documentation(format_type='detailed'),
    'compact': get_tools_documentation(format_type='compact'),
    'json': get_tools_documentation(format_type='json'),
    'markdown': get_tools_documentation(format_type='markdown'),
}

print("\n📊 Documentation sizes by format:\n")
for fmt, content in formats.items():
    lines = content.count('\n') + 1
    chars = len(content)
    print(f"  {fmt:10s}: {chars:6,d} chars, {lines:4d} lines")

print("\n💡 Choose format based on use case:")
print("  • compact  : System prompts (minimal token usage)")
print("  • detailed : Human-readable reference")
print("  • json     : API documentation / programmatic access")
print("  • markdown : README files / GitHub documentation")

# Demo 9: Self-Documentation (Meta!)
print("\n" + "=" * 80)
print("DEMO 9: Self-Documentation (Very Meta!)")
print("=" * 80)

print("\n🔍 The manual generator can document itself!\n")

meta_docs = get_tools_documentation(format_type='compact', category='meta')
print(meta_docs)

print("\n🤯 This tool generates its own documentation!")
print("   The LLM can learn how to generate documentation by reading")
print("   the documentation that was generated by the generator!")

# Demo 10: Integration Example
print("\n" + "=" * 80)
print("DEMO 10: Complete Integration Example")
print("=" * 80)

print("\n🎬 Scenario: Prompt Engineer sets up an LLM orchestrator\n")

print("Step 1: Generate tool documentation")
print("  docs = get_tools_documentation(format_type='json')")

print("\nStep 2: Parse into structured format")
print("  tools_spec = json.loads(docs)")

print("\nStep 3: Build system prompt")
print("  system_prompt = build_prompt_with_tools(tools_spec)")

print("\nStep 4: LLM receives prompt and learns about tools")
print("  llm_response = call_llm(system_prompt, user_query)")

print("\nStep 5: LLM uses execute_tool() to call tools")
print("  result = execute_tool(tool_name, **args)")

print("\n✅ Complete workflow with zero manual documentation!")

# Summary
print("\n" + "=" * 80)
print("KEY BENEFITS FOR PROMPT ENGINEERS")
print("=" * 80)

print("""
🎯 Why the Manual Generator is Critical:

1. 🔄 ALWAYS UP-TO-DATE: Documentation auto-generated from code
   • Add a new tool? Documentation updates automatically
   • No more outdated docs in system prompts!

2. 📝 MULTIPLE FORMATS: One function, four output formats
   • Compact for token-efficient prompts
   • Detailed for human reference
   • JSON for programmatic access
   • Markdown for README files

3. 🔍 SMART FILTERING: Get exactly what you need
   • Filter by category (analysis, filesystem, etc.)
   • Generate docs for specific tool subsets

4. 🤖 LLM-FRIENDLY: Designed for AI consumption
   • Clear structure
   • Complete type information
   • Required vs optional arguments explicit

5. 🔧 SELF-DOCUMENTING: The tool documents itself
   • LLMs can discover their own capabilities
   • Meta-circular documentation loop

6. 🎨 ZERO MAINTENANCE: Never write tool docs manually
   • Docstrings → formatted documentation
   • inspect module extracts signatures
   • TOOLS_METADATA provides categorization

💡 Usage Patterns:

# In your system prompt
tools_docs = get_tools_documentation(format_type='compact')
system_prompt = f"Available tools:\n{tools_docs}"

# For API documentation
api_docs = get_tools_documentation(format_type='json')
save_to_file('api_docs.json', api_docs)

# For README
readme_section = get_tools_documentation(format_type='markdown')
append_to_readme(readme_section)

# For specific categories only
analysis_tools = get_tools_documentation(category='analysis')
""")

print("=" * 80)
print("\n🎉 The Prompt Engineer can now focus on prompt design,")
print("   not on maintaining tool documentation!")
print("\n" + "=" * 80)
