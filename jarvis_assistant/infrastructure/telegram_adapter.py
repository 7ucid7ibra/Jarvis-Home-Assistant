from collections.abc import Callable

import requests

from ..domain.ports import TelegramPort


class TelegramBotAdapter(TelegramPort):
    """Legacy Telegram Bot API sender with runtime-resolved credentials."""

    def __init__(
        self,
        credentials: Callable[[], tuple[str, str]],
        *,
        post: Callable = requests.post,
    ) -> None:
        self._credentials = credentials
        self._post = post

    def send(self, message: str) -> dict:
        token, chat_id = self._credentials()
        if not token or not chat_id:
            return {"status": "error", "error": "Telegram token or chat ID is not set."}
        if not message:
            return {"status": "error", "error": "Message is empty."}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            response = self._post(
                url,
                json={"chat_id": chat_id, "text": message},
                timeout=10,
            )
            response.raise_for_status()
            return {"status": "success"}
        except Exception as exc:
            return {"status": "error", "error": str(exc)}
