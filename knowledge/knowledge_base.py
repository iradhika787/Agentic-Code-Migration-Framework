"""Simple knowledge base for reusable modernization rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnowledgeBase:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def add_entry(self, category: str, rule: str, confidence: float = 0.8) -> None:
        self.entries.append({"category": category, "rule": rule, "confidence": confidence})

    def search(self, category: str) -> list[dict[str, Any]]:
        return [entry for entry in self.entries if entry["category"] == category]
