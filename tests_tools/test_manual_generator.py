"""
Comprehensive tests for Increment 7: The Manual Generator
Tests automatic documentation generation for tools.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import (
    get_tools_documentation,
    execute_tool,
    TOOLS_MAPPING
)
import json

def test_detailed_documentation():
    """Test detailed documentation format."""
    print("TEST 1: Detailed Documentation Format")
    
    docs = get_tools_documentation(format_type='detailed')
    
    # Check structure
    assert "AVAILABLE TOOLS DOCUMENTATION" in docs
    assert "Total Tools:" in docs
    assert "Categories:" in docs
    
    # Check that all tools are documented
    for tool_name in TOOLS_MAPPING.keys():
        assert tool_name in docs, f"Tool {tool_name} not in documentation"
    
    # Check categories are present
    assert "FILESYSTEM" in docs.upper()
    assert "ANALYSIS" in docs.upper()
    assert "EXECUTION" in docs.upper()
    assert "FORMATTING" in docs.upper()
    assert "BACKUP" in docs.upper()
    assert "META" in docs.upper()  # New category for manual generator
    
    print("✅ Detailed documentation contains all tools and categories")


def test_compact_documentation():
    """Test compact documentation format."""
    print("\nTEST 2: Compact Documentation Format")
    
    docs = get_tools_documentation(format_type='compact')
    
    # Check structure
    assert "TOOLS QUICK REFERENCE" in docs
    
    # Should be shorter than detailed
    detailed = get_tools_documentation(format_type='detailed')
    assert len(docs) < len(detailed)
    
    # All tools should still be listed
    for tool_name in TOOLS_MAPPING.keys():
        assert tool_name in docs
    
    print(f"✅ Compact format is shorter ({len(docs)} vs {len(detailed)} chars)")


def test_json_documentation():
    """Test JSON documentation format."""
    print("\nTEST 3: JSON Documentation Format")
    
    docs_str = get_tools_documentation(format_type='json')
    
    # Should be valid JSON
    try:
        docs = json.loads(docs_str)
    except json.JSONDecodeError:
        assert False, "Documentation is not valid JSON"
    
    # Check structure
    assert isinstance(docs, dict)
    
    # All tools should be present
    for tool_name in TOOLS_MAPPING.keys():
        assert tool_name in docs, f"Tool {tool_name} not in JSON docs"
        
        tool_doc = docs[tool_name]
        assert 'description' in tool_doc
        assert 'category' in tool_doc
        assert 'required_args' in tool_doc
        assert 'optional_args' in tool_doc
        assert 'parameters' in tool_doc
    
    print(f"✅ Valid JSON with {len(docs)} tools documented")


def test_markdown_documentation():
    """Test Markdown documentation format."""
    print("\nTEST 4: Markdown Documentation Format")
    
    docs = get_tools_documentation(format_type='markdown')
    
    # Check Markdown structure
    assert "# Tools Documentation" in docs
    assert "**Total Tools:**" in docs
    
    # Check for Markdown headers
    assert "##" in docs  # Category headers
    assert "###" in docs  # Tool headers
    
    # Check for code formatting
    assert "`" in docs  # Inline code
    assert "```" in docs  # Code blocks
    
    # All tools should be documented
    for tool_name in TOOLS_MAPPING.keys():
        assert tool_name in docs
    
    print("✅ Valid Markdown documentation generated")


def test_category_filtering():
    """Test filtering documentation by category."""
    print("\nTEST 5: Category Filtering")
    
    # Test filesystem category
    fs_docs = get_tools_documentation(category='filesystem')
    assert 'read_file' in fs_docs
    assert 'write_file' in fs_docs
    assert 'run_pylint' not in fs_docs  # Should not include analysis tools
    
    # Test analysis category
    analysis_docs = get_tools_documentation(category='analysis')
    assert 'check_syntax' in analysis_docs
    assert 'run_pylint' in analysis_docs
    assert 'read_file' not in analysis_docs  # Should not include filesystem tools
    
    # Test meta category (new!)
    meta_docs = get_tools_documentation(category='meta')
    assert 'get_tools_documentation' in meta_docs
    assert 'read_file' not in meta_docs
    
    print("✅ Category filtering works correctly")


def test_format_types_complete():
    """Test that all format types produce complete documentation."""
    print("\nTEST 6: Completeness Across Formats")
    
    formats = ['detailed', 'compact', 'json', 'markdown']
    
    for fmt in formats:
        docs = get_tools_documentation(format_type=fmt)
        
        # Should contain something
        assert len(docs) > 100, f"{fmt} format produced very short documentation"
        
        # Should document all tools (in some form)
        tool_count = 0
        for tool_name in TOOLS_MAPPING.keys():
            if tool_name in docs:
                tool_count += 1
        
        assert tool_count == len(TOOLS_MAPPING), \
            f"{fmt} format missing {len(TOOLS_MAPPING) - tool_count} tools"
        
        print(f"  ✅ {fmt}: {len(docs)} chars, {tool_count} tools")


def test_documentation_includes_signatures():
    """Test that documentation includes function signatures."""
    print("\nTEST 7: Function Signatures Included")
    
    docs = get_tools_documentation(format_type='detailed')
    
    # Check specific signatures
    assert "read_file(path)" in docs or "read_file(" in docs
    assert "write_file(path" in docs
    assert "run_pylint(path" in docs
    
    # Check that required vs optional is documented
    assert "Required Arguments:" in docs or "required" in docs.lower()
    
    print("✅ Function signatures are documented")


def test_documentation_includes_descriptions():
    """Test that documentation includes tool descriptions."""
    print("\nTEST 8: Tool Descriptions Included")
    
    docs = get_tools_documentation(format_type='detailed')
    
    # Check that descriptions are present
    assert "sandbox" in docs.lower()  # Filesystem tools mention sandbox
    assert "syntax" in docs.lower()   # Analysis tools mention syntax
    assert "format" in docs.lower()   # Formatting tools mention format
    assert "backup" in docs.lower()   # Backup tools mention backup
    
    print("✅ Tool descriptions are included")


def test_callable_via_dispatcher():
    """Test that get_tools_documentation can be called via dispatcher."""
    print("\nTEST 9: Callable via Dispatcher")
    
    # Call via execute_tool
    result = execute_tool('get_tools_documentation', format_type='compact')
    
    assert result['status'] == 'success'
    assert result['output'] is not None
    assert 'TOOLS QUICK REFERENCE' in result['output']
    
    # Test with category filter
    result = execute_tool('get_tools_documentation', 
                         format_type='detailed', 
                         category='filesystem')
    
    assert result['status'] == 'success'
    assert 'read_file' in result['output']
    assert 'run_pylint' not in result['output']
    
    print("✅ get_tools_documentation callable via dispatcher")


def test_json_structure_details():
    """Test detailed structure of JSON documentation."""
    print("\nTEST 10: JSON Structure Details")
    
    docs_str = get_tools_documentation(format_type='json')
    docs = json.loads(docs_str)
    
    # Check a specific tool in detail
    read_file_doc = docs['read_file']
    
    assert read_file_doc['category'] == 'filesystem'
    assert 'path' in read_file_doc['required_args']
    assert 'description' in read_file_doc
    assert 'parameters' in read_file_doc
    
    # Check that parameters have details
    assert isinstance(read_file_doc['parameters'], dict)
    
    print("✅ JSON documentation has detailed structure")


def test_use_case_system_prompt():
    """Test realistic use case: generating a system prompt."""
    print("\nTEST 11: Use Case - System Prompt Generation")
    
    # Simulate what a Prompt Engineer would do
    system_prompt = f"""You are an AI assistant with access to Python development tools.

