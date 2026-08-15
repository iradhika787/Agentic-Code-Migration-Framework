import unittest

from core.context import ModernizationContext
from core.workflow_planner import WorkflowPlanner


class WorkflowPlannerTest(unittest.TestCase):
    def test_documentation_objective_uses_documentation_flow(self):
        context = ModernizationContext(user_objective="generate documentation")
        workflow = WorkflowPlanner().plan(context)
        self.assertIn("document", [step["step"] for step in workflow])

    def test_dependency_objective_uses_dependency_flow(self):
        context = ModernizationContext(user_objective="modernize dependencies")
        workflow = WorkflowPlanner().plan(context)
        self.assertIn("analyze_dependencies", [step["step"] for step in workflow])


if __name__ == "__main__":
    unittest.main()
