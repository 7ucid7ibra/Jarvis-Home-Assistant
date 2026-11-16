from ..domain.ports import HomeAssistantPort


class LegacyHomeAssistantAdapter(HomeAssistantPort):
    """Expose the legacy Home Assistant client through the application port."""

    def __init__(self, client):
        self._client = client

    def call_service(self, domain: str, service: str, data: dict) -> list:
        return self._client.call_service(domain, service, data)

    def get_entity_state(self, entity_id: str) -> dict:
        return self._client.get_entity_state(entity_id)
