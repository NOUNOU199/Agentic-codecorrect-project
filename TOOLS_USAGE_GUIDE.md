# Tools Usage Guide

**A Practical Guide to Using the Sandboxed Python Development Tools**

---

## 📖 Overview

This project provides a comprehensive toolkit for AI agents and developers to safely create, test, analyze, and debug Python code in a sandboxed environment. The tools are organized into 6 categories with 18 total functions designed to work together seamlessly.

**Key Principle:** All file operations happen inside the `sandbox/` directory for security.

---

## 🎯 Quick Start

### Basic Workflow

```python
from src.tools import execute_tool

# 1. Create a Python file
execute_tool('write_file', path='hello.py', content='print("Hello, World!")')

# 2. Check syntax
execute_tool('check_syntax', code_string='print("Hello, World!")')

# 3. Run it
execute_tool('run_script', script_path='hello.py')

# 4. Format it nicely
execute_tool('apply_black_formatting', path='hello.py')
```

### Using the Dispatcher

**Always use `execute_tool()` instead of calling functions directly:**
- ✅ `execute_tool('read_file', path='test.py')` - Safe, handles errors
- ❌ `read_file('test.py')` - Direct call, crashes on errors

**Why?** The dispatcher provides:
- Error handling (never crashes)
- Standardized output format
- Validation before execution

---

## 📁 Category 1: FILESYSTEM Tools

**Purpose:** Create, read, and manage files safely within the sandbox.

### `write_file(path, content)`

**What it does:** Creates or overwrites a file in the sandbox.

**When to use:**
- Creating new Python files
- Updating existing code
- Saving generated content

**Example:**
```python
# Create a simple script
result = execute_tool('write_file', 
    path='calculator.py',
    content='''def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

if __name__ == "__main__":
    print(add(5, 3))
    print(subtract(10, 4))
''')

if result['status'] == 'success':
    print("✅ File created successfully")
```

**Pro Tips:**
- Paths are relative to `sandbox/` directory
- Parent directories are created automatically
- Use triple quotes (`'''`) for multi-line content

---

### `read_file(path)`

**What it does:** Reads the contents of a file from the sandbox.

**When to use:**
- Inspecting existing code
- Loading file contents before modification
- Debugging what's actually in a file

**Example:**
```python
# Read what we just created
result = execute_tool('read_file', path='calculator.py')

if result['status'] == 'success':
    print("File contents:")
    print(result['output'])
```

**Pro Tips:**
- Returns the full file content as a string
- Use this before editing to avoid overwriting changes
- Combine with syntax checking to validate files

---

### `list_files(path=None)`

**What it does:** Lists all files in the sandbox recursively.

**When to use:**
- See what files exist
- Finding files you created earlier
- Understanding the sandbox structure

**Example:**
```python
# List all files
result = execute_tool('list_files')

if result['status'] == 'success':
    print("Files in sandbox:")
    for file in result['output']:
        print(f"  - {file}")
```

**Pro Tips:**
- Returns relative paths from sandbox root
- Includes all subdirectories
- Great for debugging "file not found" errors

---

### `validate_path(path)`

**What it does:** Checks if a path is safe (inside sandbox).

**When to use:**
- Validating user input
- Before attempting file operations
- Security checking

**Example:**
```python
# Check if path is safe
result = execute_tool('validate_path', path='../../../etc/passwd')

if result['status'] == 'error':
    print("⚠️ Dangerous path detected!")
```

**Pro Tips:**
- Always validates before file operations
- Prevents directory traversal attacks
- Built into all file operations automatically

---

## 🔍 Category 2: ANALYSIS Tools

**Purpose:** Check code quality, find bugs, and ensure correctness.

### `check_syntax(code_string)`

**What it does:** Validates Python syntax without running code.

**When to use:**
- Before saving a file
- Quick validation of generated code
- Finding syntax errors early

**Example:**
```python
# Good syntax
good_code = 'print("Hello")'
result = execute_tool('check_syntax', code_string=good_code)
print(result['output'])  # (True, "Valid Python syntax")

# Bad syntax
bad_code = 'print("Hello"'  # Missing closing )
result = execute_tool('check_syntax', code_string=bad_code)
print(result['output'])  # (False, "SyntaxError: ...")
```

**Pro Tips:**
- Fast - no execution needed
- Catches basic errors immediately
- Use before `write_file()` to avoid saving broken code

---

