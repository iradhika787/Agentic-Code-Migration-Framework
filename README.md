# Agentic Code Migration Framework

An agentic Python 2 to Python 3 migration framework with static analysis,
rule-based rewrites, verification, optional LLM fallback, reporting, a Streamlit
UI, and a curated migration dataset for evaluation or model fine-tuning.

## What Works Today

- Detects common Python 2 constructs such as `print` statements, `has_key`,
  old exception syntax, `xrange`, iterator-return changes, backtick `repr`,
  `<>`, and integer division risks.
- Migrates many common patterns with deterministic rules.
- Verifies migrated code by parsing, compiling, running, checking expected
  output when provided, and optionally running a project test suite.
- Falls back to an injected LLM provider after verification failure when a
  provider is configured.
- Generates migration reports and unified diffs.
- Includes a Streamlit interface for single-file migration.
- Includes a 64-example Python 2 to 3 dataset with train, validation, and test
  splits.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

The only listed runtime dependency is currently `streamlit`. The tests use
Python's standard `unittest` plus `pytest` as the test runner.

## Run A Single Migration

```bash
python main.py samples/example1.py --output-dir outputs
```

Or use the lower-level orchestrator:

```bash
python orchestrator.py samples/example1.py
```

## Run The UI

```bash
streamlit run app.py
```

The UI lets you upload a Python file, run the migration workflow, and inspect
input, output, diff, analysis issues, verification details, and logs.

## Run Tests

```bash
python -m pytest -q
```

## Benchmark Samples

```bash
python benchmark.py
```

This runs the framework over the sample files in `samples/` and writes
`benchmark_results.md`.

## Evaluate Against The Dataset

```bash
python -m data.evaluate_dataset data/splits/test.jsonl
```

The evaluator compares the rule-based migrator output against expected dataset
conversions and reports exact and normalized match rates by category and
difficulty. This is the fastest feedback loop for improving migration rules.

## Dataset

The dataset lives under `data/`:

- `data/python2to3_complete_dataset.json`: full 64-example dataset.
- `data/splits/train.jsonl`: training split.
- `data/splits/validation.jsonl`: validation split.
- `data/splits/test.jsonl`: test split.
- `data/dataset_manager.py`: dataset loading, validation, deduplication, and
  split utilities.
- `data/evaluate_dataset.py`: migration-rule evaluation script.

## Architecture

The primary runtime path is:

1. `orchestrator.Orchestrator`
2. `plugins.python2_to_python3.Python2ToPython3Plugin`
3. `AnalysisAgent`
4. `MigrationAgent`
5. `VerificationAgent`

The `core/` package contains generic modernization abstractions that can grow
to support additional migration plugins and workflow types.

## Known Gaps

- README and docs are now usable, but deeper API documentation is still needed.
- The rule engine is regex-heavy and should move toward token-aware or AST-aware
  transformations for complex syntax.
- LLM provider support is currently limited to Ollama-style generation and needs
  stronger configuration, retries, and error handling.
- Knowledge base and memory classes are scaffolds and are not yet deeply wired
  into migration decisions.
- Dataset evaluation measures output match, but it does not yet score semantic
  equivalence beyond expected text.
