import unittest

from jarvis_assistant.application.intent_parser import IntentResponseParser
from jarvis_assistant.domain.outcomes import (
    ActionOutcome,
    ClarificationOutcome,
    ConversationOutcome,
)


class IntentResponseParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = IntentResponseParser()

    def test_parses_structured_json(self):
        result = self.parser.parse('{"intent": "help"}')

        self.assertEqual(result.kind, "structured")
        self.assertEqual(result.data, {"intent": "help"})
        self.assertEqual(result.outcome, ActionOutcome("action", "intent", {"intent": "help"}))

    def test_parses_fenced_json(self):
        result = self.parser.parse('```json\n{"action": "remember"}\n```')

        self.assertEqual(result.kind, "structured")
        self.assertEqual(result.data, {"action": "remember"})

    def test_parses_web_search_tool_call(self):
        response = (
            '<invoke name="web_search">'
            '<parameter name="query">latest weather</parameter>'
            "</invoke>"
        )

        result = self.parser.parse(response)

        self.assertEqual(result.kind, "web_search")
        self.assertEqual(result.query, "latest weather")
        self.assertEqual(
            result.outcome,
            ActionOutcome("action", "web_search", {"query": "latest weather"}),
        )

    def test_classifies_normal_text_as_conversation(self):
        result = self.parser.parse("The answer is forty-two.")

        self.assertEqual(result.kind, "conversation")
        self.assertEqual(result.text, "The answer is forty-two.")
        self.assertEqual(
            result.outcome,
            ConversationOutcome("conversation", "The answer is forty-two."),
        )

    def test_rejects_control_like_plain_text(self):
        result = self.parser.parse(
            "Done.",
            user_text="Turn on the table lamp",
            entities=[{"name": "table lamp", "domain": "light"}],
        )

        self.assertEqual(result.kind, "unsafe_control")
        self.assertEqual(
            result.outcome,
            ClarificationOutcome(
                "clarification",
                "control_command_without_structured_intent",
                "Done.",
            ),
        )


if __name__ == "__main__":
    unittest.main()
