"""Headless orchestration for an intent-model request."""

from collections.abc import Sequence
from typing import Any

from ..domain.ports import AsyncTextGeneratorPort
from .intent_prompt import IntentPromptBuilder


class IntentRequestService:
    """Build and submit intent requests without Qt controller dependencies."""

    def __init__(
        self,
        prompt_builder: IntentPromptBuilder,
        generator: AsyncTextGeneratorPort,
    ) -> None:
        self._prompt_builder = prompt_builder
        self._generator = generator

    def submit(
        self,
        *,
        history: Sequence[dict[str, Any]],
        user_text: str,
        entities_context: str,
        memory_context: str,
        capabilities: str,
        time_context: str,
    ) -> list[dict[str, Any]]:
        messages = self._prompt_builder.build(
            history=history,
            user_text=user_text,
            entities_context=entities_context,
            memory_context=memory_context,
            capabilities=capabilities,
            time_context=time_context,
        )
        self._generator.request(messages, "json")
        return messages
