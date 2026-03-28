"""
Pytest Runner Utility
Executes tests on target code and captures results.
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


class PytestRunner:
    """Utility for running pytest and parsing test results."""

    def __init__(self, target_dir: str):
        """
        Initialize pytest runner with target directory.
        
        Args:
            target_dir: Path to directory containing code to test
        """
        self.target_dir = Path(target_dir)

    def run_tests(self, test_file: str = None) -> Dict:
        """
        Run pytest on target code.
        
        Args:
            test_file: Optional specific test file to run (relative path).
                      If None, runs all tests in target_dir.
            
        Returns:
            Dict with keys:
                - success (bool): Whether pytest ran successfully
                - passed (int): Number of tests passed
                - failed (int): Number of tests failed
                - errors (int): Number of test errors
                - messages (list): Test output lines
                - raw_output (str): Full pytest output
        """
        if test_file:
            target_path = self.target_dir / test_file
            if not target_path.exists():
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "errors": 1,
                    "messages": [f"Test file not found: {test_file}"],
                    "raw_output": ""
                }
        else:
            target_path = self.target_dir

        try:
            # Run pytest with JSON output
            result = subprocess.run(
                ["pytest", str(target_path), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output_lines = result.stdout.split('\n') if result.stdout else []
            
            # Parse summary line (e.g., "5 passed, 2 failed in 0.42s")
            passed = failed = errors = 0
            for line in output_lines:
                if " passed" in line:
                    try:
                        passed = int(line.split(" passed")[0].strip().split()[-1])
                    except (ValueError, IndexError):
                        pass
                if " failed" in line:
                    try:
                        failed = int(line.split(" failed")[0].strip().split()[-1])
                    except (ValueError, IndexError):
                        pass
                if " error" in line:
                    try:
                        errors = int(line.split(" error")[0].strip().split()[-1])
                    except (ValueError, IndexError):
                        pass
            
            return {
                "success": result.returncode == 0,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "messages": output_lines,
                "raw_output": result.stdout + result.stderr
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "messages": ["Pytest execution timed out"],
                "raw_output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": 1,
                "messages": [str(e)],
                "raw_output": ""
            }

    def run_on_file(self, relative_path: str) -> Dict:
        """
        Run pytest on code file (expects pytest to be installed).
        
        Args:
            relative_path: Path to Python file relative to target_dir
            
        Returns:
            Dict with test results
        """
        return self.run_tests(relative_path)

    def summarize_results(self, test_results: Dict) -> Dict:
        """
        Create summary of test results.
        
        Args:
            test_results: Output from run_tests()
            
        Returns:
            Dict with summary statistics
        """
        total = test_results.get("passed", 0) + test_results.get("failed", 0)
        pass_rate = (test_results.get("passed", 0) / total * 100) if total > 0 else 0
        
        return {
            "total_tests": total,
            "passed": test_results.get("passed", 0),
            "failed": test_results.get("failed", 0),
            "errors": test_results.get("errors", 0),
            "pass_rate": pass_rate,
            "success": test_results.get("success", False)
        }
