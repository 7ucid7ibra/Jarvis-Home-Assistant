"""Build intent-model requests without coupling them to Qt."""

from collections.abc import Callable, Sequence
from typing import Any


class IntentPromptBuilder:
    """Compose the intent system prompt, conversation history, and user text."""

    def __init__(self, system_prompt_factory: Callable[..., str]) -> None:
        self._system_prompt_factory = system_prompt_factory

    def build(
        self,
        *,
        history: Sequence[dict[str, Any]],
        user_text: str,
        entities_context: str,
        memory_context: str,
        capabilities: str,
        time_context: str,
    ) -> list[dict[str, Any]]:
        system_prompt = self._system_prompt_factory(
            entities_context=entities_context,
            memory_context=memory_context,
            capabilities=capabilities,
            time_context=time_context,
        )
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})
        return messages

