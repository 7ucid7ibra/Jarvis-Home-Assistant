import time
from collections.abc import Callable

from ..domain.ports import HomeAssistantPort
from ..intelligence.intent_utils import state_matches_action


class HomeAssistantActionService:
    """Execute and verify a supported Home Assistant service call."""

    VALID_SERVICES = {"turn_on", "turn_off", "toggle", "set_value"}

    def __init__(
        self,
        client: HomeAssistantPort,
        *,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
        verification_timeout: float = 5.0,
        poll_interval: float = 0.5,
    ) -> None:
        self._client = client
        self._clock = clock
        self._sleep = sleep
        self._verification_timeout = verification_timeout
        self._poll_interval = poll_interval

    def execute(self, action: dict) -> dict:
        service = action.get("service")
        if service not in self.VALID_SERVICES:
            return {
                "error": (
                    f"Service '{service}' is not supported. I can only turn on, "
                    "turn off, toggle, or set a value."
                ),
                "action": action,
            }
        if service == "set_value":
            if action.get("domain") != "input_number":
                return {"error": "set_value is only supported for input_number.", "action": action}
            if action.get("value") is None:
                return {"error": "No value provided for input_number.", "action": action}

        try:
            target_ids = action.get("entity_id")
            if isinstance(target_ids, str):
                target_ids = [target_ids]
            if not target_ids:
                return {"error": "No target entity provided.", "action": action}

            initial_states = {
                entity_id: self._client.get_entity_state(entity_id).get("state")
                for entity_id in target_ids
            }
            payload = {"entity_id": action.get("entity_id")}
            if service == "set_value":
                value = action.get("value")
                if isinstance(value, str):
                    try:
                        value = float(value)
                        if value.is_integer():
                            value = int(value)
                    except Exception:
                        return {"error": "Value must be numeric for input_number.", "action": action}
                payload["value"] = value

            self._client.call_service(action.get("domain"), service, payload)

            deadline = self._clock() + self._verification_timeout
            final_states = {}
            verified = False
            while True:
                all_match = True
                for entity_id in target_ids:
                    try:
                        new_state = self._client.get_entity_state(entity_id).get("state", "unknown")
                    except Exception:
                        new_state = "unknown"
                    final_states[entity_id] = new_state
                    if not state_matches_action(
                        service,
                        initial_states.get(entity_id),
                        new_state,
                        action.get("value"),
                    ):
                        all_match = False

                if all_match:
                    verified = True
                    break
                if self._clock() >= deadline:
                    break
                self._sleep(self._poll_interval)

            result = action.copy()
            result["verified"] = verified
            result["final_states"] = final_states
            return result
        except Exception as exc:
            return {"error": str(exc), "action": action}
