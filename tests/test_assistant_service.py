from dataclasses import dataclass, field
import unittest

from jarvis_assistant.application import AssistantService
from jarvis_assistant.application import IntentPromptBuilder
from jarvis_assistant.application.domain_error import EmptyUserInputError
from jarvis_assistant.domain import ConversationMessage


@dataclass
class InMemoryConversation:
    entries: list[ConversationMessage] = field(default_factory=list)

    def messages(self):
        return tuple(self.entries)

    def append(self, message: ConversationMessage) -> None:
        self.entries.append(message)


class EchoGenerator:
    def generate(self, messages):
        assert messages[-1].role == "user"
        return f"Echo: {messages[-1].content}"


class AssistantServiceTests(unittest.TestCase):
    def test_begin_user_turn_normalizes_and_persists_input(self):
        conversation = InMemoryConversation()
        service = AssistantService(conversation)

        text = service.begin_user_turn("  Turn on the lamp  ")

        self.assertEqual(text, "Turn on the lamp")
        self.assertEqual(
            conversation.entries,
            [ConversationMessage("user", "Turn on the lamp")],
        )

    def test_complete_assistant_turn_normalizes_and_persists_response(self):
        conversation = InMemoryConversation()
        service = AssistantService(conversation)

        response = service.complete_assistant_turn("  Done.  ")

        self.assertEqual(response, "Done.")
        self.assertEqual(
            conversation.entries,
            [ConversationMessage("assistant", "Done.")],
        )

    def test_intent_prompt_builder_preserves_history_order(self):
        calls = []

        def build_system_prompt(**kwargs):
            calls.append(kwargs)
            return "system prompt"

        builder = IntentPromptBuilder(build_system_prompt)
        history = [{"role": "user", "content": "Earlier"}]

        messages = builder.build(
            history=history,
            user_text="Turn on the lamp",
            entities_context="light.lamp",
            memory_context="",
            capabilities="home control",
            time_context="2026-11-16 12:00",
        )

        self.assertEqual(
            messages,
            [
                {"role": "system", "content": "system prompt"},
                {"role": "user", "content": "Earlier"},
                {"role": "user", "content": "Turn on the lamp"},
            ],
        )
        self.assertEqual(calls[0]["entities_context"], "light.lamp")

    def test_handle_text_persists_both_sides_of_a_turn(self):
        conversation = InMemoryConversation()
        service = AssistantService(conversation, EchoGenerator())

        turn = service.handle_text("  Hello Jarvis  ")

        self.assertEqual(turn.user_text, "Hello Jarvis")
        self.assertEqual(turn.assistant_text, "Echo: Hello Jarvis")
        self.assertEqual(conversation.entries, [
            ConversationMessage("user", "Hello Jarvis"),
            ConversationMessage("assistant", "Echo: Hello Jarvis"),
        ])

    def test_handle_text_rejects_blank_input_without_mutating_history(self):
        conversation = InMemoryConversation()
        service = AssistantService(conversation, EchoGenerator())

        with self.assertRaises(EmptyUserInputError):
            service.handle_text("  \n\t")

        self.assertEqual(conversation.entries, [])


if __name__ == "__main__":
    unittest.main()
