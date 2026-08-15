import unittest

from verification.engine import VerificationEngine


class VerificationEngineTest(unittest.TestCase):
    def test_engine_runs_registered_checks(self):
        engine = VerificationEngine()
        engine.add_check("syntax", lambda context: {"passed": True, "name": "syntax"})
        engine.add_check("runtime", lambda context: {"passed": True, "name": "runtime"})

        results = engine.run({"source": "print('ok')"})

        self.assertEqual(results["syntax"]["name"], "syntax")
        self.assertEqual(results["runtime"]["name"], "runtime")


if __name__ == "__main__":
    unittest.main()
