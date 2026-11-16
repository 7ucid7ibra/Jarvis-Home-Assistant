import unittest

from jarvis_assistant.application import (
    AssistantService,
    IntentPromptBuilder,
    IntentRequestService,
    IntentResponseParser,
)
from jarvis_assistant.domain import ConversationMessage


class InMemoryConversation:
    def __init__(self):
        self.items = []

    def messages(self):
        return tuple(self.items)

    def append(self, message):
        self.items.append(message)


class FakeIntentGenerator:
    def __init__(self):
        self.requests = []

    def request(self, messages, response_format="json"):
        self.requests.append((messages, response_format))


class HeadlessTextFlowTests(unittest.TestCase):
    def test_text_turn_builds_intent_request_and_persists_direct_reply(self):
        conversation = InMemoryConversation()
        assistant = AssistantService(conversation)
        generator = FakeIntentGenerator()
        builder = IntentPromptBuilder(
            lambda **_: "Classify the request and return JSON when needed."
        )
        request_service = IntentRequestService(builder, generator)
        parser = IntentResponseParser()

        user_text = assistant.begin_user_turn("  What can you do?  ")
        request_service.submit(
            history=[{"role": "user", "content": user_text}],
            user_text=user_text,
            entities_context="",
            memory_context="No specific user facts known yet.",
            capabilities="help",
            time_context="",
        )
        outcome = parser.parse("I can control your connected home devices.")
        reply = assistant.complete_assistant_turn(outcome.text)

        self.assertEqual(generator.requests[0][1], "json")
        self.assertEqual(generator.requests[0][0][-1], {"role": "user", "content": user_text})
        self.assertEqual(outcome.kind, "conversation")
        self.assertEqual(reply, "I can control your connected home devices.")
        self.assertEqual(
            conversation.messages(),
            (
                ConversationMessage("user", "What can you do?"),
                ConversationMessage("assistant", reply),
            ),
        )


if __name__ == "__main__":
    unittest.main()
