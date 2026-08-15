import unittest

from core.confidence_engine import ConfidenceEngine
from core.context import ModernizationContext
from core.orchestrator import FrameworkOrchestrator


class ConfidenceEngineTest(unittest.TestCase):
    def test_confidence_engine_decides_proceed_for_high_confidence(self):
        engine = ConfidenceEngine()
        self.assertEqual(engine.decide(0.95), "proceed")

    def test_confidence_engine_decides_warn_for_mid_confidence(self):
        engine = ConfidenceEngine()
        self.assertEqual(engine.decide(0.7), "warn")

    def test_framework_orchestrator_sets_decision(self):
        context = ModernizationContext()
        context.confidence_scores["overall"] = 0.9
        orchestrator = FrameworkOrchestrator()
        result = orchestrator.run(context)
        self.assertEqual(result.final_report_data["decision"], "proceed")


if __name__ == "__main__":
    unittest.main()
