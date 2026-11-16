"""Dependency boundaries for the UI-independent assistant core."""

from collections.abc import Callable
from typing import Protocol, Sequence

from .turns import ConversationMessage


class ConversationPort(Protocol):
    def messages(self) -> Sequence[ConversationMessage]:
        """Return the current conversation in chronological order."""

    def append(self, message: ConversationMessage) -> None:
        """Persist one conversation message."""


class TextGeneratorPort(Protocol):
    def generate(self, messages: Sequence[ConversationMessage]) -> str:
        """Generate an assistant response for the supplied conversation."""


class AsyncTextGeneratorPort(Protocol):
    def request(self, messages: list[dict], response_format: str = "json") -> None:
        """Submit a generation request to an externally managed worker."""


class HomeAssistantPort(Protocol):
    def call_service(self, domain: str, service: str, data: dict) -> list:
        """Call one Home Assistant service."""

    def get_entity_state(self, entity_id: str) -> dict:
        """Read one Home Assistant entity state."""


class MemoryPort(Protocol):
    def add_fact(self, key: str, value: str) -> None:
        """Persist one user fact."""

    def get_all_context(self) -> str:
        """Return facts formatted for an LLM prompt."""


class WebSearchPort(Protocol):
    def search(self, query: str, max_results: int = 3) -> dict:
        """Search the web and return a user-safe result payload."""


class TelegramPort(Protocol):
    def send(self, message: str) -> dict:
        """Send a configured Telegram message."""


class TaskSchedulerPort(Protocol):
    def schedule(self, delay_ms: int, task: Callable[[], None]) -> object:
        """Schedule a callback and retain it until it has run."""
