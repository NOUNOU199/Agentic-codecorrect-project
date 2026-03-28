import os
import subprocess
import sys
import ast  # For syntax checking
import re
import json
import shutil
import time
import inspect
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Callable

# Define the sandbox directory as an absolute path
SANDBOX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sandbox'))
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.sandbox_backup'))

# Ensure sandbox directory exists
os.makedirs(SANDBOX_DIR, exist_ok=True)


def validate_path(path: str) -> str:
    """
    Validates that the given path is within the sandbox directory.
    
    Args:
        path: The path to validate (can be relative or absolute)
        
    Returns:
        The absolute path if valid
        
    Raises:
        ValueError: If the path is outside the sandbox directory
    """
    # Convert to absolute path
    if not os.path.isabs(path):
        abs_path = os.path.abspath(os.path.join(SANDBOX_DIR, path))
    else:
        abs_path = os.path.abspath(path)
    
    # Normalize paths to handle .. and . properly
    abs_path = os.path.normpath(abs_path)
    sandbox_norm = os.path.normpath(SANDBOX_DIR)
    
    # Check if the path starts with the sandbox directory
    if not abs_path.startswith(sandbox_norm + os.sep) and abs_path != sandbox_norm:
        raise ValueError(f"Access denied: Path '{path}' is outside the sandbox directory")
    
    return abs_path


def read_file(path: str) -> str:
    """
    Reads and returns the content of a file within the sandbox.
    
    Args:
        path: Path to the file (relative to sandbox or absolute within sandbox)
        
    Returns:
        The content of the file as a string
        
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file cannot be read
    """
    abs_path = validate_path(path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {path}")
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise PermissionError(f"Cannot read file '{path}': {str(e)}")


def write_file(path: str, content: str) -> None:
    """
    Writes content to a file within the sandbox, creating it if necessary.
    
    Args:
        path: Path to the file (relative to sandbox or absolute within sandbox)
        content: Content to write to the file
        
    Raises:
        ValueError: If the path is outside the sandbox
        PermissionError: If the file cannot be written
    """
    abs_path = validate_path(path)
    
    # Create parent directories if they don't exist
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise PermissionError(f"Cannot write to file '{path}': {str(e)}")


def list_files(path: str = "") -> List[str]:
    """
    Lists all files in the sandbox directory recursively.
    
    Args:
        path: Optional subdirectory within sandbox to list (default: root of sandbox)
        
    Returns:
        List of file paths relative to the sandbox directory
        
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the directory doesn't exist
    """
    if path:
        abs_path = validate_path(path)
    else:
        abs_path = SANDBOX_DIR
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Directory not found: {path}")
    
    if not os.path.isdir(abs_path):
        raise ValueError(f"Path is not a directory: {path}")
    
    file_list = []
    
    for root, dirs, files in os.walk(abs_path):
        for file in files:
            full_path = os.path.join(root, file)
            # Make path relative to sandbox
            rel_path = os.path.relpath(full_path, SANDBOX_DIR)
            file_list.append(rel_path)
    
    return sorted(file_list)


# ============================================================================
# INCREMENT 2: THE INSPECTOR - Smart Analysis Tools
# ============================================================================

def check_syntax(code_string: str) -> Tuple[bool, str]:
    """
    Validates Python syntax without executing the code.
    
    Args:
        code_string: Python code to validate
        
    Returns:
        Tuple of (is_valid, message):
            - (True, "Valid") if syntax is correct
            - (False, error_message) if syntax errors are found
    """
    try:
        ast.parse(code_string)
        return (True, "Valid")
    except SyntaxError as e:
        error_msg = f"Syntax error at line {e.lineno}"
        if e.offset:
            error_msg += f", column {e.offset}"
        error_msg += f": {e.msg}"
        if e.text:
            error_msg += f"\n  {e.text.rstrip()}"
            if e.offset:
                error_msg += f"\n  {' ' * (e.offset - 1)}^"
        return (False, error_msg)
    except Exception as e:
        return (False, f"Parsing error: {str(e)}")


def _ensure_pylint_installed() -> bool:
    """
    Checks if pylint is installed, attempts to install if not.
    
    Returns:
        True if pylint is available, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "pylint", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("Pylint not found. Attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pylint"],
                capture_output=True,
                check=True,
                timeout=60
            )
            print("✓ Pylint installed successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to install pylint: {e}")
            return False


def run_pylint(path: str, return_full_report: bool = False) -> Dict[str, Any]:
    """
    Runs pylint on a file and returns structured analysis data.
    
    Args:
        path: Path to the Python file (relative to sandbox or absolute within sandbox)
        return_full_report: If True, includes full raw output in results
        
    Returns:
        Dictionary containing:
            - 'score': float (0-10) or None if unavailable
            - 'errors': list of major errors/issues
            - 'error_count': number of errors
            - 'warning_count': number of warnings
            - 'convention_count': number of convention issues
            - 'refactor_count': number of refactor suggestions
            - 'by_category': dict of issues grouped by type
            - 'raw_output': full pylint output (if return_full_report=True)
            - 'success': bool indicating if pylint ran successfully
            
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the file doesn't exist
    """
    # Ensure pylint is available
    if not _ensure_pylint_installed():
        return {
            'success': False,
            'score': None,
            'errors': ["Pylint is not installed and could not be installed automatically"],
            'error_count': 0,
            'warning_count': 0,
            'convention_count': 0,
            'refactor_count': 0,
            'by_category': {},
            'raw_output': ""
        }
    
    abs_path = validate_path(path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {path}")
    
    try:
        # Run pylint with JSON output for structured parsing
        result = subprocess.run(
            [sys.executable, "-m", "pylint", abs_path, "--output-format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Also get the text report for score
        result_text = subprocess.run(
            [sys.executable, "-m", "pylint", abs_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse JSON output
        issues = []
        try:
            issues = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError:
            pass
        
        # Extract score from text output
        score = None
        score_match = re.search(r'rated at ([-\d.]+)/10', result_text.stdout)
        if score_match:
            score = float(score_match.group(1))
        
        # Categorize issues
        by_category = {
            'error': [],
            'warning': [],
            'convention': [],
            'refactor': [],
            'fatal': []
        }
        
        major_errors = []
        
        for issue in issues:
            issue_type = issue.get('type', 'unknown').lower()
            message = issue.get('message', '')
            line = issue.get('line', 0)
            symbol = issue.get('symbol', '')
            
            formatted = f"Line {line}: [{symbol}] {message}"
            
            if issue_type in by_category:
                by_category[issue_type].append(formatted)
            
            # Collect major errors (fatal, error, and critical warnings)
            if issue_type in ['error', 'fatal'] or (issue_type == 'warning' and 'undefined' in message.lower()):
                major_errors.append(formatted)
        
        return {
            'success': True,
            'score': score,
            'errors': major_errors,
            'error_count': len(by_category['error']) + len(by_category['fatal']),
            'warning_count': len(by_category['warning']),
            'convention_count': len(by_category['convention']),
            'refactor_count': len(by_category['refactor']),
            'by_category': by_category,
            'raw_output': result_text.stdout if return_full_report else ""
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'score': None,
            'errors': ["Pylint execution timed out"],
            'error_count': 0,
            'warning_count': 0,
            'convention_count': 0,
            'refactor_count': 0,
            'by_category': {},
            'raw_output': ""
        }
    except Exception as e:
        return {
            'success': False,
            'score': None,
            'errors': [f"Error running pylint: {str(e)}"],
            'error_count': 0,
            'warning_count': 0,
            'convention_count': 0,
            'refactor_count': 0,
            'by_category': {},
            'raw_output': ""
        }


def analyze_code_quality(path: str) -> Dict[str, Any]:
    """
    Performs comprehensive code quality analysis combining syntax check and pylint.
    
    Args:
        path: Path to the Python file to analyze
        
    Returns:
        Dictionary with combined analysis results:
            - 'syntax_valid': bool
            - 'syntax_message': str
            - 'pylint_score': float or None
            - 'total_issues': int
            - 'critical_issues': list
            - 'all_issues': dict by category
            - 'recommendations': list of improvement suggestions
    """
    abs_path = validate_path(path)
    
    # First check syntax
    try:
        code = read_file(path)
        syntax_valid, syntax_msg = check_syntax(code)
    except Exception as e:
        syntax_valid = False
        syntax_msg = f"Could not read file: {e}"
    
    # If syntax is invalid, skip pylint
    if not syntax_valid:
        return {
            'syntax_valid': False,
            'syntax_message': syntax_msg,
            'pylint_score': None,
            'total_issues': 1,
            'critical_issues': [syntax_msg],
            'all_issues': {},
            'recommendations': ["Fix syntax errors before proceeding with further analysis"]
        }
    
    # Run pylint analysis
    pylint_results = run_pylint(path)
    
    # Generate recommendations
    recommendations = []
    if pylint_results['score'] is not None:
        if pylint_results['score'] < 5.0:
            recommendations.append("Code quality is poor. Major refactoring recommended.")
        elif pylint_results['score'] < 7.0:
            recommendations.append("Code quality is acceptable but needs improvement.")
        elif pylint_results['score'] < 9.0:
            recommendations.append("Code quality is good with minor issues.")
        else:
            recommendations.append("Code quality is excellent!")
    
    if pylint_results['error_count'] > 0:
        recommendations.append(f"Fix {pylint_results['error_count']} error(s) immediately.")
    
    if pylint_results['convention_count'] > 5:
        recommendations.append("Consider following PEP 8 style guidelines more closely.")
    
    return {
        'syntax_valid': True,
        'syntax_message': syntax_msg,
        'pylint_score': pylint_results['score'],
        'total_issues': sum([
            pylint_results['error_count'],
            pylint_results['warning_count'],
            pylint_results['convention_count'],
            pylint_results['refactor_count']
        ]),
        'critical_issues': pylint_results['errors'],
        'all_issues': pylint_results['by_category'],
        'recommendations': recommendations
    }


# ============================================================================
# INCREMENT 3: THE JUDGE - Execution & Testing Tools
# ============================================================================

def _ensure_pytest_installed() -> bool:
    """
    Checks if pytest is installed, attempts to install if not.
    
    Returns:
        True if pytest is available, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("Pytest not found. Attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest"],
                capture_output=True,
                check=True,
                timeout=60
            )
            print("✓ Pytest installed successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to install pytest: {e}")
            return False


