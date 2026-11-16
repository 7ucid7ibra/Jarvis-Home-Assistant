"""Data passed through the headless assistant workflow."""

from dataclasses import dataclass
from typing import Literal

Role = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class ConversationMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class AssistantTurn:
    user_text: str
    assistant_text: str

