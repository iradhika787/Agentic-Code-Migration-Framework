"""Core framework primitives for agentic software modernization."""

from .context import ModernizationContext
from .confidence_engine import ConfidenceEngine
from .interfaces import (
    Agent,
    Capability,
    LLMProvider,
    ModernizationPlugin,
    VerificationStrategy,
)
