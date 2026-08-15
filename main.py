"""Entry point for the agentic Python migration workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

from orchestrator import MigrationOrchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate Python 2 scripts to Python 3.")
    parser.add_argument(
        "source",
        nargs="?",
        default="samples/example1.py",
        help="Path to the Python 2 source file.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where migrated files should be written.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    orchestrator = MigrationOrchestrator()
    with Path(args.source).open(encoding="utf-8") as source_file:
        source_code = source_file.read()

    result = orchestrator.run(source_code)

    print(f"Analyzed: {args.source}")
    print(f"Issues found: {len(result['issues_found'])}")
    for issue in result["issues_found"]:
        print(f"  line {issue.get('line')}: {issue.get('type')} - {issue.get('detail')}")

    verification = result.get("verification_report", {})
    print(f"Verification: {verification.get('errors') or 'passed'}")
    if result.get("success"):
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / Path(args.source).name
        output_path.write_text(result["migrated_code"], encoding="utf-8")
        print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()

