"""Persistence and secret-store collaborators for the legacy Config facade."""

import json
import os
from collections.abc import Mapping
from typing import Any, Protocol

from ..core import secret_store


class SecretBackend(Protocol):
    def get_secret(self, key: str) -> str | None: ...
    def set_secret(self, key: str, value: str) -> None: ...
    def delete_secret(self, key: str) -> None: ...
    def is_available(self) -> bool: ...


class DefaultSecretBackend:
    def get_secret(self, key: str) -> str | None:
        return secret_store.get_secret(key)

    def set_secret(self, key: str, value: str) -> None:
        secret_store.set_secret(key, value)

    def delete_secret(self, key: str) -> None:
        secret_store.delete_secret(key)

    def is_available(self) -> bool:
        return secret_store.is_available()


class JsonSettingsStore:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> dict[str, Any]:
        try:
            with open(self.path, encoding="utf-8") as handle:
                payload = json.load(handle)
            return payload if isinstance(payload, dict) else {}
        except (OSError, ValueError, TypeError):
            return {}

    def save(self, settings: Mapping[str, Any]) -> None:
        parent_dir = os.path.dirname(self.path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(dict(settings), handle, indent=2)
