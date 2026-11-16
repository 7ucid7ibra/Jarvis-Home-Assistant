import unittest

from jarvis_assistant.infrastructure.home_assistant_adapter import (
    LegacyHomeAssistantAdapter,
)


class FakeHomeAssistantClient:
    def __init__(self):
        self.calls = []

    def call_service(self, domain, service, data):
        self.calls.append((domain, service, data))
        return [{"entity_id": data["entity_id"]}]


class HomeAssistantAdapterTests(unittest.TestCase):
    def test_forwards_service_calls_to_legacy_client(self):
        client = FakeHomeAssistantClient()
        adapter = LegacyHomeAssistantAdapter(client)
        payload = {"entity_id": "light.desk"}

        result = adapter.call_service("light", "turn_on", payload)

        self.assertEqual(client.calls, [("light", "turn_on", payload)])
        self.assertEqual(result, [{"entity_id": "light.desk"}])


if __name__ == "__main__":
    unittest.main()
