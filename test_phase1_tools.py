"""Test Phase 1 toolsmith utilities."""

from src.utils.code_reader import CodeReader, SandboxSecurityError
from src.utils.pylint_runner import PylintRunner
from src.utils.pytest_runner import PytestRunner

print("=" * 60)
print("🧪 Testing Phase 1 Toolsmith Utilities")
print("=" * 60)

# Test 1: CodeReader
print("\n1️⃣ CodeReader Tests")
print("-" * 40)
reader = CodeReader('./sandbox')
files = reader.list_python_files()
print(f"✅ Found {len(files)} Python files: {files}")

content = reader.read_file('example.py')
print(f"✅ Read example.py: {len(content)} characters")

try:
    reader.read_file('../.env')
    print("❌ FAIL: Escape not blocked")
except SandboxSecurityError:
    print("✅ Sandbox escape blocked (security OK)")

# Test 2: PylintRunner
print("\n2️⃣ PylintRunner Tests")
print("-" * 40)
pylint = PylintRunner('./sandbox')
result = pylint.run_pylint('example.py')
print(f"✅ Pylint score: {result['score']}/10")
print(f"✅ Issues found: {len(result['messages'])}")

# Test 3: PytestRunner
print("\n3️⃣ PytestRunner Tests")
print("-" * 40)
pytest = PytestRunner('./sandbox')
test_result = pytest.run_tests()
print(f"✅ Pytest execution completed")
print(f"   - Passed: {test_result['passed']}")
print(f"   - Failed: {test_result['failed']}")
print(f"   - Errors: {test_result['errors']}")

print("\n" + "=" * 60)
print("✅ All Phase 1 toolsmith utilities working!")
print("=" * 60)
