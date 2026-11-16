from dataclasses import dataclass
from typing import Any, Literal, TypeAlias


@dataclass(frozen=True)
class ConversationOutcome:
    kind: Literal["conversation"]
    text: str


@dataclass(frozen=True)
class ActionOutcome:
    kind: Literal["action"]
    name: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ClarificationOutcome:
    kind: Literal["clarification"]
    reason: str
    text: str


ResponseOutcome: TypeAlias = ConversationOutcome | ActionOutcome | ClarificationOutcome
