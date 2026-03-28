"""
Quick demo showing the structured analysis output from the Inspector.
"""

import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import check_syntax, run_pylint, analyze_code_quality, write_file

print("=" * 70)
print("INSPECTOR DEMO - Structured Analysis Output")
print("=" * 70)

# Create a sample file with various issues
sample_code = """
import os

def calculate(x,y,z):
    result=x+y+z
    temp=result*2
    return temp

def unused_function():
    pass

x=calculate(1,2,3)
print(x)
"""

write_file("demo_analysis.py", sample_code)
print("\n📝 Sample code created in sandbox/demo_analysis.py\n")

# Run comprehensive analysis
print("🔍 Running comprehensive analysis...\n")
analysis = analyze_code_quality("demo_analysis.py")

print("📊 STRUCTURED ANALYSIS RESULTS:")
print("-" * 70)
print(json.dumps(analysis, indent=2, default=str))

print("\n" + "=" * 70)
print("💡 KEY INSIGHTS:")
print("-" * 70)
print(f"✓ Syntax Check: {'PASSED' if analysis['syntax_valid'] else 'FAILED'}")
print(f"✓ Code Quality Score: {analysis['pylint_score']}/10")
print(f"✓ Total Issues Found: {analysis['total_issues']}")
print(f"✓ Critical Issues: {len(analysis['critical_issues'])}")

print("\n🎯 RECOMMENDATIONS:")
for i, rec in enumerate(analysis['recommendations'], 1):
    print(f"  {i}. {rec}")

print("\n📋 ISSUES BY CATEGORY:")
for category, issues in analysis['all_issues'].items():
    if issues:
        print(f"\n  {category.upper()} ({len(issues)}):")
        for issue in issues[:3]:  # Show max 3 per category
            print(f"    • {issue}")
        if len(issues) > 3:
            print(f"    ... and {len(issues) - 3} more")

print("\n" + "=" * 70)
