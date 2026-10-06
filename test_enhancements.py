#!/usr/bin/env python
"""Test the specific enhancements."""

from orchestrator import Orchestrator

print("=" * 70)
print("TESTING ENHANCEMENTS")
print("=" * 70)

# Test 1: Print detection
test1 = '''
print "Hello"
print x
print y, z
'''

print("\n\nTEST 1: Print Statement Detection")
print("-" * 50)
print("Code:", test1.strip())
result = Orchestrator().run(test1)
print(f"Issues found: {len(result['issues_found'])}")
for issue in result['issues_found']:
    print(f"  - {issue['type']}")
print(f"Migrated:\n{result['migrated_code']}")

# Test 2: Division semantics
test2 = '''
result = 2 / 3
x = 10 / 5
'''

print("\n\nTEST 2: Division Semantics")
print("-" * 50)
print("Code:", test2.strip())
result = Orchestrator().run(test2)
print(f"Issues found: {len(result['issues_found'])}")
for issue in result['issues_found']:
    print(f"  - {issue['type']}")
print(f"Migrated:\n{result['migrated_code']}")

# Test 3: Complex example
test3 = '''
def process(data):
    print "Processing"
    result = data / 2
    for k, v in d.iteritems():
        print k, v
    return result
'''

print("\n\nTEST 3: Complex Migration")
print("-" * 50)
print("Code:", test3.strip())
result = Orchestrator().run(test3)
print(f"Success: {result['success']}")
print(f"Issues found: {len(result['issues_found'])}")
for issue in result['issues_found']:
    print(f"  - {issue['type']}")
print(f"\nMigrated:\n{result['migrated_code']}")
print(f"\nVerification:")
report = result.get('verification_report', {})
print(f"  Syntax valid: {report.get('syntax_valid')}")
print(f"  Runs: {report.get('runs')}")

print("\n" + "=" * 70)
