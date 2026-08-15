import sys
import tempfile
import unittest
from pathlib import Path

from agents.verification_agent import VerificationAgent
from plugins.python2_to_python3.plugin import Python2ToPython3Plugin


class ProjectSuiteVerificationTest(unittest.TestCase):
    def _write_unittest_project(self, root: str, assertion: str) -> None:
        Path(root, "test_sample.py").write_text(
            "import unittest\n\n"
            "class SampleTest(unittest.TestCase):\n"
            "    def test_behavior(self):\n"
            f"        {assertion}\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )

    def test_verification_runs_project_unittest_suite_successfully(self):
        with tempfile.TemporaryDirectory() as project:
            self._write_unittest_project(project, "self.assertEqual(2 + 2, 4)")

            report = VerificationAgent().verify(
                "print('ok')",
                project_path=project,
                test_command=[sys.executable, "-m", "unittest", "discover"],
            )

            self.assertTrue(report["test_suite_ran"])
            self.assertTrue(report["test_suite_passed"])
            self.assertIn("unittest", report["test_suite_command"])

    def test_verification_reports_project_test_failures(self):
        with tempfile.TemporaryDirectory() as project:
            self._write_unittest_project(project, "self.assertEqual(2 + 2, 5)")

            report = VerificationAgent().verify(
                "print('ok')",
                project_path=project,
                test_command=[sys.executable, "-m", "unittest", "discover"],
            )

            self.assertTrue(report["test_suite_ran"])
            self.assertFalse(report["test_suite_passed"])
            self.assertTrue(any("Test suite failed" in error for error in report["errors"]))

    def test_plugin_rejects_migration_when_project_tests_fail(self):
        with tempfile.TemporaryDirectory() as project:
            self._write_unittest_project(project, "self.assertEqual(2 + 2, 5)")

            result = Python2ToPython3Plugin().run_pipeline(
                "print 'ok'",
                project_path=project,
                test_command=[sys.executable, "-m", "unittest", "discover"],
            )

            self.assertFalse(result["success"])
            self.assertFalse(result["verification_report"]["test_suite_passed"])
            self.assertEqual(result["iteration_history"][0]["failed_checks"], ["test_suite_passed"])
            self.assertFalse(result["iteration_metrics"]["converged"])
            self.assertEqual(result["iteration_metrics"]["total_iterations"], 1)


if __name__ == "__main__":
    unittest.main()
