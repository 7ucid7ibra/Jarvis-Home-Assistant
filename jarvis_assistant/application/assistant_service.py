"""Headless orchestration for one text conversation turn."""

from .domain_error import EmptyUserInputError
from ..domain import (
    AssistantTurn,
    ConversationMessage,
    ConversationPort,
    TextGeneratorPort,
)


class AssistantService:
    """Coordinate conversation storage and text generation.

    The service deliberately knows nothing about Qt, audio, network clients,
    or configuration. Those concerns can be adapted to its two ports.
    """

    def __init__(
        self,
        conversation: ConversationPort,
        generator: TextGeneratorPort | None = None,
    ) -> None:
        self._conversation = conversation
        self._generator = generator

    def begin_user_turn(self, user_text: str) -> str:
        """Validate and persist user input before asynchronous processing."""
        text = user_text.strip()
        if not text:
            raise EmptyUserInputError("User input cannot be empty.")
        self._conversation.append(ConversationMessage("user", text))
        return text

    def complete_assistant_turn(self, assistant_text: str) -> str:
        """Persist a completed assistant response."""
        response = assistant_text.strip()
        self._conversation.append(ConversationMessage("assistant", response))
        return response

    def handle_text(self, user_text: str) -> AssistantTurn:
        if self._generator is None:
            raise RuntimeError("A text generator is required for handle_text().")

        text = self.begin_user_turn(user_text)
        response = self._generator.generate(self._conversation.messages())
        response = self.complete_assistant_turn(response)
        return AssistantTurn(user_text=text, assistant_text=response)
