#!/usr/bin/env python
"""Test error handling and edge cases in the backend."""

from orchestrator import Orchestrator

print("=" * 70)
print("BACKEND ERROR HANDLING & EDGE CASES TEST")
print("=" * 70)

# Test 1: Code with explicit output verification
test1_code = '''
def add(a, b):
    return a + b

print 2 / 3  # Python 2: 0, Python 3: 0.666...
'''

print("\n\n" + "="*70)
print("TEST 1: Division Semantics (Python 2 vs 3)")
print("="*70)
print("Code:", test1_code.strip()[:80] + "...")

orch = Orchestrator()
result = orch.run(test1_code)
print(f"Success: {result['success']}")
print(f"Issues Found: {len(result['issues_found'])}")
if result['issues_found']:
    for issue in result['issues_found']:
        print(f"  - {issue['type']}: {issue['detail']}")

# Test 2: Code with syntax errors
test2_code = '''
print "unclosed string
x = 5
'''

print("\n\n" + "="*70)
print("TEST 2: Syntax Error in Source")
print("="*70)
print("Code: Print statement with unclosed string")

try:
    result = orch.run(test2_code)
    print(f"Success: {result['success']}")
    print(f"Attempts: {result['attempts']}")
except Exception as e:
    print(f"Exception (Expected): {type(e).__name__}: {e}")

# Test 3: Large file handling
test3_code = '\n'.join([
    f'# Line {i}' if i % 100 == 0 else f'x{i} = {i}'
    for i in range(1000)
]) + '\nprint "Done"'

print("\n\n" + "="*70)
print("TEST 3: Large File (1000 lines)")
print("="*70)

import time
start = time.time()
result = orch.run(test3_code)
elapsed = time.time() - start

print(f"Success: {result['success']}")
print(f"Time: {elapsed:.2f}s")
print(f"Code Size: {len(test3_code)} chars")
print(f"Issues Found: {len(result['issues_found'])}")
print(f"Migrated Size: {len(result['migrated_code'])} chars")

# Test 4: Unicode and encoding
test4_code = '''
# -*- coding: utf-8 -*-
print "Hëllö, wørld!"
print unicode("test")
'''

print("\n\n" + "="*70)
print("TEST 4: Unicode/Encoding")
print("="*70)

result = orch.run(test4_code)
print(f"Success: {result['success']}")
print(f"Issues Found: {len(result['issues_found'])}")
print(f"Migrated Code:\n{result['migrated_code']}")

# Test 5: Multiple issue types
test5_code = '''
d = {"key": "value"}
if d.has_key("key"):
    print "found"

result = map(lambda x: x * 2, [1, 2, 3])
print result

except Exception, e:
    print str(e)
'''

print("\n\n" + "="*70)
print("TEST 5: Multiple Issue Types")
print("="*70)

result = orch.run(test5_code)
print(f"Success: {result['success']}")
print(f"Issues Found: {len(result['issues_found'])}")
if result['issues_found']:
    print("Issue types:")
    issue_types = set()
    for issue in result['issues_found']:
        issue_types.add(issue['type'])
    for itype in sorted(issue_types):
        print(f"  - {itype}")

print("\n" + "=" * 70)
print("EDGE CASE TESTING COMPLETE")
print("=" * 70)
