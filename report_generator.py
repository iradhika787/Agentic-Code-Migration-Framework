from datetime import datetime


def _coerce_result(result: dict, filename: str) -> dict:
    if isinstance(result, dict):
        return result
    if hasattr(result, "final_report_data"):
        final_report = getattr(result, "final_report_data", {}) or {}
        return {
            "success": final_report.get("success", False),
            "attempts": final_report.get("attempts", 0),
            "issues_found": final_report.get("issues_found", []),
            "execution_log": getattr(result, "logs", []),
            "diff": final_report.get("diff", ""),
            "verification_report": final_report.get("verification_report", {}),
            "migrated_code": final_report.get("migrated_code", ""),
            "confidence_scores": final_report.get("confidence_scores", {}),
            "filename": filename,
        }
    return {"success": False, "attempts": 0, "issues_found": [], "execution_log": [], "diff": "", "verification_report": {}, "migrated_code": "", "confidence_scores": {}, "filename": filename}


def generate_report(filename: str, result: dict, output_path: str = None) -> str:
    """
    Generates a Markdown modernization report from either a result dict or a context-like object.
    """
    if output_path is None:
        base = filename.replace("/", "_").replace("\\", "_").rstrip(".py")
        output_path = f"reports/{base}_report.md"

    import os
    os.makedirs("reports", exist_ok=True)

    result = _coerce_result(result, filename)
    lines = []
    lines.append(f"# Modernization Report: {result.get('filename', filename)}")
    lines.append(f"\n_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

    lines.append("## Summary")
    lines.append(f"- **Success:** {'✅ Yes' if result.get('success') else '❌ No'}")
    lines.append(f"- **Attempts:** {result.get('attempts', 0)}")
    lines.append(f"- **Issues detected:** {len(result.get('issues_found', []))}\n")

    if result.get("confidence_scores"):
        lines.append("- **Confidence:**")
        for key, value in result["confidence_scores"].items():
            lines.append(f"  - {key}: {value}")

    lines.append("## Issues Detected")
    for issue in result.get("issues_found", []):
        lines.append(f"- Line {issue.get('line')}: `{issue.get('type')}` — `{issue.get('detail')}`")

    lines.append("\n## Execution Log")
    lines.append("```")
    lines.extend(result.get("execution_log", []))
    lines.append("```")

    lines.append("\n## Code Diff")
    lines.append("```diff")
    lines.append(result.get("diff", ""))
    lines.append("```")

    lines.append("\n## Verification Report")
    verification_report = result.get("verification_report") or {}
    for k, v in verification_report.items():
        lines.append(f"- **{k}:** {v}")

    lines.append("\n## Final Output")
    lines.append("```python")
    lines.append(result.get("migrated_code", ""))
    lines.append("```")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Report saved to {output_path}")
    return output_path


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from orchestrator import Orchestrator

    filename = sys.argv[1]
    expected = sys.argv[2] if len(sys.argv) > 2 else None

    with open(filename) as f:
        source = f.read()

    orchestrator = Orchestrator()
    result = orchestrator.run(source, expected_output=expected)

    generate_report(filename, result)