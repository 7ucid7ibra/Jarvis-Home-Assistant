import unittest

from jarvis_assistant.infrastructure.provider_clients import LMStudioClient, OllamaClient, ProviderRequestError


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = "request failed"
        self.reason = "request failed"

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class ProviderClientTests(unittest.TestCase):
    def test_ollama_generation_uses_chat_endpoint_and_json_format(self):
        calls = []

        def get(url, **kwargs):
            calls.append(("get", url, kwargs))
            return FakeResponse({"models": []})

        def post(url, **kwargs):
            calls.append(("post", url, kwargs))
            return FakeResponse({"message": {"content": "ready"}})

        client = OllamaClient("http://127.0.0.1:11434", get=get, post=post)
        reply = client.generate("jarvis", [{"role": "user", "content": "hello"}], "json")

        self.assertEqual("ready", reply)
        self.assertEqual("http://127.0.0.1:11434/api/chat", calls[-1][1])
        self.assertEqual("json", calls[-1][2]["json"]["format"])

    def test_ollama_remote_unavailable_has_recovery_marker(self):
        def get(url, **kwargs):
            raise OSError("offline")

        client = OllamaClient("http://jarvis.example:11434", get=get)
        with self.assertRaisesRegex(ProviderRequestError, "__OLLAMA_REMOTE_UNREACHABLE__"):
            client.generate("jarvis", [], "json")

    def test_lmstudio_checks_visible_model_before_generation(self):
        calls = []

        def get(url, **kwargs):
            calls.append(url)
            if url.endswith("/v1/models"):
                return FakeResponse({"data": [{"id": "loaded-model"}]})
            return FakeResponse({"data": []})

        client = LMStudioClient("http://127.0.0.1:1234", get=get)
        with self.assertRaisesRegex(ProviderRequestError, "model id mismatch"):
            client.generate("other-model", [])

    def test_lmstudio_generation_uses_openai_compatible_endpoint(self):
        def get(url, **kwargs):
            return FakeResponse({"data": [{"id": "loaded-model"}]})

        captured = {}

        def post(url, **kwargs):
            captured["url"] = url
            captured["payload"] = kwargs["json"]
            return FakeResponse({"choices": [{"message": {"content": "ready"}}]})

        client = LMStudioClient("http://127.0.0.1:1234", get=get, post=post)
        self.assertEqual("ready", client.generate("loaded-model", [{"role": "user", "content": "hello"}]))
        self.assertEqual("http://127.0.0.1:1234/v1/chat/completions", captured["url"])
        self.assertNotIn("response_format", captured["payload"])


if __name__ == "__main__":
    unittest.main()
