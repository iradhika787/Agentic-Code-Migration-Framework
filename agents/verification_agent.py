import subprocess
import tempfile
import os
import ast
import shlex
import sys

class VerificationAgent:
    """
    Verifies migrated code by checking:
    1. It's syntactically valid Python 3
    2. It compiles without errors
    3. It runs without crashing
    4. (Optional) Its output matches an expected value — catches
       silent semantic bugs that compiling/running alone would miss
       (e.g. Python 2 floor division becoming Python 3 true division).
    """

    def verify(
        self,
        migrated_code: str,
        expected_output: str = None,
        runtime_timeout_seconds: int = 10,
        project_path: str = None,
        test_command: list[str] | str = None,
        test_timeout_seconds: int = 30,
    ) -> dict:
        result = {
            "syntax_valid": False,
            "compiles": False,
            "runs": False,
            "output_matches": True,  # default True when no expected_output given
            "actual_output": None,
            "runtime_timed_out": False,
            "test_suite_ran": False,
            "test_suite_passed": True,
            "test_suite_command": None,
            "test_suite_output": None,
            "errors": []
        }

        # 1. Syntax check via ast.parse
        try:
            ast.parse(migrated_code)
            result["syntax_valid"] = True
        except SyntaxError as e:
            result["errors"].append(f"SyntaxError: {e}")
            return result  # no point continuing

        # 2. Compile check
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(migrated_code)
            tmp_path = tmp.name

        try:
            compile_result = subprocess.run(
                ["python", "-m", "py_compile", tmp_path],
                capture_output=True, text=True, timeout=10
            )
            if compile_result.returncode == 0:
                result["compiles"] = True
            else:
                result["errors"].append(compile_result.stderr)
        except Exception as e:
            result["errors"].append(str(e))

        # 3. Execution check
        if result["compiles"]:
            try:
                run_result = subprocess.run(
                    ["python", tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=runtime_timeout_seconds,
                )
                if run_result.returncode == 0:
                    result["runs"] = True
                    result["actual_output"] = run_result.stdout.strip()
                else:
                    result["errors"].append(run_result.stderr)
            except subprocess.TimeoutExpired:
                result["runtime_timed_out"] = True
                result["errors"].append(
                    f"Runtime timeout after {runtime_timeout_seconds} seconds"
                )
            except Exception as e:
                result["errors"].append(str(e))

        # 4. Output-matching check (only if expected_output was provided)
        if result["runs"] and expected_output is not None:
            actual = result["actual_output"]
            expected = expected_output.strip()
            if actual != expected:
                result["output_matches"] = False
                result["errors"].append(
                    f"Output mismatch: expected '{expected}', got '{actual}'. "
                    f"This likely means the migration changed program behavior "
                    f"(e.g. Python 2 '/' floor division becoming Python 3 true "
                    f"division — use '//' if integer division was intended)."
                )

        if project_path is not None:
            self._run_project_tests(
                result,
                project_path=project_path,
                test_command=test_command,
                test_timeout_seconds=test_timeout_seconds,
            )

        os.unlink(tmp_path)
        return result

    def _run_project_tests(
        self,
        result: dict,
        project_path: str,
        test_command: list[str] | str = None,
        test_timeout_seconds: int = 30,
    ) -> None:
        command = self._build_test_command(project_path, test_command)
        result["test_suite_ran"] = True
        result["test_suite_command"] = " ".join(command)

        try:
            test_result = subprocess.run(
                command,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=test_timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            result["test_suite_passed"] = False
            result["errors"].append(f"Test suite timeout after {test_timeout_seconds} seconds")
            return
        except Exception as e:
            result["test_suite_passed"] = False
            result["errors"].append(f"Test suite execution failed: {e}")
            return

        output = "\n".join(
            part.strip()
            for part in [test_result.stdout, test_result.stderr]
            if part and part.strip()
        )
        result["test_suite_output"] = output
        if test_result.returncode != 0:
            result["test_suite_passed"] = False
            result["errors"].append(f"Test suite failed with exit code {test_result.returncode}")

    def _build_test_command(self, project_path: str, test_command: list[str] | str = None) -> list[str]:
        if isinstance(test_command, list):
            return test_command
        if isinstance(test_command, str):
            return shlex.split(test_command)
        if os.path.exists(os.path.join(project_path, "pytest.ini")) or os.path.exists(os.path.join(project_path, "tests")):
            return [sys.executable, "-m", "pytest"]
        return [sys.executable, "-m", "unittest", "discover"]


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from analysis_agent import AnalysisAgent
    from migration_agent import MigrationAgent

    with open(sys.argv[1]) as f:
        source = f.read()

    expected = sys.argv[2] if len(sys.argv) > 2 else None

    analyzer = AnalysisAgent()
    issues = analyzer.analyze(source)

    migrator = MigrationAgent()
    migrated_code = migrator.migrate(source, issues)

    verifier = VerificationAgent()
    report = verifier.verify(migrated_code, expected_output=expected)

    print("---- MIGRATED CODE ----")
    print(migrated_code)
    print("\n---- VERIFICATION REPORT ----")
    for k, v in report.items():
        print(f"{k}: {v}")
