#!/usr/bin/env python
"""Debug the failing test."""

from agents.migration_agent import MigrationAgent
from plugins.python2_to_python3.plugin import Python2ToPython3Plugin

code = "items = map(str, xrange(3))\nprint items"

# Step 1: Migrate
migrator = MigrationAgent()
result_code = migrator.migrate(code, [])

print("Original:")
print(code)
print("\nMigrated:")
print(result_code)

# Step 2: Run migrated code
import subprocess
import tempfile

with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write(result_code)
    f.flush()
    
    run_result = subprocess.run(["python", f.name], capture_output=True, text=True)
    print("\nOutput:")
    print(repr(run_result.stdout))
    print("Stderr:")
    print(repr(run_result.stderr))
    print("Return code:", run_result.returncode)
