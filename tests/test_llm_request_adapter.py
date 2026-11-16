import unittest

from jarvis_assistant.infrastructure.llm_request_adapter import QtLLMRequestAdapter


class FakeEmitter:
    def __init__(self):
        self.calls = []

    def emit(self, messages, response_format):
        self.calls.append((messages, response_format))


class LLMRequestAdapterTests(unittest.TestCase):
    def test_forwards_messages_and_format_to_legacy_signal(self):
        emitter = FakeEmitter()
        adapter = QtLLMRequestAdapter(emitter)
        messages = [{"role": "user", "content": "Hello"}]

        adapter.request(messages, "text")

        self.assertEqual(emitter.calls, [(messages, "text")])


if __name__ == "__main__":
    unittest.main()
