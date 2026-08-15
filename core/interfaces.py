"""Framework interfaces used across agents, plugins, and providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .context import ModernizationContext


@runtime_checkable
class Agent(Protocol):
    name: str

    def run(self, context: ModernizationContext) -> Any:
        ...


@runtime_checkable
class Capability(Protocol):
    name: str

    def supports(self, context: ModernizationContext) -> bool:
        ...


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    source_technology: str
    target_technology: str
    version: str = "0.1.0"


@runtime_checkable
class ModernizationPlugin(Protocol):
    metadata: PluginMetadata

    def detect(self, context: ModernizationContext) -> dict[str, Any]:
        ...

    def analyze(self, context: ModernizationContext) -> dict[str, Any]:
        ...

    def plan(self, context: ModernizationContext) -> list[dict[str, Any]]:
        ...

    def execute(self, context: ModernizationContext) -> dict[str, Any]:
        ...

    def verify(self, context: ModernizationContext) -> dict[str, Any]:
        ...


@runtime_checkable
class VerificationStrategy(Protocol):
    name: str

    def verify(self, context: ModernizationContext) -> dict[str, Any]:
        ...


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    def generate(self, prompt: str, **kwargs: Any) -> str:
        ...
