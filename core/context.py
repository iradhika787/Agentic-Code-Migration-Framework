"""Shared execution state for a modernization run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModernizationContext:
    project_path: str | None = None
    file_inventory: list[str] = field(default_factory=list)
    detected_languages: list[dict[str, Any]] = field(default_factory=list)
    detected_frameworks: list[dict[str, Any]] = field(default_factory=list)
    detected_dependencies: list[dict[str, Any]] = field(default_factory=list)
    detected_versions: dict[str, Any] = field(default_factory=dict)
    user_objective: str | None = None
    selected_capabilities: list[str] = field(default_factory=list)
    selected_plugins: list[str] = field(default_factory=list)
    selected_provider: str | None = None
    selected_model: str | None = None
    knowledge_retrieved: list[dict[str, Any]] = field(default_factory=list)
    workflow_plan: list[dict[str, Any]] = field(default_factory=list)
    agent_outputs: dict[str, Any] = field(default_factory=dict)
    proposed_changes: list[dict[str, Any]] = field(default_factory=list)
    diffs: list[str] = field(default_factory=list)
    verification_results: list[dict[str, Any]] = field(default_factory=list)
    retry_history: list[dict[str, Any]] = field(default_factory=list)
    confidence_scores: dict[str, float] = field(default_factory=dict)
    logs: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    final_report_data: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
