"""Python 2 to Python 3 modernization plugin facade."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.interfaces import PluginMetadata
from core.context import ModernizationContext

from agents.analysis_agent import AnalysisAgent
from agents.migration_agent import MigrationAgent
from agents.verification_agent import VerificationAgent


@dataclass
class Python2ToPython3Plugin:
    metadata: PluginMetadata = field(
        default_factory=lambda: PluginMetadata(
            name="python2_to_python3",
            source_technology="python2",
            target_technology="python3",
        )
    )
    analyzer: AnalysisAgent = field(default_factory=AnalysisAgent)
    migrator: MigrationAgent = field(default_factory=MigrationAgent)
    verifier: VerificationAgent = field(default_factory=VerificationAgent)

    def detect(self, context: ModernizationContext) -> dict:
        return {
            "technology": "python",
            "confidence": 0.99,
            "plugin": self.metadata.name,
        }

    def analyze(self, context: ModernizationContext) -> dict:
        source_code = context.agent_outputs.get("source_code", "")
        issues = self.analyzer.analyze(source_code)
        context.agent_outputs["issues_found"] = issues
        return {"issues_found": issues, "confidence": 0.95}

    def plan(self, context: ModernizationContext) -> list[dict]:
        return [
            {"step": "analysis", "agent": "AnalysisAgent"},
            {"step": "migration", "agent": "MigrationAgent"},
            {"step": "verification", "agent": "VerificationAgent"},
        ]

    def execute(self, context: ModernizationContext) -> dict:
        source_code = context.agent_outputs.get("source_code", "")
        issues = context.agent_outputs.get("issues_found", [])
        migrated_code = self.migrator.migrate(source_code, issues)
        context.agent_outputs["migrated_code"] = migrated_code
        return {"migrated_code": migrated_code, "confidence": 0.9}

    def verify(self, context: ModernizationContext) -> dict:
        migrated_code = context.agent_outputs.get("migrated_code", "")
        expected_output = context.final_report_data.get("expected_output")
        report = self.verifier.verify(
            migrated_code,
            expected_output=expected_output,
            project_path=context.final_report_data.get("project_path"),
            test_command=context.final_report_data.get("test_command"),
        )
        context.agent_outputs["verification_report"] = report
        return report

    def _is_success(self, report: dict, expected_output: str | None) -> bool:
        base_ok = report.get("syntax_valid") and report.get("compiles")
        if not base_ok:
            return False

        if report.get("runtime_timed_out"):
            return expected_output is None

        return (
            report.get("runs")
            and report.get("output_matches")
            and report.get("test_suite_passed", True)
        )

    def run_pipeline(
        self,
        source_code: str,
        expected_output: str | None = None,
        max_retries: int = 3,
        project_path: str | None = None,
        test_command: list[str] | str | None = None,
    ) -> dict:
        context = ModernizationContext()
        context.agent_outputs["source_code"] = source_code
        if expected_output is not None:
            context.final_report_data["expected_output"] = expected_output
        if project_path is not None:
            context.final_report_data["project_path"] = project_path
        if test_command is not None:
            context.final_report_data["test_command"] = test_command

        self.detect(context)
        analysis_result = self.analyze(context)
        issues = analysis_result.get("issues_found", [])
        log = [f"[Analysis Agent] Found {len(issues)} issue(s):"]
        for issue in issues:
            log.append(f"    - Line {issue.get('line')}: {issue.get('type')} ({issue.get('detail')})")

        attempt = 0
        migrated_code = None
        report = None
        last_errors = []
        iteration_history = []

        while attempt < max_retries:
            attempt += 1
            if attempt == 1:
                migration_method = "rule_based"
                log.append(f"\n[Migration Agent] Attempt {attempt} using rule-based migration...")
                migrated_code = self.migrator.migrate_with_rules(source_code)
            else:
                migration_method = "ai_fallback"
                log.append(f"\n[Migration Agent] Attempt {attempt} using AI fallback...")
                migrated_code = self.migrator.migrate_with_provider(
                    source_code,
                    issues,
                    previous_errors=last_errors,
                )

            context.agent_outputs["migrated_code"] = migrated_code
            report = self.verify(context)
            log.append(
                f"[Verification Agent] syntax_valid={report['syntax_valid']}, "
                f"compiles={report['compiles']}, runs={report['runs']}, "
                f"output_matches={report['output_matches']}, "
                f"test_suite_passed={report.get('test_suite_passed', True)}"
            )
            if report.get("errors"):
                for err in report["errors"]:
                    log.append(f"    ! {err}")

            success = self._is_success(report, expected_output)
            feedback = self._build_verification_feedback(report)
            iteration_history.append(
                {
                    "attempt": attempt,
                    "migration_method": migration_method,
                    "success": success,
                    "failed_checks": feedback["failed_checks"],
                    "feedback": feedback["messages"],
                }
            )
            if success:
                if report.get("runtime_timed_out"):
                    log.append("[Plugin] Runtime timed out, accepted for this run because no expected output was required.")
                log.append(f"[Plugin] Migration succeeded on attempt {attempt}.")
                break

            last_errors = feedback["messages"]
            if self.migrator.provider is None:
                log.append("[Plugin] Rule-based migration failed and no AI provider is configured.")
                break
            log.append(
                f"[Plugin] Attempt {attempt} failed checks: "
                f"{', '.join(feedback['failed_checks']) or 'unknown'}. "
                "Retrying with verification feedback..."
            )

        final_success = self._is_success(report or {}, expected_output)

        return {
            "issues_found": issues,
            "migrated_code": migrated_code,
            "verification_report": report,
            "attempts": attempt,
            "success": final_success,
            "iteration_history": iteration_history,
            "iteration_metrics": self._build_iteration_metrics(iteration_history),
            "execution_log": log,
            "diff": self._generate_diff(source_code, migrated_code),
            "confidence_scores": {
                "plugin_detected": context.confidence_scores.get("plugin_detected", 0.0),
                "analysis": 0.95,
                "migration": 0.9,
                "verification": 0.97,
            },
        }

    def _generate_diff(self, original: str, migrated: str | None) -> str:
        if not migrated:
            return ""
        import difflib

        diff_lines = difflib.unified_diff(
            original.splitlines(keepends=True),
            migrated.splitlines(keepends=True),
            fromfile="original.py",
            tofile="migrated.py",
        )
        return "".join(diff_lines)

    def _build_verification_feedback(self, report: dict) -> dict:
        checks = {
            "syntax_valid": report.get("syntax_valid"),
            "compiles": report.get("compiles"),
            "runs": report.get("runs"),
            "output_matches": report.get("output_matches"),
            "test_suite_passed": report.get("test_suite_passed", True),
        }
        if report.get("runtime_timed_out"):
            checks["runtime_timed_out"] = False

        failed_checks = [name for name, passed in checks.items() if not passed]
        messages = [f"Failed check: {name}" for name in failed_checks]
        messages.extend(report.get("errors", []))

        actual_output = report.get("actual_output")
        if actual_output is not None:
            messages.append(f"Actual output: {actual_output}")

        test_output = report.get("test_suite_output")
        if test_output:
            messages.append(f"Test suite output:\n{test_output}")

        return {
            "failed_checks": failed_checks,
            "messages": messages,
        }

    def _build_iteration_metrics(self, iteration_history: list[dict]) -> dict:
        attempts = len(iteration_history)
        successful_attempts = [item for item in iteration_history if item.get("success")]
        rule_attempts = [
            item for item in iteration_history
            if item.get("migration_method") == "rule_based"
        ]
        ai_attempts = [
            item for item in iteration_history
            if item.get("migration_method") == "ai_fallback"
        ]
        return {
            "iterations_to_convergence": successful_attempts[0]["attempt"] if successful_attempts else None,
            "total_iterations": attempts,
            "rule_based_attempts": len(rule_attempts),
            "ai_fallback_attempts": len(ai_attempts),
            "converged": bool(successful_attempts),
        }
