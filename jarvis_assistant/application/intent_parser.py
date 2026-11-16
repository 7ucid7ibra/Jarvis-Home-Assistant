from dataclasses import dataclass
from typing import Any, Literal

from ..domain.outcomes import (
    ActionOutcome,
    ClarificationOutcome,
    ConversationOutcome,
    ResponseOutcome,
)
from ..intelligence.intent_utils import looks_like_home_control_request
from ..core.utils import extract_json, extract_tool_call_query


ParseKind = Literal["structured", "web_search", "unsafe_control", "conversation"]


@dataclass(frozen=True)
class IntentParseResult:
    kind: ParseKind
    data: dict[str, Any] | None = None
    query: str | None = None
    text: str = ""
    outcome: ResponseOutcome | None = None


class IntentResponseParser:
    """Classify an intent-agent response without performing any actions."""

    def parse(
        self,
        response: str,
        *,
        user_text: str = "",
        entities: list[dict[str, str]] | None = None,
    ) -> IntentParseResult:
        try:
            parsed = extract_json(response)
        except Exception:
            parsed = None

        if isinstance(parsed, dict) and any(
            key in parsed for key in ("intent", "action", "target")
        ):
            return IntentParseResult(
                kind="structured",
                data=parsed,
                text=response,
                outcome=ActionOutcome("action", "intent", parsed),
            )

        query = extract_tool_call_query(response, "web_search")
        if query:
            return IntentParseResult(
                kind="web_search",
                query=query,
                text=response,
                outcome=ActionOutcome("action", "web_search", {"query": query}),
            )

        if looks_like_home_control_request(user_text, entities or []):
            return IntentParseResult(
                kind="unsafe_control",
                text=response,
                outcome=ClarificationOutcome(
                    "clarification",
                    "control_command_without_structured_intent",
                    response,
                ),
            )

        return IntentParseResult(
            kind="conversation",
            text=response,
            outcome=ConversationOutcome("conversation", response),
        )
