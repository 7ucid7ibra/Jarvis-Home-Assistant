import unittest

from jarvis_assistant.application.home_assistant_actions import HomeAssistantActionService


class FakeHomeAssistant:
    def __init__(self):
        self.state = "off"
        self.calls = []

    def get_entity_state(self, entity_id):
        return {"state": self.state}

    def call_service(self, domain, service, data):
        self.calls.append((domain, service, data))
        if service == "turn_on":
            self.state = "on"
        return []


class FailingHomeAssistant(FakeHomeAssistant):
    def get_entity_state(self, entity_id):
        raise RuntimeError("connection failed")


class Clock:
    def __init__(self):
        self.value = 0.0

    def now(self):
        return self.value

    def sleep(self, seconds):
        self.value += seconds


class HomeAssistantActionServiceTests(unittest.TestCase):
    def test_executes_and_verifies_turn_on(self):
        client = FakeHomeAssistant()
        service = HomeAssistantActionService(client)

        result = service.execute(
            {"domain": "light", "service": "turn_on", "entity_id": "light.desk"}
        )

        self.assertTrue(result["verified"])
        self.assertEqual(result["final_states"], {"light.desk": "on"})
        self.assertEqual(
            client.calls,
            [("light", "turn_on", {"entity_id": "light.desk"})],
        )

    def test_rejects_unsupported_service_without_calling_client(self):
        client = FakeHomeAssistant()
        service = HomeAssistantActionService(client)

        result = service.execute(
            {"domain": "light", "service": "open", "entity_id": "light.desk"}
        )

        self.assertIn("not supported", result["error"])
        self.assertEqual(client.calls, [])

    def test_returns_error_when_initial_state_lookup_fails(self):
        client = FailingHomeAssistant()
        service = HomeAssistantActionService(client)

        result = service.execute(
            {"domain": "light", "service": "turn_on", "entity_id": "light.desk"}
        )

        self.assertEqual(result["error"], "connection failed")

    def test_reports_unverified_action_after_timeout(self):
        client = FakeHomeAssistant()
        client.state = "on"
        clock = Clock()
        service = HomeAssistantActionService(
            client,
            clock=clock.now,
            sleep=clock.sleep,
            verification_timeout=1.0,
            poll_interval=0.5,
        )

        result = service.execute(
            {"domain": "light", "service": "turn_off", "entity_id": "light.desk"}
        )

        self.assertFalse(result["verified"])
        self.assertEqual(result["final_states"], {"light.desk": "on"})


if __name__ == "__main__":
    unittest.main()
