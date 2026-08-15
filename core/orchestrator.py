"""Generic orchestration facade for modernization workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .confidence_engine import ConfidenceEngine
from .context import ModernizationContext
from .workflow_planner import WorkflowPlanner


@dataclass
class FrameworkOrchestrator:
    planner: WorkflowPlanner = field(default_factory=WorkflowPlanner)
    confidence_engine: ConfidenceEngine = field(default_factory=ConfidenceEngine)

    def build_context(
        self,
        source_code: str,
        *,
        project_path: str | None = None,
        user_objective: str | None = None,
        expected_output: str | None = None,
    ) -> ModernizationContext:
        context = ModernizationContext(
            project_path=project_path,
            user_objective=user_objective,
        )
        context.agent_outputs["source_code"] = source_code
        if expected_output is not None:
            context.final_report_data["expected_output"] = expected_output
        context.workflow_plan = self.planner.plan(context)
        return context

    def run(self, context: ModernizationContext) -> ModernizationContext:
        context.logs.append("Framework orchestrator initialized.")
        context.workflow_plan = self.planner.plan(context)
        confidence = self.confidence_engine.score(
            {"confidence": context.confidence_scores.get("overall", 0.0)}
        )
        context.confidence_scores["overall"] = confidence
        decision = self.confidence_engine.decide(confidence)
        context.final_report_data["confidence"] = confidence
        context.final_report_data["decision"] = decision
        context.logs.append(f"Confidence decision: {decision} ({confidence:.2f})")
        return context
