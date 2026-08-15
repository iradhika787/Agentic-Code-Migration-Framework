"""Provider-independent LLM abstraction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .interfaces import LLMProvider


@dataclass
class EchoProvider:
    """Fallback provider used until a real backend is selected."""

    name: str = "echo"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return prompt
