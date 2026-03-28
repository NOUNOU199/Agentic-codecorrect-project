"""
FEATURE 3: main.py - Mandatory Entry Point
Implements the official entry point for automated evaluation.

Usage:
    python main.py --target_dir "./sandbox/dataset_inconnu"

Requirements (from official documents):
- Parse --target_dir argument
- Validate directory existence
- Launch orchestration
- Exit cleanly
"""

import argparse
import sys
from pathlib import Path


def parse_arguments():
    """Parse command-line arguments as specified in official documents"""
    parser = argparse.ArgumentParser(
        description='The Refactoring Swarm - Multi-agent code refactoring system'
    )
    
    parser.add_argument(
        '--target_dir',
        type=str,
        required=True,
        help='Target directory containing Python code to refactor'
    )
    
    return parser.parse_args()


def validate_target_directory(target_dir: str) -> bool:
    """Validate that target directory exists"""
    path = Path(target_dir)
    
    if not path.exists():
        print(f"ERROR: Target directory does not exist: {target_dir}", file=sys.stderr)
        return False
    
    if not path.is_dir():
        print(f"ERROR: Target path is not a directory: {target_dir}", file=sys.stderr)
        return False
    
    return True


def main():
    """Main entry point for The Refactoring Swarm"""
    try:
        # Parse arguments
        args = parse_arguments()
        target_dir = args.target_dir
        
        # Validate directory
        if not validate_target_directory(target_dir):
            sys.exit(1)
        
        # Import orchestration components
        from src.orchestration.orchestrator import Orchestrator
        from src.agents.auditor_agent import AuditorAgent
        from src.agents.fixer_agent import FixerAgent
        from src.agents.judge_agent import JudgeAgent
        
        # Initialize agents
        auditor = AuditorAgent()
        fixer = FixerAgent()
        judge = JudgeAgent()
        
        # Create orchestrator
        orchestrator = Orchestrator(
            auditor=auditor,
            fixer=fixer,
            judge=judge
        )
        
        # Execute refactoring workflow
        print(f"Starting refactoring workflow on: {target_dir}")
        result = orchestrator.run(target_directory=target_dir)
        
        # Output result
        print(f"\nRefactoring Status: {result.get('status')}")
        print(f"Total Iterations: {result.get('iterations', 'N/A')}")
        
        if result.get('status') == 'SUCCESS':
            print("✓ Refactoring completed successfully")
            sys.exit(0)
        else:
            print(f"✗ Refactoring failed or incomplete")
            if result.get('message'):
                print(f"  Reason: {result.get('message')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nRefactoring interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()