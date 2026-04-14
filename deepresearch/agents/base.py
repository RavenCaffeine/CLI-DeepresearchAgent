"""
Base Agent

Defines the abstract interface that all research agents must implement.
Inspired by OpenClaw-style agent architecture with consistent run/stream contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..llm.base import BaseLLM
from ..prompts.loader import PromptLoader


class BaseAgent(ABC):
    """
    Abstract base class for all research agents.

    Each agent receives an LLM and a shared state dict, mutates the state,
    and returns it. This contract keeps nodes in the LangGraph workflow
    composable and easy to test in isolation.
    """

    def __init__(self, llm: BaseLLM) -> None:
        self.llm = llm
        self.prompt_loader = PromptLoader()

    # ------------------------------------------------------------------
    # Core contract
    # ------------------------------------------------------------------

    @abstractmethod
    def run(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's primary task given the current workflow state.

        Args:
            state: Shared LangGraph state dict (mutated in-place is OK).
            **kwargs: Agent-specific extra parameters.

        Returns:
            Updated state dict.
        """
        ...

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _generate(self, prompt: str, **kwargs) -> str:
        """Thin wrapper around the LLM so subclasses stay provider-agnostic."""
        return self.llm.generate(prompt, **kwargs)

    def _load_prompt(self, template_name: str, **context) -> str:
        """Load and render a named prompt template."""
        return self.prompt_loader.load(template_name, **context)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(llm={self.llm!r})"
