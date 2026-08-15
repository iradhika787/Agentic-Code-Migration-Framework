import unittest

from plugins.python2_to_python3.plugin import Python2ToPython3Plugin
from agents.verification_agent import VerificationAgent


class RuntimeTimeoutPolicyTest(unittest.TestCase):
    def test_verification_marks_runtime_timeout(self):
        code = "import time\ntime.sleep(0.2)\nprint('done')\n"
        report = VerificationAgent().verify(code, runtime_timeout_seconds=0)
        self.assertTrue(report["runtime_timed_out"])
        self.assertTrue(report["syntax_valid"])
        self.assertTrue(report["compiles"])

    def test_plugin_accepts_timeout_without_expected_output(self):
        plugin = Python2ToPython3Plugin()
        report = {
            "syntax_valid": True,
            "compiles": True,
            "runs": False,
            "output_matches": True,
            "runtime_timed_out": True,
        }
        self.assertTrue(plugin._is_success(report, expected_output=None))

    def test_plugin_rejects_timeout_with_expected_output(self):
        plugin = Python2ToPython3Plugin()
        report = {
            "syntax_valid": True,
            "compiles": True,
            "runs": False,
            "output_matches": True,
            "runtime_timed_out": True,
        }
        self.assertFalse(plugin._is_success(report, expected_output="ok"))


if __name__ == "__main__":
    unittest.main()
