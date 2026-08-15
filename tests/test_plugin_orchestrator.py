import unittest

from orchestrator import Orchestrator
from plugins.python2_to_python3.plugin import Python2ToPython3Plugin


class PluginOrchestratorTest(unittest.TestCase):
    def test_orchestrator_uses_python_plugin_by_default(self):
        orchestrator = Orchestrator()
        self.assertIsInstance(orchestrator.plugin, Python2ToPython3Plugin)


if __name__ == "__main__":
    unittest.main()
