"""Generic verification engine with a simple plugin-friendly interface."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerificationEngine:
    checks: list[dict[str, Any]] = field(default_factory=list)

    def add_check(self, name: str, check_fn: Any) -> None:
        self.checks.append({"name": name, "check_fn": check_fn})

    def run(self, context: Any) -> dict[str, Any]:
        results: dict[str, Any] = {}
        for check in self.checks:
            name = check["name"]
            fn = check["check_fn"]
            results[name] = fn(context)
        return results
