"""
Interactive demo showing the Polisher's capabilities.
Demonstrates how Black formatting improves code quality scores.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tools import (
    apply_black_formatting,
    get_project_structure,
    format_and_analyze,
    write_file,
    analyze_code_quality
)

print("=" * 70)
print("THE POLISHER - Code Formatting & Quality Demo")
print("=" * 70)

# Create a really messy Python file
messy_code = '''
import os,sys
import json

def calculate(x,y,z):
    result=x+y+z;temp=result*2
    return temp

def process_data(  data  ):
        processed=[]
        for item in data:
                    if item>0:
                                        processed.append(item*2)
        return processed

x=5;y=10;z=15
result=calculate(x,y,z)
print(result)

data=[1,2,3,4,5]
processed=process_data(data)
print(processed)

def another_function(a,b,c,d,e,f,g):
    return a+b+c+d+e+f+g
'''

write_file("demo_messy.py", messy_code)

print("\n📝 Created a messy Python file with:")
print("   • Inconsistent spacing")
print("   • Poor indentation")
print("   • Multiple statements on one line")
print("   • No proper formatting")

# Show the mess
print("\n" + "=" * 70)
print("BEFORE FORMATTING")
print("=" * 70)
print(messy_code[:300] + "...")

# Analyze before
print("\n🔍 Analyzing code quality BEFORE formatting...")
before = analyze_code_quality("demo_messy.py")
before_score = before.get('pylint_score', 0)
before_issues = before.get('total_issues', 0)

print(f"\n📊 Quality Score: {before_score}/10")
print(f"📋 Total Issues: {before_issues}")
if before.get('all_issues', {}).get('convention'):
    print(f"⚠️  Convention issues: {len(before['all_issues']['convention'])}")

# Apply Black
print("\n" + "=" * 70)
print("APPLYING BLACK FORMATTER")
print("=" * 70)

format_result = apply_black_formatting("demo_messy.py")
print(f"\n{'✓' if format_result['success'] else '✗'} {format_result['summary']}")

if format_result['reformatted']:
    print("✨ Code has been automatically reformatted!")
    
    # Read formatted code
    from src.tools import read_file
    formatted_code = read_file("demo_messy.py")
    
    print("\n" + "=" * 70)
    print("AFTER FORMATTING")
    print("=" * 70)
    print(formatted_code[:400] + "...")

# Analyze after
print("\n🔍 Analyzing code quality AFTER formatting...")
after = analyze_code_quality("demo_messy.py")
after_score = after.get('pylint_score', 0)
after_issues = after.get('total_issues', 0)

print(f"\n📊 Quality Score: {after_score}/10")
print(f"📋 Total Issues: {after_issues}")
if after.get('all_issues', {}).get('convention'):
    print(f"⚠️  Convention issues: {len(after['all_issues']['convention'])}")

# Show improvement
print("\n" + "=" * 70)
print("IMPROVEMENT SUMMARY")
print("=" * 70)

score_improvement = after_score - before_score
issue_reduction = before_issues - after_issues

print(f"\n🎯 Score Change: {before_score}/10 → {after_score}/10")
if score_improvement > 0:
    print(f"✅ Improved by {score_improvement:.2f} points!")
elif score_improvement < 0:
    print(f"⚠️  Decreased by {abs(score_improvement):.2f} points")
else:
    print(f"➡️  No change in score")

print(f"\n📉 Issues Reduced: {before_issues} → {after_issues}")
if issue_reduction > 0:
    print(f"✅ Fixed {issue_reduction} issues automatically!")

# Show project structure
print("\n" + "=" * 70)
print("PROJECT STRUCTURE VISUALIZATION")
print("=" * 70)

print("\n🗂️  Current sandbox structure:\n")
tree = get_project_structure(max_depth=3)
print(tree)

# Comprehensive workflow demo
print("\n" + "=" * 70)
print("COMPREHENSIVE WORKFLOW: format_and_analyze()")
print("=" * 70)

# Create another messy file
complex_code = '''
import os

def helper(x,y):
    return x*y

def main(a,b,c):
    result=helper(a,b)+c
    return result

if __name__=="__main__":
    print(main(2,3,4))
'''

write_file("demo_complex.py", complex_code)
print("\n📝 Created demo_complex.py")

result = format_and_analyze("demo_complex.py")

print(f"\n✓ Complete workflow executed")
print(f"  Formatting: {result['formatting']['summary']}")

if result['analysis_before'] and result['analysis_after']:
    before = result['analysis_before']['pylint_score']
    after = result['analysis_after']['pylint_score']
    print(f"  Score: {before}/10 → {after}/10")
    
    if result['improvement']:
        print(f"  Change: {result['improvement']:+.2f} points")

print(f"\n💡 Recommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

print("\n" + "=" * 70)
print("KEY TAKEAWAY")
print("=" * 70)
print("""
🎯 The Polisher automatically fixes style issues with Black,
   boosting Pylint scores before the agent attempts logic fixes.
   
📈 This is crucial for the self-healing loop:
   1. Format code with Black (automatic style fixes)
   2. Analyze with Pylint (detect remaining issues)
   3. Agent fixes logic/semantic issues
   4. Repeat until quality threshold is met
""")

print("=" * 70)
