"""Evaluate the rule-based migrator against a Python 2 to 3 dataset."""

from __future__ import annotations

import argparse
import io
import json
import tokenize
from collections import defaultdict
from pathlib import Path
from typing import Any

from agents.analysis_agent import AnalysisAgent
from agents.migration_agent import MigrationAgent


def load_examples(path: str | Path) -> list[dict[str, Any]]:
    """Load examples from a JSONL split or the full dataset JSON file."""
    dataset_path = Path(path)
    if dataset_path.suffix == ".jsonl":
        return [
            json.loads(line)
            for line in dataset_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    return payload.get("examples", [])


def normalize_code(code: str) -> str:
    """Normalize formatting and comments for migration-output comparison."""
    try:
        tokens = [
            token
            for token in tokenize.generate_tokens(io.StringIO(code).readline)
            if token.type != tokenize.COMMENT
        ]
        code = tokenize.untokenize(tokens)
    except tokenize.TokenError:
        pass

    return "\n".join(line.rstrip() for line in code.strip().splitlines())


def evaluate_examples(
    examples: list[dict[str, Any]],
    analyzer: AnalysisAgent | None = None,
    migrator: MigrationAgent | None = None,
) -> dict[str, Any]:
    analyzer = analyzer or AnalysisAgent()
    migrator = migrator or MigrationAgent()

    results = []
    for example in examples:
        source = example["python2_code"]
        expected = example["python3_code"]
        issues = analyzer.analyze(source)
        actual = migrator.migrate_with_rules(source)
        results.append(
            {
                "id": example.get("id"),
                "category": example.get("category", "unknown"),
                "difficulty": example.get("difficulty", "unknown"),
                "pattern_type": example.get("pattern_type", "unknown"),
                "exact_match": actual.strip() == expected.strip(),
                "normalized_match": normalize_code(actual) == normalize_code(expected),
                "actual": actual,
                "expected": expected,
                "issue_count": len(issues),
            }
        )

    return {
        "total": len(results),
        "exact_matches": sum(1 for item in results if item["exact_match"]),
        "normalized_matches": sum(1 for item in results if item["normalized_match"]),
        "by_category": _summarize(results, "category"),
        "by_difficulty": _summarize(results, "difficulty"),
        "failures": [item for item in results if not item["normalized_match"]],
    }


def _summarize(results: list[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "matched": 0})
    for item in results:
        bucket = summary[item[key]]
        bucket["total"] += 1
        if item["normalized_match"]:
            bucket["matched"] += 1
    return dict(sorted(summary.items()))


def format_summary(summary: dict[str, Any], max_failures: int = 10) -> str:
    total = summary["total"]
    normalized = summary["normalized_matches"]
    exact = summary["exact_matches"]
    accuracy = (normalized / total * 100) if total else 0.0

    lines = [
        "Dataset evaluation",
        f"Total examples: {total}",
        f"Exact matches: {exact}/{total}",
        f"Normalized matches: {normalized}/{total} ({accuracy:.1f}%)",
        "",
        "By category:",
    ]
    for category, stats in summary["by_category"].items():
        lines.append(f"- {category}: {stats['matched']}/{stats['total']}")

    lines.append("")
    lines.append("By difficulty:")
    for difficulty, stats in summary["by_difficulty"].items():
        lines.append(f"- {difficulty}: {stats['matched']}/{stats['total']}")

    failures = summary["failures"][:max_failures]
    if failures:
        lines.append("")
        lines.append(f"First {len(failures)} failure(s):")
        for failure in failures:
            lines.append(
                f"- {failure['id']} [{failure['category']}/{failure['pattern_type']}]"
            )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the migration rules against a dataset split."
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        default="data/splits/test.jsonl",
        help="Path to a JSONL split or full dataset JSON file.",
    )
    parser.add_argument(
        "--max-failures",
        type=int,
        default=10,
        help="Number of mismatches to list in the CLI summary.",
    )
    args = parser.parse_args()

    examples = load_examples(args.dataset)
    summary = evaluate_examples(examples)
    print(format_summary(summary, max_failures=args.max_failures))


if __name__ == "__main__":
    main()