def run_pytest(test_file_path: str, verbose: bool = True, timeout: int = 30) -> Dict[str, Any]:
    """
    Runs pytest on a specific test file within the sandbox.
    
    Args:
        test_file_path: Path to the test file (relative to sandbox or absolute within sandbox)
        verbose: If True, runs pytest in verbose mode
        timeout: Maximum execution time in seconds (default: 30)
        
    Returns:
        Dictionary containing:
            - 'success': bool indicating if tests passed
            - 'exit_code': pytest exit code (0 = all passed, 1 = some failed, etc.)
            - 'passed': number of tests passed
            - 'failed': number of tests failed
            - 'errors': number of tests with errors
            - 'stdout': standard output from pytest
            - 'stderr': standard error from pytest
            - 'timeout': bool indicating if execution timed out
            - 'summary': brief summary message
            
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the test file doesn't exist
    """
    # Ensure pytest is available
    if not _ensure_pytest_installed():
        return {
            'success': False,
            'exit_code': -1,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'stdout': "",
            'stderr': "Pytest is not installed and could not be installed automatically",
            'timeout': False,
            'summary': "Pytest unavailable"
        }
    
    abs_path = validate_path(test_file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Test file not found: {test_file_path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {test_file_path}")
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", abs_path]
    if verbose:
        cmd.append("-v")
    cmd.extend(["--tb=short", "--no-header"])
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=SANDBOX_DIR
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        
        # Parse test results from output
        passed = len(re.findall(r'PASSED', stdout))
        failed = len(re.findall(r'FAILED', stdout))
        errors = len(re.findall(r'ERROR', stdout))
        
        # Generate summary
        if exit_code == 0:
            summary = f"All tests passed ({passed} passed)"
        elif exit_code == 1:
            summary = f"Tests failed ({passed} passed, {failed} failed, {errors} errors)"
        elif exit_code == 2:
            summary = "Test execution interrupted"
        elif exit_code == 3:
            summary = "Internal error"
        elif exit_code == 4:
            summary = "Pytest command line usage error"
        elif exit_code == 5:
            summary = "No tests collected"
        else:
            summary = f"Unknown exit code: {exit_code}"
        
        return {
            'success': exit_code == 0,
            'exit_code': exit_code,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'stdout': stdout,
            'stderr': stderr,
            'timeout': False,
            'summary': summary
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'exit_code': -1,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'stdout': "",
            'stderr': f"Test execution timed out after {timeout} seconds",
            'timeout': True,
            'summary': f"Timeout after {timeout}s"
        }
    except Exception as e:
        return {
            'success': False,
            'exit_code': -1,
            'passed': 0,
            'failed': 0,
            'errors': 1,
            'stdout': "",
            'stderr': f"Error running pytest: {str(e)}",
            'timeout': False,
            'summary': f"Execution error: {str(e)}"
        }


def run_script(script_path: str, timeout: int = 5, args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Executes a Python script within the sandbox with timeout protection.
    
    This is crucial for detecting infinite loops, crashes, or hanging code.
    The default 5-second timeout prevents the self-healing loop from getting stuck.
    
    Args:
        script_path: Path to the Python script (relative to sandbox or absolute within sandbox)
        timeout: Maximum execution time in seconds (default: 5 for quick feedback)
        args: Optional list of command-line arguments to pass to the script
        
    Returns:
        Dictionary containing:
            - 'success': bool indicating if script ran without errors
            - 'exit_code': script exit code (0 = success)
            - 'stdout': standard output from the script
            - 'stderr': standard error from the script
            - 'timeout': bool indicating if execution timed out
            - 'execution_time': actual execution time in seconds
            - 'summary': brief summary message
            
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the script doesn't exist
    """
    abs_path = validate_path(script_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {script_path}")
    
    # Build command
    cmd = [sys.executable, abs_path]
    if args:
        cmd.extend(args)
    
    import time
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=SANDBOX_DIR
        )
        
        execution_time = time.time() - start_time
        exit_code = result.returncode
        
        # Generate summary
        if exit_code == 0:
            summary = f"Success ({execution_time:.2f}s)"
        else:
            summary = f"Exit code {exit_code} ({execution_time:.2f}s)"
        
        return {
            'success': exit_code == 0,
            'exit_code': exit_code,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timeout': False,
            'execution_time': execution_time,
            'summary': summary
        }
        
    except subprocess.TimeoutExpired as e:
        execution_time = time.time() - start_time
        
        # Try to get partial output
        stdout = e.stdout.decode('utf-8') if e.stdout else ""
        stderr = e.stderr.decode('utf-8') if e.stderr else ""
        
        return {
            'success': False,
            'exit_code': -1,
            'stdout': stdout,
            'stderr': stderr + f"\n[TIMEOUT] Script exceeded {timeout}s limit - possible infinite loop",
            'timeout': True,
            'execution_time': execution_time,
            'summary': f"Timeout after {timeout}s (infinite loop?)"
        }
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            'success': False,
            'exit_code': -1,
            'stdout': "",
            'stderr': f"Error executing script: {str(e)}",
            'timeout': False,
            'execution_time': execution_time,
            'summary': f"Execution error: {str(e)}"
        }


def test_and_analyze(script_path: str, test_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Comprehensive testing: runs the script, checks syntax, analyzes quality, and runs tests.
    
    Args:
        script_path: Path to the Python script to test
        test_path: Optional path to pytest test file
        
    Returns:
        Dictionary with complete analysis including:
            - 'script_execution': results from run_script()
            - 'code_quality': results from analyze_code_quality()
            - 'tests': results from run_pytest() if test_path provided
            - 'overall_status': 'pass', 'fail', or 'timeout'
            - 'issues_found': list of all issues
            - 'recommendations': combined recommendations
    """
    results = {
        'script_execution': None,
        'code_quality': None,
        'tests': None,
        'overall_status': 'pass',
        'issues_found': [],
        'recommendations': []
    }
    
    # 1. Run the script
    try:
        script_result = run_script(script_path)
        results['script_execution'] = script_result
        
        if script_result['timeout']:
            results['overall_status'] = 'timeout'
            results['issues_found'].append("Script has infinite loop or hangs")
            results['recommendations'].append("Fix infinite loop or add proper exit conditions")
        elif not script_result['success']:
            results['overall_status'] = 'fail'
            results['issues_found'].append(f"Script failed: {script_result['stderr']}")
    except Exception as e:
        results['issues_found'].append(f"Cannot execute script: {e}")
        results['overall_status'] = 'fail'
    
    # 2. Analyze code quality
    try:
        quality = analyze_code_quality(script_path)
        results['code_quality'] = quality
        
        if not quality['syntax_valid']:
            results['overall_status'] = 'fail'
            results['issues_found'].append(f"Syntax error: {quality['syntax_message']}")
        
        if quality['critical_issues']:
            results['issues_found'].extend(quality['critical_issues'])
        
        results['recommendations'].extend(quality['recommendations'])
    except Exception as e:
        results['issues_found'].append(f"Cannot analyze quality: {e}")
    
    # 3. Run tests if provided
    if test_path:
        try:
            test_result = run_pytest(test_path)
            results['tests'] = test_result
            
            if not test_result['success']:
                results['overall_status'] = 'fail'
                results['issues_found'].append(f"Tests failed: {test_result['summary']}")
        except Exception as e:
            results['issues_found'].append(f"Cannot run tests: {e}")
    
    return results


# ============================================================================
# INCREMENT 4: THE POLISHER - Quality & Formatter
# ============================================================================

def _ensure_black_installed() -> bool:
    """
    Checks if black is installed, attempts to install if not.
    
    Returns:
        True if black is available, False otherwise
    """
    try:
        subprocess.run(
            [sys.executable, "-m", "black", "--version"],
            capture_output=True,
            check=True,
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("Black not found. Attempting to install...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "black"],
                capture_output=True,
                check=True,
                timeout=60
            )
            print("✓ Black installed successfully")
            return True
        except Exception as e:
            print(f"✗ Failed to install black: {e}")
            return False


def apply_black_formatting(path: str, line_length: int = 88, check_only: bool = False) -> Dict[str, Any]:
    """
    Applies Black code formatting to a Python file.
    
    This automatically fixes:
    - Indentation issues
    - Line length violations
    - Spacing around operators
    - Quote normalization
    - Trailing commas
    
    This is crucial for boosting Pylint scores by fixing style issues automatically.
    
    Args:
        path: Path to the Python file (relative to sandbox or absolute within sandbox)
        line_length: Maximum line length (default: 88, Black's default)
        check_only: If True, only check if file would be reformatted without changing it
        
    Returns:
        Dictionary containing:
            - 'success': bool indicating if formatting succeeded
            - 'reformatted': bool indicating if file was changed
            - 'stdout': output from Black
            - 'stderr': error messages if any
            - 'summary': brief summary message
            
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the file doesn't exist
    """
    # Ensure black is available
    if not _ensure_black_installed():
        return {
            'success': False,
            'reformatted': False,
            'stdout': "",
            'stderr': "Black is not installed and could not be installed automatically",
            'summary': "Black unavailable"
        }
    
    abs_path = validate_path(path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {path}")
    
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {path}")
    
    # Build black command
    cmd = [sys.executable, "-m", "black", abs_path, f"--line-length={line_length}"]
    if check_only:
        cmd.append("--check")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        
        # Exit code 0 = file was already formatted or successfully reformatted
        # Exit code 1 = file would be reformatted (when using --check)
        # Other codes = errors
        
        if check_only:
            reformatted = exit_code == 1
            success = exit_code in [0, 1]
            if exit_code == 0:
                summary = "File already formatted"
            elif exit_code == 1:
                summary = "File would be reformatted"
            else:
                summary = "Error checking format"
        else:
            reformatted = "reformatted" in stdout.lower()
            success = exit_code == 0
            if reformatted:
                summary = "File reformatted successfully"
            else:
                summary = "File already formatted" if success else "Formatting failed"
        
        return {
            'success': success,
            'reformatted': reformatted,
            'stdout': stdout,
            'stderr': stderr,
            'summary': summary
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'reformatted': False,
            'stdout': "",
            'stderr': "Black formatting timed out",
            'summary': "Timeout"
        }
    except Exception as e:
        return {
            'success': False,
            'reformatted': False,
            'stdout': "",
            'stderr': f"Error running black: {str(e)}",
            'summary': f"Error: {str(e)}"
        }


def get_project_structure(base_path: str = "", max_depth: int = 5, show_hidden: bool = False) -> str:
    """
    Returns a pretty tree representation of the sandbox directory structure.
    
    This helps the AI agent understand the project context and file organization.
    
    Args:
        base_path: Optional subdirectory within sandbox (default: root of sandbox)
        max_depth: Maximum depth to traverse (default: 5)
        show_hidden: Whether to show hidden files/folders (default: False)
        
    Returns:
        String representation of the directory tree
        
    Raises:
        ValueError: If the path is outside the sandbox
        FileNotFoundError: If the directory doesn't exist
    """
    if base_path:
        abs_path = validate_path(base_path)
    else:
        abs_path = SANDBOX_DIR
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Directory not found: {base_path}")
    
    if not os.path.isdir(abs_path):
        raise ValueError(f"Path is not a directory: {base_path}")
    
    def _build_tree(directory: str, prefix: str = "", depth: int = 0) -> List[str]:
        """Recursively build tree structure."""
        if depth > max_depth:
            return []
        
        lines = []
        try:
            entries = sorted(os.listdir(directory))
            
            # Filter hidden files if needed
            if not show_hidden:
                entries = [e for e in entries if not e.startswith('.')]
            
            # Separate directories and files
            dirs = [e for e in entries if os.path.isdir(os.path.join(directory, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(directory, e))]
            
            # Combine: directories first, then files
            all_entries = dirs + files
            
            for i, entry in enumerate(all_entries):
                is_last = i == len(all_entries) - 1
                entry_path = os.path.join(directory, entry)
                
                # Choose the right tree characters
                if is_last:
                    current = "└── "
                    extension = "    "
                else:
                    current = "├── "
                    extension = "│   "
                
                # Add file/folder indicator
                if os.path.isdir(entry_path):
                    display_name = f"📁 {entry}/"
                else:
                    # Add file type indicator
                    if entry.endswith('.py'):
                        display_name = f"🐍 {entry}"
                    elif entry.endswith(('.txt', '.md', '.rst')):
                        display_name = f"📄 {entry}"
                    elif entry.endswith(('.json', '.yaml', '.yml', '.toml')):
                        display_name = f"⚙️ {entry}"
                    else:
                        display_name = f"📄 {entry}"
                
                lines.append(f"{prefix}{current}{display_name}")
                
                # Recurse for directories
                if os.path.isdir(entry_path):
                    lines.extend(_build_tree(entry_path, prefix + extension, depth + 1))
        
        except PermissionError:
            lines.append(f"{prefix}[Permission Denied]")
        
        return lines
    
    # Build the tree
    tree_lines = [f"📦 {os.path.basename(abs_path) or 'sandbox'}/"]
    tree_lines.extend(_build_tree(abs_path))
    
    return "\n".join(tree_lines)


def format_and_analyze(path: str) -> Dict[str, Any]:
    """
    Comprehensive code improvement: format with Black, then analyze quality.
    
    This is the recommended workflow for improving code quality:
    1. Auto-format with Black to fix style issues
    2. Analyze with Pylint to check for remaining issues
    
    Args:
        path: Path to the Python file
        
    Returns:
        Dictionary with:
            - 'formatting': results from apply_black_formatting()
            - 'analysis_before': quality analysis before formatting (if check_only used)
            - 'analysis_after': quality analysis after formatting
            - 'improvement': score improvement (if before analysis available)
            - 'recommendations': what to do next
    """
    results = {
        'formatting': None,
        'analysis_before': None,
        'analysis_after': None,
        'improvement': None,
        'recommendations': []
    }
    
    # Get initial quality score
    try:
        initial_analysis = analyze_code_quality(path)
        results['analysis_before'] = initial_analysis
        initial_score = initial_analysis.get('pylint_score')
    except Exception:
        initial_score = None
    
    # Apply Black formatting
    try:
        format_result = apply_black_formatting(path)
        results['formatting'] = format_result
        
        if not format_result['success']:
            results['recommendations'].append("Fix formatting errors manually")
            return results
        
        if format_result['reformatted']:
            results['recommendations'].append("✓ Code auto-formatted with Black")
    except Exception as e:
        results['recommendations'].append(f"Could not format: {e}")
        return results
    
    # Analyze after formatting
    try:
        final_analysis = analyze_code_quality(path)
        results['analysis_after'] = final_analysis
        final_score = final_analysis.get('pylint_score')
        
        # Calculate improvement
        if initial_score is not None and final_score is not None:
            improvement = final_score - initial_score
            results['improvement'] = improvement
            
            if improvement > 0:
                results['recommendations'].append(f"✓ Quality improved by {improvement:.2f} points!")
            elif improvement < 0:
                results['recommendations'].append(f"⚠ Quality decreased by {abs(improvement):.2f} points")
            else:
                results['recommendations'].append("Quality score unchanged")
        
        # Add remaining recommendations
        if final_analysis.get('critical_issues'):
            results['recommendations'].append(f"Fix {len(final_analysis['critical_issues'])} critical issues")
        
        if final_score is not None and final_score < 8.0:
            results['recommendations'].append("Consider refactoring for better quality")
    
    except Exception as e:
        results['recommendations'].append(f"Could not analyze: {e}")
    
    return results


# ============================================================================
# INCREMENT 5: THE TIME MACHINE - Backup & Restore
# ============================================================================

def backup_sandbox(backup_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Creates a backup of the entire sandbox directory.
    
    This is crucial for the self-healing loop: if an agent breaks code,
    we can restore to a previous working state.
    
    Args:
        backup_name: Optional custom backup name (default: timestamp-based)
        
    Returns:
        Dictionary containing:
            - 'success': bool indicating if backup succeeded
            - 'backup_path': path to the backup
            - 'files_backed_up': number of files backed up
            - 'size_bytes': total size of backup
            - 'timestamp': backup creation timestamp
            - 'summary': brief summary message
    """
    try:
        # Create backup directory if it doesn't exist
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Generate backup name with timestamp
        if backup_name is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Check if sandbox exists
        if not os.path.exists(SANDBOX_DIR):
            return {
                'success': False,
                'backup_path': None,
                'files_backed_up': 0,
                'size_bytes': 0,
                'timestamp': time.time(),
                'summary': "Sandbox directory does not exist"
            }
        
        # Remove existing backup with same name if it exists
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
        
        # Copy the entire sandbox directory
        shutil.copytree(SANDBOX_DIR, backup_path, symlinks=False)
        
        # Count files and calculate size
        files_backed_up = 0
        size_bytes = 0
        for root, dirs, files in os.walk(backup_path):
            files_backed_up += len(files)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size_bytes += os.path.getsize(file_path)
                except OSError:
                    pass
        
        return {
            'success': True,
            'backup_path': backup_path,
            'files_backed_up': files_backed_up,
            'size_bytes': size_bytes,
            'timestamp': time.time(),
            'summary': f"Backup created: {files_backed_up} files, {size_bytes / 1024:.2f} KB"
        }
        
    except PermissionError as e:
        return {
            'success': False,
            'backup_path': None,
            'files_backed_up': 0,
            'size_bytes': 0,
            'timestamp': time.time(),
            'summary': f"Permission denied: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'backup_path': None,
            'files_backed_up': 0,
            'size_bytes': 0,
            'timestamp': time.time(),
            'summary': f"Backup failed: {str(e)}"
        }


def restore_sandbox(backup_name: Optional[str] = None, confirm: bool = True) -> Dict[str, Any]:
    """
    Restores the sandbox from a backup.
    
    WARNING: This DELETES the current sandbox and replaces it with the backup!
    
    Args:
        backup_name: Name of backup to restore (default: most recent)
        confirm: Safety check - must be False to actually restore (prevents accidents)
        
    Returns:
        Dictionary containing:
            - 'success': bool indicating if restore succeeded
            - 'backup_used': path to the backup that was restored
            - 'files_restored': number of files restored
            - 'summary': brief summary message
    """
    # Safety check
    if confirm:
        return {
            'success': False,
            'backup_used': None,
            'files_restored': 0,
            'summary': "Restore aborted: set confirm=False to actually restore"
        }
    
    try:
        # Check if backup directory exists
        if not os.path.exists(BACKUP_DIR):
            return {
                'success': False,
                'backup_used': None,
                'files_restored': 0,
                'summary': "No backups found - backup directory does not exist"
            }
        
        # Find the backup to restore
        if backup_name is None:
            # Get most recent backup
            backups = [d for d in os.listdir(BACKUP_DIR) 
                      if os.path.isdir(os.path.join(BACKUP_DIR, d))]
            
            if not backups:
                return {
                    'success': False,
                    'backup_used': None,
                    'files_restored': 0,
                    'summary': "No backups found"
                }
            
            # Sort by modification time (most recent first)
            backups.sort(key=lambda x: os.path.getmtime(os.path.join(BACKUP_DIR, x)), reverse=True)
            backup_name = backups[0]
        
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Verify backup exists
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'backup_used': None,
                'files_restored': 0,
                'summary': f"Backup '{backup_name}' not found"
            }
        
        # Delete current sandbox
        if os.path.exists(SANDBOX_DIR):
            shutil.rmtree(SANDBOX_DIR)
        
        # Restore from backup
        shutil.copytree(backup_path, SANDBOX_DIR, symlinks=False)
        
        # Count restored files
        files_restored = 0
        for root, dirs, files in os.walk(SANDBOX_DIR):
            files_restored += len(files)
        
        return {
            'success': True,
            'backup_used': backup_path,
            'files_restored': files_restored,
            'summary': f"Restored {files_restored} files from '{backup_name}'"
        }
        
    except PermissionError as e:
        return {
            'success': False,
            'backup_used': None,
            'files_restored': 0,
            'summary': f"Permission denied: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'backup_used': None,
            'files_restored': 0,
            'summary': f"Restore failed: {str(e)}"
        }


def list_backups() -> Dict[str, Any]:
    """
    Lists all available backups with metadata.
    
    Returns:
        Dictionary containing:
            - 'success': bool indicating if listing succeeded
            - 'backups': list of backup info dicts
            - 'total_backups': number of backups available
            - 'total_size_bytes': total size of all backups
    """
    try:
        if not os.path.exists(BACKUP_DIR):
            return {
                'success': True,
                'backups': [],
                'total_backups': 0,
                'total_size_bytes': 0
            }
        
        backups_info = []
        total_size = 0
        
        for backup_name in os.listdir(BACKUP_DIR):
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            
            if not os.path.isdir(backup_path):
                continue
            
            # Get metadata
            mtime = os.path.getmtime(backup_path)
            
            # Count files and size
            file_count = 0
            size_bytes = 0
            for root, dirs, files in os.walk(backup_path):
                file_count += len(files)
                for file in files:
                    try:
                        size_bytes += os.path.getsize(os.path.join(root, file))
                    except OSError:
                        pass
            
            total_size += size_bytes
            
            backups_info.append({
                'name': backup_name,
                'path': backup_path,
                'created': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
                'timestamp': mtime,
                'files': file_count,
                'size_bytes': size_bytes,
                'size_mb': size_bytes / (1024 * 1024)
            })
        
        # Sort by timestamp (most recent first)
        backups_info.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'success': True,
            'backups': backups_info,
            'total_backups': len(backups_info),
            'total_size_bytes': total_size
        }
        
    except Exception as e:
        return {
            'success': False,
            'backups': [],
            'total_backups': 0,
            'total_size_bytes': 0,
            'error': str(e)
        }


def delete_backup(backup_name: str) -> Dict[str, Any]:
    """
    Deletes a specific backup.
    
    Args:
        backup_name: Name of the backup to delete
        
    Returns:
        Dictionary with success status and summary
    """
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'summary': f"Backup '{backup_name}' not found"
            }
        
        shutil.rmtree(backup_path)
        
        return {
            'success': True,
            'summary': f"Deleted backup '{backup_name}'"
        }
        
    except Exception as e:
        return {
            'success': False,
            'summary': f"Failed to delete backup: {str(e)}"
        }


# ============================================================================
# INCREMENT 7: THE MANUAL GENERATOR - Self-Documentation for Prompt Engineers
# ============================================================================

def get_tools_documentation(format_type: str = 'detailed', category: str = None) -> str:
    """
    Generate comprehensive documentation for all available tools.
    
    This function inspects TOOLS_MAPPING and generates formatted documentation
    that can be used in LLM system prompts. The Prompt Engineer can call this
    to get the exact tool specifications without manually writing them.
    
    Args:
        format_type: Documentation format ('detailed', 'compact', 'json', 'markdown')
            - 'detailed': Full documentation with descriptions and examples
            - 'compact': Brief listing with just signatures
            - 'json': Machine-readable JSON format
            - 'markdown': Markdown-formatted documentation
        category: Optional category filter (filesystem, analysis, execution, formatting, backup, meta)
    
    Returns:
        Formatted string containing tool documentation
        
    Example:
        # For system prompt
        system_prompt = f"You have access to these tools:\n{get_tools_documentation()}"
        
        # Get just filesystem tools
        fs_docs = get_tools_documentation(category='filesystem')
    """
    # Filter tools by category if specified
    if category:
        tools_to_document = {
            name: func for name, func in TOOLS_MAPPING.items()
            if TOOLS_METADATA.get(name, {}).get('category') == category
        }
    else:
        tools_to_document = TOOLS_MAPPING
    
    if format_type == 'json':
        return _generate_json_documentation(tools_to_document)
    elif format_type == 'compact':
        return _generate_compact_documentation(tools_to_document)
    elif format_type == 'markdown':
        return _generate_markdown_documentation(tools_to_document)
    else:  # detailed (default)
        return _generate_detailed_documentation(tools_to_document)


def _generate_detailed_documentation(tools: Dict[str, Callable]) -> str:
    """Generate detailed text documentation for tools."""
    lines = []
    lines.append("=" * 80)
    lines.append("AVAILABLE TOOLS DOCUMENTATION")
    lines.append("=" * 80)
    lines.append(f"\nTotal Tools: {len(tools)}")
    
    # Group by category
    categories = {}
    for tool_name in tools:
        metadata = TOOLS_METADATA.get(tool_name, {})
        cat = metadata.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool_name)
    
    lines.append(f"Categories: {', '.join(sorted(categories.keys()))}")
    lines.append("")
    
    # Document each category
    for category in sorted(categories.keys()):
        lines.append("-" * 80)
        lines.append(f"CATEGORY: {category.upper()}")
        lines.append("-" * 80)
        lines.append("")
        
        for tool_name in sorted(categories[category]):
            tool_func = tools[tool_name]
            metadata = TOOLS_METADATA.get(tool_name, {})
            
            # Tool header
            lines.append(f"Tool: {tool_name}")
            lines.append(f"Description: {metadata.get('description', 'No description')}")
            
            # Get function signature
            sig = inspect.signature(tool_func)
            params = []
            for param_name, param in sig.parameters.items():
                if param.default == inspect.Parameter.empty:
                    params.append(f"{param_name}")
                else:
                    params.append(f"{param_name}={repr(param.default)}")
            
            lines.append(f"Signature: {tool_name}({', '.join(params)})")
            
            # Required and optional arguments
            required = metadata.get('required_args', [])
            optional = metadata.get('optional_args', [])
            
            if required:
                lines.append(f"Required Arguments: {', '.join(required)}")
            if optional:
                lines.append(f"Optional Arguments: {', '.join(optional)}")
            
            # Docstring
            docstring = inspect.getdoc(tool_func)
            if docstring:
                lines.append("\nDocumentation:")
                for line in docstring.split('\n'):
                    lines.append(f"  {line}")
            
            lines.append("")
    
    lines.append("=" * 80)
    return '\n'.join(lines)


def _generate_compact_documentation(tools: Dict[str, Callable]) -> str:
    """Generate compact one-line documentation for tools."""
    lines = []
    lines.append("TOOLS QUICK REFERENCE")
    lines.append("=" * 80)
    
    # Group by category
    categories = {}
    for tool_name in tools:
        metadata = TOOLS_METADATA.get(tool_name, {})
        cat = metadata.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool_name)
    
    for category in sorted(categories.keys()):
        lines.append(f"\n{category.upper()}:")
        for tool_name in sorted(categories[category]):
            metadata = TOOLS_METADATA.get(tool_name, {})
            required = metadata.get('required_args', [])
            optional = metadata.get('optional_args', [])
            
            args_str = ', '.join(required)
            if optional:
                args_str += f" [, {', '.join(optional)}]"
            
            desc = metadata.get('description', 'No description')
            lines.append(f"  • {tool_name}({args_str})")
            lines.append(f"    {desc}")
    
    return '\n'.join(lines)


def _generate_json_documentation(tools: Dict[str, Callable]) -> str:
    """Generate JSON documentation for tools."""
    docs = {}
    
    for tool_name, tool_func in tools.items():
        metadata = TOOLS_METADATA.get(tool_name, {})
        
        # Get function signature details
        sig = inspect.signature(tool_func)
        parameters = {}
        
        for param_name, param in sig.parameters.items():
            param_info = {
                'required': param.default == inspect.Parameter.empty,
                'default': None if param.default == inspect.Parameter.empty else repr(param.default)
            }
            
            # Try to get type annotation
            if param.annotation != inspect.Parameter.empty:
                param_info['type'] = str(param.annotation)
            
            parameters[param_name] = param_info
        
        docs[tool_name] = {
            'description': metadata.get('description', 'No description'),
            'category': metadata.get('category', 'uncategorized'),
            'required_args': metadata.get('required_args', []),
            'optional_args': metadata.get('optional_args', []),
            'parameters': parameters,
            'docstring': inspect.getdoc(tool_func)
        }
    
    return json.dumps(docs, indent=2)


def _generate_markdown_documentation(tools: Dict[str, Callable]) -> str:
    """Generate Markdown documentation for tools."""
    lines = []
    lines.append("# Tools Documentation\n")
    lines.append(f"**Total Tools:** {len(tools)}\n")
    
    # Group by category
    categories = {}
    for tool_name in tools:
        metadata = TOOLS_METADATA.get(tool_name, {})
        cat = metadata.get('category', 'uncategorized')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(tool_name)
    
    # Document each category
    for category in sorted(categories.keys()):
        lines.append(f"\n## {category.upper()}\n")
        
        for tool_name in sorted(categories[category]):
            tool_func = tools[tool_name]
            metadata = TOOLS_METADATA.get(tool_name, {})
            
            lines.append(f"### `{tool_name}()`\n")
            lines.append(f"**Description:** {metadata.get('description', 'No description')}\n")
            
            # Arguments
            required = metadata.get('required_args', [])
            optional = metadata.get('optional_args', [])
            
            if required or optional:
                lines.append("**Arguments:**")
                for arg in required:
                    lines.append(f"- `{arg}` (required)")
                for arg in optional:
                    lines.append(f"- `{arg}` (optional)")
                lines.append("")
            
            # Docstring as code block
            docstring = inspect.getdoc(tool_func)
            if docstring:
                lines.append("**Details:**")
                lines.append("```")
                lines.append(docstring)
                lines.append("```\n")
    
    return '\n'.join(lines)


# ============================================================================
# INCREMENT 6: THE DISPATCHER - Unified Tool Entry Point
# ============================================================================

# Master dictionary mapping tool names to functions
TOOLS_MAPPING: Dict[str, Callable] = {
    # Increment 1: Fortress (Secure File System)
    'read_file': read_file,
    'write_file': write_file,
    'list_files': list_files,
    'validate_path': validate_path,
    
    # Increment 2: Inspector (Smart Analysis)
    'check_syntax': check_syntax,
    'run_pylint': run_pylint,
    'analyze_code_quality': analyze_code_quality,
    
    # Increment 3: Judge (Execution & Testing)
    'run_script': run_script,
    'run_pytest': run_pytest,
    'test_and_analyze': test_and_analyze,
    
    # Increment 4: Polisher (Quality & Formatter)
    'apply_black_formatting': apply_black_formatting,
    'get_project_structure': get_project_structure,
    'format_and_analyze': format_and_analyze,
    
    # Increment 5: Time Machine (Backup & Restore)
    'backup_sandbox': backup_sandbox,
    'restore_sandbox': restore_sandbox,
    'list_backups': list_backups,
    'delete_backup': delete_backup,
    
    # Increment 7: Manual Generator (Self-Documentation)
    'get_tools_documentation': get_tools_documentation,
}

# Tool metadata for documentation and validation
TOOLS_METADATA: Dict[str, Dict[str, Any]] = {
    'read_file': {
        'description': 'Read contents of a file within the sandbox',
        'category': 'filesystem',
        'required_args': ['path'],
        'optional_args': [],
    },
    'write_file': {
        'description': 'Write content to a file within the sandbox',
        'category': 'filesystem',
        'required_args': ['path', 'content'],
        'optional_args': [],
    },
    'list_files': {
        'description': 'List all files in the sandbox recursively',
        'category': 'filesystem',
        'required_args': [],
        'optional_args': ['path'],
    },
    'validate_path': {
        'description': 'Validate that a path is within the sandbox',
        'category': 'filesystem',
        'required_args': ['path'],
        'optional_args': [],
    },
    'check_syntax': {
        'description': 'Check Python syntax without executing code',
        'category': 'analysis',
        'required_args': ['code_string'],
        'optional_args': [],
    },
    'run_pylint': {
        'description': 'Run pylint analysis on a Python file',
        'category': 'analysis',
        'required_args': ['path'],
        'optional_args': ['return_full_report'],
    },
    'analyze_code_quality': {
        'description': 'Comprehensive code quality analysis (syntax + pylint)',
        'category': 'analysis',
        'required_args': ['path'],
        'optional_args': [],
    },
    'run_script': {
        'description': 'Execute a Python script with timeout protection',
        'category': 'execution',
        'required_args': ['script_path'],
        'optional_args': ['timeout', 'args'],
    },
    'run_pytest': {
        'description': 'Run pytest on a test file',
        'category': 'execution',
        'required_args': ['test_file_path'],
        'optional_args': ['verbose', 'timeout'],
    },
    'test_and_analyze': {
        'description': 'Comprehensive testing: run script, check quality, run tests',
        'category': 'execution',
        'required_args': ['script_path'],
        'optional_args': ['test_path'],
    },
    'apply_black_formatting': {
        'description': 'Format Python code using Black',
        'category': 'formatting',
        'required_args': ['path'],
        'optional_args': ['line_length', 'check_only'],
    },
    'get_project_structure': {
        'description': 'Get a tree view of the sandbox directory structure',
        'category': 'formatting',
        'required_args': [],
        'optional_args': ['base_path', 'max_depth', 'show_hidden'],
    },
    'format_and_analyze': {
        'description': 'Format with Black then analyze quality',
        'category': 'formatting',
        'required_args': ['path'],
        'optional_args': [],
    },
    'backup_sandbox': {
        'description': 'Create a backup of the entire sandbox',
        'category': 'backup',
        'required_args': [],
        'optional_args': ['backup_name'],
    },
    'restore_sandbox': {
        'description': 'Restore sandbox from a backup',
        'category': 'backup',
        'required_args': [],
        'optional_args': ['backup_name', 'confirm'],
    },
    'list_backups': {
        'description': 'List all available backups with metadata',
        'category': 'backup',
        'required_args': [],
        'optional_args': [],
    },
    'delete_backup': {
        'description': 'Delete a specific backup',
        'category': 'backup',
        'required_args': ['backup_name'],
        'optional_args': [],
    },
    'get_tools_documentation': {
        'description': 'Generate comprehensive documentation for all available tools',
        'category': 'meta',
        'required_args': [],
        'optional_args': ['format_type', 'category'],
    },
}


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Master function to execute any tool by name with error handling.
    
    This is the SINGLE ENTRY POINT for the orchestrator to call tools.
    Prevents crashes from hallucinated tool names or invalid arguments.
    
    Args:
        tool_name: Name of the tool to execute
        **kwargs: Arguments to pass to the tool
        
    Returns:
        Dictionary with standardized output:
            - 'status': 'success' or 'error'
            - 'tool': name of the tool executed
            - 'output': result from the tool (if success)
            - 'error': error message (if error)
            - 'error_type': type of error (if error)
            
    Examples:
        >>> execute_tool('read_file', path='test.txt')
        {'status': 'success', 'tool': 'read_file', 'output': 'file contents...'}
        
        >>> execute_tool('fake_tool', arg='value')
        {'status': 'error', 'tool': 'fake_tool', 'error': '...', 'error_type': 'ToolNotFoundError'}
    """
    # Check if tool exists
    if tool_name not in TOOLS_MAPPING:
        return {
            'status': 'error',
            'tool': tool_name,
            'error': f"Tool '{tool_name}' not found. Available tools: {', '.join(list_available_tools())}",
            'error_type': 'ToolNotFoundError',
            'output': None
        }
    
    try:
        # Get the function
        tool_function = TOOLS_MAPPING[tool_name]
        
        # Execute with error handling
        try:
            result = tool_function(**kwargs)
            
            return {
                'status': 'success',
                'tool': tool_name,
                'output': result,
                'error': None,
                'error_type': None
            }
            
        except TypeError as e:
            # Invalid arguments
            sig = inspect.signature(tool_function)
            params = list(sig.parameters.keys())
            
            return {
                'status': 'error',
                'tool': tool_name,
                'error': f"Invalid arguments for '{tool_name}': {str(e)}. Expected parameters: {params}",
                'error_type': 'InvalidArgumentsError',
                'output': None
            }
            
        except FileNotFoundError as e:
            return {
                'status': 'error',
                'tool': tool_name,
                'error': f"File not found: {str(e)}",
                'error_type': 'FileNotFoundError',
                'output': None
            }
            
        except ValueError as e:
            return {
                'status': 'error',
                'tool': tool_name,
                'error': f"Invalid value: {str(e)}",
                'error_type': 'ValueError',
                'output': None
            }
            
        except PermissionError as e:
            return {
                'status': 'error',
                'tool': tool_name,
                'error': f"Permission denied: {str(e)}",
                'error_type': 'PermissionError',
                'output': None
            }
            
        except Exception as e:
            # Catch-all for any other errors
            return {
                'status': 'error',
                'tool': tool_name,
                'error': f"Unexpected error: {type(e).__name__}: {str(e)}",
                'error_type': type(e).__name__,
                'output': None
            }
            
    except Exception as e:
        # This catches errors in the dispatcher itself
        return {
            'status': 'error',
            'tool': tool_name,
            'error': f"Dispatcher error: {str(e)}",
            'error_type': 'DispatcherError',
            'output': None
        }


def list_available_tools(category: Optional[str] = None) -> List[str]:
    """
    List all available tools, optionally filtered by category.
    
    Args:
        category: Optional category filter ('filesystem', 'analysis', 'execution', 'formatting', 'backup')
        
    Returns:
        List of tool names
    """
    if category is None:
        return sorted(TOOLS_MAPPING.keys())
    
    # Filter by category
    tools = [
        name for name, meta in TOOLS_METADATA.items()
        if meta.get('category') == category
    ]
    return sorted(tools)


def get_tool_info(tool_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific tool.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Dictionary with tool metadata including description, arguments, and signature
    """
    if tool_name not in TOOLS_MAPPING:
        return {
            'exists': False,
            'error': f"Tool '{tool_name}' not found"
        }
    
    tool_function = TOOLS_MAPPING[tool_name]
    metadata = TOOLS_METADATA.get(tool_name, {})
    
    # Get function signature
    sig = inspect.signature(tool_function)
    params = {}
    for param_name, param in sig.parameters.items():
        params[param_name] = {
            'default': None if param.default == inspect.Parameter.empty else param.default,
            'annotation': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'Any',
            'required': param.default == inspect.Parameter.empty
        }
    
    return {
        'exists': True,
        'name': tool_name,
        'description': metadata.get('description', 'No description available'),
        'category': metadata.get('category', 'unknown'),
        'parameters': params,
        'required_args': metadata.get('required_args', []),
        'optional_args': metadata.get('optional_args', []),
        'docstring': tool_function.__doc__
    }


def get_tools_by_category() -> Dict[str, List[str]]:
    """
    Get all tools organized by category.
    
    Returns:
        Dictionary mapping categories to lists of tool names
    """
    categories: Dict[str, List[str]] = {}
    
    for tool_name, metadata in TOOLS_METADATA.items():
        category = metadata.get('category', 'other')
        if category not in categories:
            categories[category] = []
        categories[category].append(tool_name)
    
    # Sort tools within each category
    for category in categories:
        categories[category].sort()
    
    return categories


def validate_tool_call(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Validate a tool call without executing it.
    
    Useful for LLMs to check if their planned tool call is valid before executing.
    
    Args:
        tool_name: Name of the tool
        **kwargs: Arguments for the tool
        
    Returns:
        Dictionary with validation results
    """
    # Check if tool exists
    if tool_name not in TOOLS_MAPPING:
        return {
            'valid': False,
            'error': f"Tool '{tool_name}' does not exist",
            'suggestions': list_available_tools()
        }
    
    tool_function = TOOLS_MAPPING[tool_name]
    metadata = TOOLS_METADATA.get(tool_name, {})
    
    # Check required arguments
    required_args = metadata.get('required_args', [])
    missing_args = [arg for arg in required_args if arg not in kwargs]
    
    if missing_args:
        return {
            'valid': False,
            'error': f"Missing required arguments: {missing_args}",
            'required': required_args,
            'provided': list(kwargs.keys())
        }
    
    # Get function signature for additional validation
    sig = inspect.signature(tool_function)
    try:
        sig.bind(**kwargs)
        return {
            'valid': True,
            'tool': tool_name,
            'arguments': kwargs
        }
    except TypeError as e:
        return {
            'valid': False,
            'error': f"Argument validation failed: {str(e)}",
            'expected_parameters': list(sig.parameters.keys())
        }


if __name__ == "__main__":
    # Quick test
    print(f"Sandbox directory: {SANDBOX_DIR}")
    print(f"Backup directory: {BACKUP_DIR}")
    print(f"Files in sandbox: {list_files()}")
    print(f"\nAvailable tools: {len(TOOLS_MAPPING)}")
    print(f"Categories: {list(get_tools_by_category().keys())}")

