#!/usr/bin/env python
"""Comprehensive backend testing script."""

import sys
from orchestrator import Orchestrator

samples = [
    ("Example 1: Simple print & dict", "samples/example1.py"),
    ("Example 3: Class with iteritems", "samples/example3.py"),
]

print("=" * 70)
print("BACKEND CORE FUNCTIONALITY TEST SUITE")
print("=" * 70)

for title, filepath in samples:
    print(f"\n\n{'='*70}")
    print(f"🧪 TEST: {title}")
    print(f"{'='*70}")
    
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        
        print(f"\n📝 Original Code ({len(source)} chars):")
        print("-" * 50)
        print(source[:200] + ("..." if len(source) > 200 else ""))
        print("-" * 50)
        
        # Test with the orchestrator
        orch = Orchestrator()
        result = orch.run(source)
        
        # Results
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"\n{status}")
        print(f"  Success: {result['success']}")
        print(f"  Attempts: {result['attempts']}")
        print(f"  Issues Found: {len(result['issues_found'])}")
        
        # Verification
        if result.get('verification_report'):
            report = result['verification_report']
            checks = [
                ("Syntax", report.get('syntax_valid')),
                ("Compiles", report.get('compiles')),
                ("Runs", report.get('runs')),
                ("Output Matches", report.get('output_matches')),
            ]
            print("\n  Verification Checks:")
            for check_name, status in checks:
                icon = "✓" if status else "✗"
                print(f"    {icon} {check_name}")
            
            if report.get('errors'):
                print("\n  Errors:")
                for err in report['errors'][:3]:  # Show first 3 errors
                    print(f"    - {err}")
        
        print(f"\n✨ Migrated Code Preview:")
        print("-" * 50)
        migrated = result['migrated_code']
        print(migrated[:200] + ("..." if len(migrated) > 200 else ""))
        print("-" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"  Message: {e}")
        import traceback
        traceback.print_exc()

print("\n\n" + "=" * 70)
print("TEST SUITE COMPLETE")
print("=" * 70)