Available Tools:
{get_tools_documentation(format_type='compact')}

Use these tools to help users develop, test, and debug Python code.
"""
    
    # Check that system prompt is useful
    assert len(system_prompt) > 500
    assert "read_file" in system_prompt
    assert "write_file" in system_prompt
    assert "run_pylint" in system_prompt
    
    print(f"✅ Generated system prompt: {len(system_prompt)} chars")
    print(f"   Contains all {len(TOOLS_MAPPING)} tools")


def test_use_case_api_documentation():
    """Test realistic use case: API documentation."""
    print("\nTEST 12: Use Case - API Documentation")
    
    # Generate API docs in Markdown
    api_docs = get_tools_documentation(format_type='markdown')
    
    # Save to a mock file path (just check it's viable)
    lines = api_docs.split('\n')
    
    assert lines[0].startswith('# ')  # Proper Markdown title
    assert any('##' in line for line in lines)  # Has sections
    assert any('```' in line for line in lines)  # Has code blocks
    
    print(f"✅ Generated API documentation: {len(lines)} lines")


def test_self_documentation():
    """Test that the tool documents itself."""
    print("\nTEST 13: Self-Documentation (Meta!)")
    
    docs = get_tools_documentation(format_type='detailed')
    
    # The manual generator should document itself
    assert 'get_tools_documentation' in docs
    assert 'meta' in docs.lower()  # It's in the meta category
    
    # Check it has the right info
    assert 'format_type' in docs or 'format' in docs.lower()
    
    print("✅ Manual generator documents itself (very meta!)")


def test_error_handling_invalid_format():
    """Test handling of invalid format types."""
    print("\nTEST 14: Error Handling - Invalid Format")
    
    # Invalid format should default to 'detailed'
    docs = get_tools_documentation(format_type='invalid_format')
    
    # Should still work (defaults to detailed)
    assert "AVAILABLE TOOLS DOCUMENTATION" in docs
    assert len(docs) > 100
    
    print("✅ Invalid format gracefully defaults to 'detailed'")


def test_error_handling_invalid_category():
    """Test handling of invalid categories."""
    print("\nTEST 15: Error Handling - Invalid Category")
    
    # Invalid category should return empty or minimal documentation
    docs = get_tools_documentation(category='nonexistent_category')
    
    # Should not crash, but may be empty or minimal
    assert isinstance(docs, str)
    
    # Should not contain any tool names since category doesn't exist
    # (or contains very minimal structure)
    
    print("✅ Invalid category handled gracefully")


def run_all_tests():
    """Run all tests for the manual generator."""
    print("=" * 80)
    print("TESTING INCREMENT 7: THE MANUAL GENERATOR")
    print("=" * 80)
    
    tests = [
        test_detailed_documentation,
        test_compact_documentation,
        test_json_documentation,
        test_markdown_documentation,
        test_category_filtering,
        test_format_types_complete,
        test_documentation_includes_signatures,
        test_documentation_includes_descriptions,
        test_callable_via_dispatcher,
        test_json_structure_details,
        test_use_case_system_prompt,
        test_use_case_api_documentation,
        test_self_documentation,
        test_error_handling_invalid_format,
        test_error_handling_invalid_category,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"💥 ERROR: {type(e).__name__}: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Manual Generator is working perfectly!")
        print(f"📚 {len(TOOLS_MAPPING)} tools can now self-document in 4 formats")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
