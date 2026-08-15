"""Confidence scoring for modernization decisions and outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ConfidenceEngine:
    proceed_threshold: float = 0.85
    warn_threshold: float = 0.60

    def score(self, evidence: dict[str, Any]) -> float:
        confidence = evidence.get("confidence")
        if isinstance(confidence, (int, float)):
            return max(0.0, min(1.0, float(confidence)))
        return 0.0

    def should_proceed(self, confidence: float) -> bool:
        return confidence >= self.proceed_threshold

    def should_warn(self, confidence: float) -> bool:
        return self.warn_threshold <= confidence < self.proceed_threshold

    def decide(self, confidence: float) -> str:
        if confidence >= self.proceed_threshold:
            return "proceed"
        if confidence >= self.warn_threshold:
            return "warn"
        return "confirm"