### `run_pylint(path, return_full_report=False)`

**What it does:** Runs pylint to analyze code quality and style.

**When to use:**
- After writing code
- Before submitting/committing
- Learning better coding practices

**Example:**
```python
# Analyze code quality
result = execute_tool('run_pylint', path='calculator.py')

if result['status'] == 'success':
    output = result['output']
    print(f"Score: {output['score']}/10")
    print(f"Total issues: {output['total_issues']}")
    
    # Show critical issues
    if output['critical_issues']:
        print("\n⚠️ Critical issues:")
        for issue in output['critical_issues']:
            print(f"  Line {issue['line']}: {issue['message']}")
```

**Pro Tips:**
- Score > 8.0 is excellent
- Score > 6.0 is acceptable
- Focus on critical and major issues first
- Use `return_full_report=True` for detailed analysis

---

### `analyze_code_quality(path)`

**What it does:** Combines syntax check + pylint analysis.

**When to use:**
- Comprehensive code review
- Before running tests
- Quality gate checks

**Example:**
```python
# Full analysis
result = execute_tool('analyze_code_quality', path='calculator.py')

if result['status'] == 'success':
    output = result['output']
    
    if output['syntax_valid']:
        print(f"✅ Syntax OK")
        print(f"📊 Quality Score: {output['pylint_score']}/10")
        print(f"🐛 Total Issues: {output['total_issues']}")
        
        # Show recommendations
        print("\n💡 Recommendations:")
        for rec in output['recommendations']:
            print(f"  - {rec}")
```

**Pro Tips:**
- One-stop quality check
- Gets both syntax AND style issues
- Includes actionable recommendations

---

## ⚙️ Category 3: EXECUTION Tools

**Purpose:** Run code safely with timeout protection.

### `run_script(script_path, timeout=10, args=None)`

**What it does:** Executes a Python script with timeout protection.

**When to use:**
- Testing if code works
- Running demos
- Validating fixes

**Example:**
```python
# Run a simple script
result = execute_tool('run_script', 
    script_path='calculator.py',
    timeout=5)

if result['status'] == 'success':
    print("Output:")
    print(result['output']['output'])
else:
    print(f"Error: {result['error']}")
```

**With arguments:**
```python
# Pass command-line arguments
result = execute_tool('run_script',
    script_path='greeter.py',
    args=['Alice', 'Bob'],
    timeout=3)
```

**Pro Tips:**
- Default timeout is 10 seconds
- Captures stdout and stderr separately
- Returns exit code
- Prevents infinite loops with timeout

---

### `run_pytest(test_file_path, verbose=True, timeout=30)`

**What it does:** Runs pytest on test files.

**When to use:**
- Running unit tests
- Validating test suites
- TDD workflow

**Example:**
```python
# Run tests
result = execute_tool('run_pytest',
    test_file_path='test_calculator.py',
    verbose=True)

if result['status'] == 'success':
    output = result['output']
    if output['success']:
        print(f"✅ {output['tests_passed']} tests passed!")
    else:
        print(f"❌ {output['tests_failed']} tests failed")
        print(output['output'])
```

**Pro Tips:**
- Install pytest first: `pip install pytest`
- Use verbose=True for detailed output
- Check `tests_passed` count
- Timeout defaults to 30 seconds for slow tests

---

### `test_and_analyze(script_path, test_path=None)`

**What it does:** Complete workflow - run script, check quality, run tests.

**When to use:**
- Full validation pipeline
- Before committing code
- CI/CD workflows

**Example:**
```python
# Complete test suite
result = execute_tool('test_and_analyze',
    script_path='calculator.py',
    test_path='test_calculator.py')

if result['status'] == 'success':
    output = result['output']
    
    print(f"Script ran: {output['script_execution']['success']}")
    print(f"Quality score: {output['quality_analysis']['pylint_score']}")
    print(f"Tests passed: {output['tests']['tests_passed']}")
    
    if output['all_passed']:
        print("🎉 Everything passed!")
```

**Pro Tips:**
- One command for complete validation
- Stops if script fails to run
- Skips tests if no test file provided

---

## 🎨 Category 4: FORMATTING Tools

**Purpose:** Make code beautiful and maintainable.

### `apply_black_formatting(path, line_length=88, check_only=False)`

**What it does:** Formats Python code using Black formatter.

**When to use:**
- Before committing code
- Cleaning up messy code
- Enforcing consistent style

