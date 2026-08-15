"""Dynamic workflow planning primitives."""

from __future__ import annotations

from dataclasses import dataclass, field

from .context import ModernizationContext


@dataclass
class WorkflowPlanner:
    def plan(self, context: ModernizationContext) -> list[dict[str, object]]:
        if context.workflow_plan:
            return context.workflow_plan

        objective = (context.user_objective or "").lower()
        plugins = context.selected_plugins or []
        if "documentation" in objective:
            workflow = [
                {"step": "discover", "agent": "ProjectDiscoveryAgent"},
                {"step": "detect", "agent": "TechnologyDetectionAgent"},
                {"step": "gather_knowledge", "agent": "KnowledgeRetrievalAgent"},
                {"step": "document", "agent": "DocumentationAgent"},
                {"step": "report", "agent": "ReportingAgent"},
            ]
        elif "dependency" in objective or "dependencies" in objective or "dependency" in plugins:
            workflow = [
                {"step": "discover", "agent": "ProjectDiscoveryAgent"},
                {"step": "detect", "agent": "TechnologyDetectionAgent"},
                {"step": "analyze_dependencies", "agent": "DependencyAnalysisAgent"},
                {"step": "execute", "agent": "ExecutionAgent"},
                {"step": "verify", "agent": "VerificationAgent"},
                {"step": "report", "agent": "ReportingAgent"},
            ]
        else:
            workflow = [
                {"step": "discover", "agent": "ProjectDiscoveryAgent"},
                {"step": "detect", "agent": "TechnologyDetectionAgent"},
                {"step": "decide", "agent": "PlanningAgent"},
                {"step": "execute", "agent": "ExecutionAgent"},
                {"step": "verify", "agent": "VerificationAgent"},
                {"step": "report", "agent": "ReportingAgent"},
            ]

        context.workflow_plan = workflow
        return workflow
