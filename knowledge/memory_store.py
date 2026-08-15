"""Simple in-memory store for run outcomes and repair patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryStore:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def remember(self, key: str, value: Any) -> None:
        self.entries.append({"key": key, "value": value})

    def recall(self, key: str) -> list[Any]:
        return [entry["value"] for entry in self.entries if entry["key"] == key]