**Example:**
```python
# Format a file
result = execute_tool('apply_black_formatting',
    path='messy_code.py',
    line_length=88)

if result['status'] == 'success':
    output = result['output']
    if output['changed']:
        print("✅ Code formatted")
        print(f"Changes: {output['diff']}")
    else:
        print("✨ Code already perfectly formatted")
```

**Check without changing:**
```python
# Just check if formatting needed
result = execute_tool('apply_black_formatting',
    path='code.py',
    check_only=True)

if result['output']['would_reformat']:
    print("⚠️ File needs formatting")
```

**Pro Tips:**
- Default line length is 88 (Black's standard)
- Use `check_only=True` to preview changes
- Black installs automatically if missing

---

### `get_project_structure(base_path=None, max_depth=5, show_hidden=False)`

**What it does:** Shows directory tree structure.

**When to use:**
- Understanding project layout
- Documentation
- Debugging file organization

**Example:**
```python
# Show full structure
result = execute_tool('get_project_structure')

if result['status'] == 'success':
    print(result['output'])
    # Output:
    # sandbox/
    # ├── calculator.py
    # ├── test_calculator.py
    # └── utils/
    #     └── helpers.py
```

**Pro Tips:**
- Set `max_depth` to limit recursion
- `show_hidden=False` skips `.git`, `__pycache__`, etc.
- Great for README documentation

---

### `format_and_analyze(path)`

**What it does:** Format with Black, then analyze quality.

**When to use:**
- Code cleanup workflow
- Before code review
- Ensuring both style and quality

**Example:**
```python
# Format + analyze in one go
result = execute_tool('format_and_analyze',
    path='calculator.py')

if result['status'] == 'success':
    output = result['output']
    
    if output['formatting']['changed']:
        print("✅ Code formatted")
    
    print(f"Quality score: {output['analysis']['pylint_score']}/10")
```

**Pro Tips:**
- Formatting improves pylint scores
- Two-step quality improvement
- Ideal for automated workflows

---

## 💾 Category 5: BACKUP Tools

**Purpose:** Save and restore sandbox state for safety.

### `backup_sandbox(backup_name=None)`

**What it does:** Creates a snapshot of the entire sandbox.

**When to use:**
- Before risky changes
- Before major refactoring
- Creating checkpoints

**Example:**
```python
# Create backup before changes
result = execute_tool('backup_sandbox',
    backup_name='before_refactor')

if result['status'] == 'success':
    print("✅ Backup created")
    
    # Now make risky changes...
    execute_tool('write_file', path='calculator.py', content='...')
```

**Auto-named backup:**
```python
# Creates backup with timestamp
result = execute_tool('backup_sandbox')
# Name: backup_20260112_143022
```

**Pro Tips:**
- Backups stored in `.sandbox_backup/` (git-ignored)
- Auto-named backups include timestamp
- Includes metadata (timestamp, file count)

---

### `restore_sandbox(backup_name=None, confirm=True)`

**What it does:** Restores sandbox from a backup.

**When to use:**
- After mistakes
- Undoing changes
- Testing different approaches

**Example:**
```python
# List available backups first
backups = execute_tool('list_backups')
print("Available backups:")
for backup in backups['output']:
    print(f"  - {backup['name']}")

# Restore from specific backup
result = execute_tool('restore_sandbox',
    backup_name='before_refactor',
    confirm=True)

if result['status'] == 'success':
    print("✅ Sandbox restored")
```

**Restore latest:**
```python
# Restore most recent backup
result = execute_tool('restore_sandbox')
```

**Pro Tips:**
- `confirm=True` required for safety
- Restores latest backup if no name given
- **WARNING:** Deletes current sandbox contents!

---

### `list_backups()`

**What it does:** Shows all available backups with metadata.

**When to use:**
- Before restoring
- Managing backups
- Checking backup history

**Example:**
```python
result = execute_tool('list_backups')

if result['status'] == 'success':
    backups = result['output']
    
    print(f"Total backups: {len(backups)}\n")
    
    for backup in backups:
        print(f"Name: {backup['name']}")
        print(f"Created: {backup['created_at']}")
        print(f"Files: {backup['file_count']}")
        print(f"Size: {backup['size_mb']:.2f} MB")
        print("---")
```

**Pro Tips:**
- Sorted by creation time (newest first)
- Includes file count and size
- Use to pick the right backup to restore

---

### `delete_backup(backup_name)`

**What it does:** Permanently deletes a backup.

**When to use:**
- Cleaning up old backups
- Managing disk space
- Removing unnecessary snapshots

**Example:**
```python
# Delete specific backup
result = execute_tool('delete_backup',
    backup_name='old_backup_20250101')

if result['status'] == 'success':
    print("✅ Backup deleted")
```

**Pro Tips:**
- Permanent deletion - cannot undo
- Free up disk space
- Keep important backups!

---

## 📚 Category 6: META Tools

**Purpose:** Self-documentation and tool discovery.

### `get_tools_documentation(format_type='detailed', category=None)`

**What it does:** Generates documentation for all tools.

**When to use:**
- Creating system prompts for LLMs
- Generating API documentation
- Learning about available tools

**Example:**
```python
# Compact format for LLM system prompts
docs = execute_tool('get_tools_documentation',
    format_type='compact')

system_prompt = f"""You are a Python coding assistant.
Available tools:
{docs['output']}
"""

# JSON for API specs
api_docs = execute_tool('get_tools_documentation',
    format_type='json')

# Markdown for README
readme = execute_tool('get_tools_documentation',
    format_type='markdown')

# Only analysis tools
analysis_docs = execute_tool('get_tools_documentation',
    category='analysis',
    format_type='compact')
```

**Formats:**
- `'detailed'` - Full human-readable docs (15K chars)
- `'compact'` - Token-efficient for prompts (1.7K chars)
- `'json'` - Machine-readable structured data (18K chars)
- `'markdown'` - README-ready docs (13K chars)

**Pro Tips:**
- Use `compact` for LLM system prompts (88% token savings)
- Filter by category to get specific tools
- Always up-to-date (generated from code)

---

## 🔄 Common Workflows

### Workflow 1: Create and Test a New Script

```python
# 1. Create backup (safety first!)
execute_tool('backup_sandbox', backup_name='before_new_script')

# 2. Write the script
code = '''
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    print(factorial(5))
'''
execute_tool('write_file', path='factorial.py', content=code)

# 3. Check syntax
result = execute_tool('check_syntax', code_string=code)
if not result['output'][0]:
    print("❌ Syntax error!")

# 4. Format it
execute_tool('apply_black_formatting', path='factorial.py')

# 5. Run it
result = execute_tool('run_script', script_path='factorial.py')
print("Output:", result['output']['output'])

# 6. Analyze quality
result = execute_tool('analyze_code_quality', path='factorial.py')
print("Quality score:", result['output']['pylint_score'])
```

---

### Workflow 2: Fix a Buggy Script

```python
# 1. Read existing code
result = execute_tool('read_file', path='buggy.py')
original_code = result['output']

# 2. Backup before changes
execute_tool('backup_sandbox', backup_name='before_fix')

# 3. Analyze what's wrong
result = execute_tool('analyze_code_quality', path='buggy.py')
print("Issues found:", result['output']['critical_issues'])

# 4. Try to run it
result = execute_tool('run_script', script_path='buggy.py')
if result['status'] == 'error':
    print("Error:", result['error'])

# 5. Fix the code
fixed_code = original_code.replace('bug', 'fix')
execute_tool('write_file', path='buggy.py', content=fixed_code)

# 6. Test the fix
result = execute_tool('run_script', script_path='buggy.py')
if result['status'] == 'success':
    print("✅ Fixed!")
else:
    # Restore backup if fix didn't work
    execute_tool('restore_sandbox', backup_name='before_fix', confirm=True)
```

---

### Workflow 3: Code Review Process

```python
# 1. Get list of files
result = execute_tool('list_files')
files = [f for f in result['output'] if f.endswith('.py')]

# 2. Review each file
for file_path in files:
    print(f"\n📄 Reviewing {file_path}")
    
    # Format it
    fmt_result = execute_tool('apply_black_formatting', path=file_path)
    if fmt_result['output']['changed']:
        print("  ✏️  Formatted")
    
    # Analyze quality
    qa_result = execute_tool('analyze_code_quality', path=file_path)
    score = qa_result['output']['pylint_score']
    
    if score >= 8.0:
        print(f"  ✅ Excellent ({score}/10)")
    elif score >= 6.0:
        print(f"  ⚠️  Acceptable ({score}/10)")
    else:
        print(f"  ❌ Needs work ({score}/10)")
        
    # Show critical issues
    critical = qa_result['output']['critical_issues']
    if critical:
        print(f"  🐛 {len(critical)} critical issues")
```

---

### Workflow 4: Safe Experimentation

```python
# 1. Create experiment backup
execute_tool('backup_sandbox', backup_name='experiment_start')

# 2. Try approach A
execute_tool('write_file', path='solution.py', content=approach_a_code)
result_a = execute_tool('run_script', script_path='solution.py')
score_a = execute_tool('analyze_code_quality', path='solution.py')

# 3. Restore and try approach B
execute_tool('restore_sandbox', backup_name='experiment_start', confirm=True)
execute_tool('write_file', path='solution.py', content=approach_b_code)
result_b = execute_tool('run_script', script_path='solution.py')
score_b = execute_tool('analyze_code_quality', path='solution.py')

# 4. Keep the better approach
if score_a['output']['pylint_score'] > score_b['output']['pylint_score']:
    execute_tool('restore_sandbox', backup_name='experiment_start', confirm=True)
    execute_tool('write_file', path='solution.py', content=approach_a_code)
    print("✅ Kept approach A")
else:
    print("✅ Kept approach B")
```

---

## 🎯 Best Practices

### 1. Always Use the Dispatcher

```python
# ✅ GOOD - Safe, handles errors
result = execute_tool('read_file', path='test.py')
if result['status'] == 'success':
    content = result['output']

# ❌ BAD - Direct call, can crash
content = read_file('test.py')  # Don't do this!
```

### 2. Check Result Status

```python
# ✅ GOOD - Check before using output
result = execute_tool('run_script', script_path='app.py')
if result['status'] == 'success':
    print(result['output']['output'])
else:
    print(f"Error: {result['error']}")

# ❌ BAD - Assume success
print(result['output'])  # Might be None if error!
```

### 3. Backup Before Risky Operations

```python
# ✅ GOOD - Backup first
execute_tool('backup_sandbox', backup_name='before_refactor')
execute_tool('write_file', path='critical.py', content=new_code)

# ❌ BAD - No safety net
execute_tool('write_file', path='critical.py', content=new_code)
```

### 4. Use Quality Tools Early

```python
# ✅ GOOD - Check before saving
syntax_ok = execute_tool('check_syntax', code_string=new_code)
if syntax_ok['output'][0]:
    execute_tool('write_file', path='app.py', content=new_code)

# ❌ BAD - Save first, debug later
execute_tool('write_file', path='app.py', content=new_code)
execute_tool('check_syntax', code_string=new_code)  # Too late!
```

### 5. Clean Up Backups

```python
# ✅ GOOD - Manage backup storage
backups = execute_tool('list_backups')['output']
if len(backups) > 10:
    # Delete oldest backups
    for backup in backups[10:]:
        execute_tool('delete_backup', backup_name=backup['name'])

# ❌ BAD - Infinite backups filling disk
execute_tool('backup_sandbox')  # Every time, forever
```

---

## ⚠️ Important Limitations

### Security Boundaries
- **All operations restricted to `sandbox/` directory**
- Cannot access files outside sandbox
- Path validation prevents directory traversal
- Backups stored in `.sandbox_backup/` (outside sandbox)

### Execution Limits
- **Default timeout: 10 seconds for scripts, 30 for tests**
- Infinite loops are terminated
- No network access in sandbox
- No system command execution

### File System
- **No symbolic links** outside sandbox
- Hidden files (`.git`, `__pycache__`) ignored by default
- Maximum file size: System memory limit
- Recursive directory deletion is permanent

### Tool Dependencies
- **pylint**: Auto-installs if missing (requires pip)
- **pytest**: Auto-installs if missing (requires pip)
- **black**: Auto-installs if missing (requires pip)
- Internet required for first-time installation

---

## 🐛 Troubleshooting

### "File not found"
```python
# List files to see what exists
execute_tool('list_files')

# Check if path is valid
execute_tool('validate_path', path='your/path.py')
```

### "Syntax error but code looks fine"
```python
# Check for hidden characters
result = execute_tool('read_file', path='problematic.py')
print(repr(result['output']))  # Shows \r\n, \t, etc.
```

### "Script times out"
```python
# Increase timeout for slow operations
execute_tool('run_script', 
    script_path='slow.py',
    timeout=60)  # 60 seconds instead of 10
```

### "Pylint score too low"
```python
# Format first to improve style score
execute_tool('apply_black_formatting', path='messy.py')

# Then analyze
result = execute_tool('analyze_code_quality', path='messy.py')
# Score usually improves after formatting
```

### "Backup restore failed"
```python
# List available backups
backups = execute_tool('list_backups')['output']
print([b['name'] for b in backups])

# Use exact backup name
execute_tool('restore_sandbox', 
    backup_name='exact_name_from_list',
    confirm=True)
```

---

## 📊 Quick Reference Table

| Task | Tool | Example |
|------|------|---------|
| Create file | `write_file` | `execute_tool('write_file', path='app.py', content='...')` |
| Read file | `read_file` | `execute_tool('read_file', path='app.py')` |
| Check syntax | `check_syntax` | `execute_tool('check_syntax', code_string='print("hi")')` |
| Run code | `run_script` | `execute_tool('run_script', script_path='app.py')` |
| Format code | `apply_black_formatting` | `execute_tool('apply_black_formatting', path='app.py')` |
| Analyze quality | `analyze_code_quality` | `execute_tool('analyze_code_quality', path='app.py')` |
| Run tests | `run_pytest` | `execute_tool('run_pytest', test_file_path='test.py')` |
| Create backup | `backup_sandbox` | `execute_tool('backup_sandbox', backup_name='v1')` |
| Restore backup | `restore_sandbox` | `execute_tool('restore_sandbox', backup_name='v1', confirm=True)` |
| List files | `list_files` | `execute_tool('list_files')` |
| Get docs | `get_tools_documentation` | `execute_tool('get_tools_documentation', format_type='compact')` |

---

## 💡 Tips for AI Agents

### For LLM Orchestrators

1. **Use compact documentation in system prompts:**
   ```python
   docs = execute_tool('get_tools_documentation', format_type='compact')
   # Only 1,700 chars vs 15,000 - save 88% tokens!
   ```

2. **Always check result['status']:**
   ```python
   result = execute_tool('run_script', script_path='app.py')
   if result['status'] == 'error':
       # Handle error gracefully
       # Don't crash the orchestrator!
   ```

3. **Use backups for iterative development:**
   ```python
   execute_tool('backup_sandbox', backup_name='iteration_1')
   # Try changes...
   if not_working:
       execute_tool('restore_sandbox', backup_name='iteration_1', confirm=True)
   ```

4. **Validate before executing:**
   ```python
   # Check syntax first
   syntax_ok = execute_tool('check_syntax', code_string=generated_code)
   if syntax_ok['output'][0]:
       execute_tool('write_file', path='gen.py', content=generated_code)
   ```

---

## 🎓 Learning Path

### Beginner: Basic Operations
1. Start with `write_file()` and `read_file()`
2. Try `check_syntax()` to validate code
3. Use `run_script()` to execute
4. Experiment with `list_files()`

### Intermediate: Quality & Testing
1. Use `apply_black_formatting()` for clean code
2. Run `analyze_code_quality()` for feedback
3. Write tests and use `run_pytest()`
4. Combine tools in workflows

### Advanced: Automation & Safety
1. Create backups before experiments
2. Use `test_and_analyze()` for full validation
3. Build automated workflows
4. Generate documentation with `get_tools_documentation()`

---

## 📖 Additional Resources

### Project Structure
```
TP-OGL/
├── sandbox/              # Your workspace (all files here)
├── .sandbox_backup/      # Automatic backups (git-ignored)
├── src/
│   └── tools.py         # All tool implementations
├── tests_tools/         # Tool tests and demos
├── docs/                # Implementation documentation
└── TOOLS_USAGE_GUIDE.md # This file
```

### Getting Help

1. **Check tool documentation:**
   ```python
   docs = execute_tool('get_tools_documentation', 
       format_type='detailed',
       category='filesystem')  # Get specific category
   ```

2. **Run the demos:**
   ```bash
   python tests_tools/demo_dispatcher.py
   python tests_tools/demo_manual_generator.py
   ```

3. **Read the source:**
   - Main implementation: [src/tools.py](src/tools.py)
   - Usage examples: [tests_tools/](tests_tools/)

---

## 🎉 You're Ready!

You now have everything you need to use the tools effectively. Remember:

- 🛡️ **Safety first**: Use backups before risky changes
- 📊 **Quality matters**: Check syntax and run pylint
- 🔄 **Iterate**: Test, analyze, improve
- 🤖 **Let AI help**: Use the dispatcher for everything

**Happy coding in the sandbox!** 🚀
