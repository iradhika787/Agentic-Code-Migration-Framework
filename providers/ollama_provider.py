"""Ollama provider adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class OllamaProvider:
    model: str = "qwen2.5-coder:7b"
    host: str = "http://localhost:11434"

    @property
    def name(self) -> str:
        return "ollama"

    def generate(self, prompt: str, **kwargs: Any) -> str:
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=kwargs.get("timeout", 120),
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("response", "")
