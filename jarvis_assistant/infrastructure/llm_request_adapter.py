from typing import Protocol

from ..domain.ports import AsyncTextGeneratorPort


class SignalEmitter(Protocol):
    def emit(self, messages: list[dict], response_format: str) -> None:
        """Emit a request to the legacy Qt worker signal."""


class QtLLMRequestAdapter(AsyncTextGeneratorPort):
    """Keep Qt signal mechanics outside application code."""

    def __init__(self, emitter: SignalEmitter):
        self._emitter = emitter

    def request(self, messages: list[dict], response_format: str = "json") -> None:
        self._emitter.emit(messages, response_format)
