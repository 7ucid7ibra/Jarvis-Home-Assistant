"""Adapt the legacy conversation store to the domain conversation port."""

from ..integrations.conversation import Conversation
from ..domain import ConversationMessage, ConversationPort


class LegacyConversationAdapter(ConversationPort):
    """Keep the existing JSON-backed Conversation usable during migration."""

    def __init__(self, conversation: Conversation) -> None:
        self._conversation = conversation

    def messages(self) -> tuple[ConversationMessage, ...]:
        return tuple(
            ConversationMessage(message.role, message.content)
            for message in self._conversation.messages
        )

    def append(self, message: ConversationMessage) -> None:
        self._conversation.add_message(message.role, message.content)
