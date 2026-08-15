import os
import sys
sys.path.append(".")
from orchestrator import Orchestrator
from report_generator import generate_report


def find_python_files(folder: str) -> list:
    """Recursively find all .py files in a folder."""
    py_files = []
    for root, dirs, files in os.walk(folder):
        # skip virtual environments and common noise folders
        dirs[:] = [d for d in dirs if d not in (".venv", "venv", "__pycache__", ".git")]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def migrate_project(folder: str, output_folder: str = "migrated_output"):
    py_files = find_python_files(folder)
    print(f"Found {len(py_files)} Python file(s) in '{folder}'.\n")

    os.makedirs(output_folder, exist_ok=True)

    summary = []

    for filepath in py_files:
        print(f"{'='*50}")
        print(f"Migrating: {filepath}")
        print(f"{'='*50}")

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        orchestrator = Orchestrator()
        result = orchestrator.run(source)

        # preserve relative folder structure in the output
        rel_path = os.path.relpath(filepath, folder)
        out_path = os.path.join(output_folder, rel_path)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result["migrated_code"])

        report_path = generate_report(filepath, result,
                                       output_path=f"reports/{rel_path.replace(os.sep, '_')}_report.md")

        summary.append({
            "file": filepath,
            "success": result["success"],
            "attempts": result["attempts"],
            "issues": len(result["issues_found"])
        })

    print(f"\n\n{'='*50}")
    print("PROJECT MIGRATION SUMMARY")
    print(f"{'='*50}")
    for s in summary:
        status = "✅" if s["success"] else "❌"
        print(f"{status} {s['file']:<40} issues={s['issues']:<3} attempts={s['attempts']}")

    total = len(summary)
    succeeded = sum(1 for s in summary if s["success"])
    print(f"\nOverall: {succeeded}/{total} files migrated successfully.")
    print(f"Migrated files saved to: {output_folder}/")
    print(f"Individual reports saved to: reports/")


if __name__ == "__main__":
    folder = sys.argv[1]
    migrate_project(folder)