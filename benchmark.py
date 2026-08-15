import sys
import time
sys.path.append("agents")

from orchestrator import Orchestrator

# Each entry: (filename, expected_output or None)
# expected_output is only set where we know the correct result in advance
# (used to demonstrate the semantic-correctness check, not just "it ran").
BENCHMARK_SET = [
    ("samples/example1.py", None),
    ("samples/example2.py", None),
    ("samples/example3.py", None),
    ("samples/example4.py", None),
    ("samples/example5.py", None),
    ("samples/example6.py", "2"),
]


def run_benchmark():
    results = []

    for filename, expected in BENCHMARK_SET:
        print(f"\n{'='*50}")
        print(f"Running: {filename}")
        print(f"{'='*50}")

        with open(filename) as f:
            source = f.read()

        orchestrator = Orchestrator()

        start = time.time()
        result = orchestrator.run(source, expected_output=expected)
        elapsed = round(time.time() - start, 2)

        results.append({
            "file": filename,
            "issues_found": len(result["issues_found"]),
            "attempts": result["attempts"],
            "success": result["success"],
            "time_sec": elapsed
        })

    return results


def print_table(results):
    print("\n\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    header = f"{'File':<25} {'Issues':<8} {'Attempts':<10} {'Success':<10} {'Time (s)':<10}"
    print(header)
    print("-" * 70)
    for r in results:
        print(f"{r['file']:<25} {r['issues_found']:<8} {r['attempts']:<10} "
              f"{str(r['success']):<10} {r['time_sec']:<10}")

    total = len(results)
    successes = sum(1 for r in results if r["success"])
    avg_attempts = round(sum(r["attempts"] for r in results) / total, 2)
    total_time = round(sum(r["time_sec"] for r in results), 2)

    print("-" * 70)
    print(f"Success rate: {successes}/{total} ({round(successes/total*100, 1)}%)")
    print(f"Average attempts: {avg_attempts}")
    print(f"Total time: {total_time}s")


def save_markdown(results, path="benchmark_results.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Results\n\n")
        f.write("| File | Issues Found | Attempts | Success | Time (s) |\n")
        f.write("|------|--------------|----------|---------|----------|\n")
        for r in results:
            f.write(f"| {r['file']} | {r['issues_found']} | {r['attempts']} | "
                     f"{'✅' if r['success'] else '❌'} | {r['time_sec']} |\n")

        total = len(results)
        successes = sum(1 for r in results if r["success"])
        avg_attempts = round(sum(r["attempts"] for r in results) / total, 2)

        f.write(f"\n**Success rate:** {successes}/{total} "
                f"({round(successes/total*100, 1)}%)\n")
        f.write(f"**Average attempts:** {avg_attempts}\n")

    print(f"\nSaved markdown table to {path}")


if __name__ == "__main__":
    results = run_benchmark()
    print_table(results)
    save_markdown(results)