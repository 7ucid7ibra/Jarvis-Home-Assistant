import unittest

from jarvis_assistant.infrastructure.web_search_adapter import DuckDuckGoWebSearchAdapter


class FakeResponse:
    def __init__(self, text="", payload=None):
        self.text = text
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class WebSearchAdapterTests(unittest.TestCase):
    def test_does_not_call_network_when_disabled(self):
        calls = []
        adapter = DuckDuckGoWebSearchAdapter(
            enabled=lambda: False,
            get=lambda *args, **kwargs: calls.append((args, kwargs)),
        )

        result = adapter.search("weather")

        self.assertEqual(result["status"], "error")
        self.assertEqual(calls, [])

    def test_parses_duckduckgo_result_and_unwraps_redirect(self):
        html = (
            '<a class="result__a" href="/l/?uddg=https%3A%2F%2Fexample.com">'
            "Example <b>result</b></a>"
            '<div class="result__snippet">Useful <b>snippet</b></div>'
        )
        adapter = DuckDuckGoWebSearchAdapter(
            enabled=lambda: True,
            get=lambda *args, **kwargs: FakeResponse(text=html),
        )

        result = adapter.search("example")

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["results"],
            [{"title": "Example result", "url": "https://example.com", "snippet": "Useful snippet"}],
        )

    def test_uses_wikipedia_fallback_when_primary_has_no_results(self):
        responses = [
            FakeResponse(text="no results"),
            FakeResponse(payload=["query", ["Example"], ["Description"], ["https://example.com"]]),
        ]
        adapter = DuckDuckGoWebSearchAdapter(
            enabled=lambda: True,
            get=lambda *args, **kwargs: responses.pop(0),
        )

        result = adapter.search("example")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["results"][0]["title"], "Example")


if __name__ == "__main__":
    unittest.main()
