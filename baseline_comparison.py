import subprocess
import tempfile
import os
import requests
from orchestrator import Orchestrator

BENCHMARK_SET = [
    ("samples/example1.py", None),
    ("samples/example2.py", None),
    ("samples/example3.py", None),
    ("samples/example4.py", None),
    ("samples/example5.py", None),
    ("samples/example6.py", "2"),
]


def ungrounded_migrate(source_code: str, model="qwen2.5-coder:7b", host="http://localhost:11434") -> str:
    """
    Baseline: asks the LLM to convert Python 2 to Python 3 with NO
    static analysis grounding — just the raw code and a generic
    instruction. Used to isolate the value added by the Analysis
    Agent's grounding, vs. relying on the LLM's own judgment alone.
    """
    prompt = f"""Convert this Python 2 code to Python 3.

```python
{source_code}
```

Output ONLY the converted Python 3 code inside a single ```python code block, nothing else.
"""
    response = requests.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    raw = response.json()["response"]
    if "```python" in raw:
        return raw.split("```python")[1].split("```")[0].strip()
    elif "```" in raw:
        return raw.split("```")[1].split("```")[0].strip()
    return raw.strip()


def check_runs(code: str, expected_output=None):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=10)
        runs_ok = result.returncode == 0
        output = result.stdout.strip()
        output_ok = True if expected_output is None else (output == expected_output.strip())
        return runs_ok, output_ok
    except Exception:
        return False, False
    finally:
        os.unlink(tmp_path)


print("NOTE: '2to3' is unavailable — removed from the Python standard library in 3.13+.")
print("Using an ungrounded single-shot LLM call as the baseline instead (isolates the")
print("value of static-analysis grounding, which is this project's core claim).\n")

print(f"{'File':<20} {'Baseline runs':<16} {'Baseline correct':<18} {'Ours runs':<12} {'Ours correct'}")
print("-" * 85)

for filename, expected in BENCHMARK_SET:
    with open(filename) as f:
        source = f.read()

    # Baseline: ungrounded LLM
    baseline_code = ungrounded_migrate(source)
    b_runs, b_correct = check_runs(baseline_code, expected)

    # Ours: grounded pipeline
    orchestrator = Orchestrator()
    result = orchestrator.run(source, expected_output=expected)
    o_runs = result["verification_report"]["runs"]
    o_correct = result["success"]

    print(f"{filename:<20} {str(b_runs):<16} {str(b_correct):<18} {str(o_runs):<12} {str(o_correct)}")