import unittest

from jarvis_assistant.infrastructure.telegram_adapter import TelegramBotAdapter


class FakeResponse:
    def raise_for_status(self):
        return None


class TelegramAdapterTests(unittest.TestCase):
    def test_rejects_missing_credentials_without_sending(self):
        calls = []
        adapter = TelegramBotAdapter(
            credentials=lambda: ("", ""),
            post=lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        result = adapter.send("Hello")

        self.assertEqual(result["status"], "error")
        self.assertEqual(calls, [])

    def test_forwards_message_to_configured_client(self):
        calls = []

        def post(*args, **kwargs):
            calls.append((args, kwargs))
            return FakeResponse()

        adapter = TelegramBotAdapter(
            credentials=lambda: ("test-token", "chat-1"),
            post=post,
        )

        result = adapter.send("Hello")

        self.assertEqual(result, {"status": "success"})
        self.assertIn("sendMessage", calls[0][0][0])
        self.assertEqual(calls[0][1]["json"], {"chat_id": "chat-1", "text": "Hello"})


if __name__ == "__main__":
    unittest.main()
