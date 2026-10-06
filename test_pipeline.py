#!/usr/bin/env python
"""Test the core pipeline end-to-end."""

from orchestrator import Orchestrator

# Load sample Python 2 code
with open('samples/example1.py', 'r') as f:
    source = f.read()

print("=" * 60)
print("TESTING CORE PIPELINE")
print("=" * 60)
print("\n📝 Original Python 2 Code:")
print("-" * 60)
print(source)
print("-" * 60)

# Run the orchestrator
orch = Orchestrator()
result = orch.run(source)

print(f"\n✅ Success: {result['success']}")
print(f"⏱️  Attempts: {result['attempts']}")
print(f"🔍 Issues Found: {len(result['issues_found'])}")

if result['issues_found']:
    print("\n📋 Issues Detected:")
    for issue in result['issues_found']:
        print(f"  - Line {issue['line']}: {issue['type']}")

print("\n🔄 Migration Method Used:")
for i, h in enumerate(result.get('iteration_history', []), 1):
    print(f"  Attempt {i}: {h.get('migration_method', 'unknown')}")

print("\n✨ Migrated Python 3 Code:")
print("-" * 60)
print(result['migrated_code'])
print("-" * 60)

if result.get('verification_report'):
    report = result['verification_report']
    print("\n🧪 Verification Results:")
    print(f"  ✓ Syntax Valid: {report.get('syntax_valid')}")
    print(f"  ✓ Compiles: {report.get('compiles')}")
    print(f"  ✓ Runs: {report.get('runs')}")
    print(f"  ✓ Output Matches: {report.get('output_matches')}")
    if report.get('errors'):
        print(f"\n  ❌ Errors:")
        for err in report['errors']:
            print(f"    - {err}")

print("\n" + "=" * 60)
