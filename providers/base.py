"""Provider abstraction for LLM integrations."""

from __future__ import annotations

from typing import Protocol, Any


class Provider(Protocol):
    name: str

    def generate(self, prompt: str, **kwargs: Any) -> str:
        ...
