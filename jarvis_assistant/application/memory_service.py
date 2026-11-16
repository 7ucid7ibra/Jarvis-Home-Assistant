"""Use cases for durable assistant memory."""

from dataclasses import dataclass
from typing import Callable

from ..domain.ports import MemoryPort


@dataclass(frozen=True)
class MemoryWriteResult:
    stored: bool
    fact: str = ""
    key: str = ""


class MemoryService:
    """Extract and persist a fact while preserving legacy fact wording."""

    def __init__(self, memory: MemoryPort, clock: Callable[[], float]) -> None:
        self._memory = memory
        self._clock = clock

    def remember(self, user_text: str) -> MemoryWriteResult:
        fact = self._extract_fact(user_text)
        if len(fact) <= 2:
            return MemoryWriteResult(stored=False)

        key = f"fact_{int(self._clock())}"
        self._memory.add_fact(key, fact)
        return MemoryWriteResult(stored=True, fact=fact, key=key)

    @staticmethod
    def _extract_fact(user_text: str) -> str:
        fact = (user_text or "").strip()
        lower_text = fact.lower()
        if "remember that" in lower_text:
            index = lower_text.find("remember that") + len("remember that")
            return fact[index:].strip()
        if "remember" in lower_text:
            index = lower_text.find("remember") + len("remember")
            return fact[index:].strip()
        return fact
