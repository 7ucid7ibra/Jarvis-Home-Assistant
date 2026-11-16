"""HTTP clients for local model providers, independent of Qt workers."""

from __future__ import annotations

import json
import subprocess
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlparse

import requests


class ProviderRequestError(RuntimeError):
    """A provider request failed with a user-safe message."""


class OllamaClient:
    """Ollama's HTTP contract without UI signals or application settings."""

    def __init__(
        self,
        base_url: str,
        get: Callable[..., Any] = requests.get,
        post: Callable[..., Any] = requests.post,
        start_process: Callable[..., Any] = subprocess.Popen,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self._get = get
        self._post = post
        self._start_process = start_process
        self._sleep = sleep
        self._tried_start = False

    def url(self, path: str) -> str:
        return f"{self.base_url}/api/{path.lstrip('/')}"

    def is_local(self) -> bool:
        try:
            host = (urlparse(self.base_url).hostname or "").lower()
        except ValueError:
            return False
        return host in {"127.0.0.1", "localhost", "::1"}

    def is_available(self, start_if_local: bool = False) -> bool:
        try:
            if self._get(self.url("tags"), timeout=2).status_code == 200:
                return True
        except Exception:
            pass

        if not (start_if_local and self.is_local()) or self._tried_start:
            return False
        self._tried_start = True
        try:
            self._start_process(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._sleep(2)
            return self._get(self.url("tags"), timeout=3).status_code == 200
        except Exception:
            return False

    def test_connection(self) -> dict:
        if not self.base_url:
            return {"ok": False, "error": "Empty Ollama base URL"}
        try:
            response = self._get(self.url("tags"), timeout=5)
            response.raise_for_status()
            return {"ok": True, "model_count": len(response.json().get("models", [])), "base_url": self.base_url}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "base_url": self.base_url}

    def generate(self, model: str, messages: list[dict], response_format: str) -> str:
        # Generation historically did not start a local server; keep recovery
        # policy in the Qt facade/UI rather than surprising the user here.
        if not self.is_available():
            if self.is_local():
                raise ProviderRequestError("Ollama is not reachable. Start it with 'ollama serve' and ensure port 11434 is open.")
            raise ProviderRequestError(f"__OLLAMA_REMOTE_UNREACHABLE__:{self.base_url}")
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if response_format == "json":
            payload["format"] = "json"
        try:
            response = self._post(self.url("chat"), json=payload, timeout=300)
            response.raise_for_status()
            return response.json().get("message", {}).get("content", "")
        except Exception as exc:
            raise ProviderRequestError(f"Ollama Error: {exc}") from exc


class LMStudioClient:
    """LM Studio's v0 management and v1 inference HTTP contract."""

    def __init__(self, base_url: str, get: Callable[..., Any] = requests.get, post: Callable[..., Any] = requests.post):
        self.base_url = base_url.rstrip("/")
        self._get = get
        self._post = post

    def v0_url(self, path: str) -> str:
        return f"{self.base_url}/api/v0/{path.lstrip('/')}"

    def v1_url(self, path: str) -> str:
        return f"{self.base_url}/v1/{path.lstrip('/')}"

    @staticmethod
    def error_text(response: Any) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    return str(error.get("message") or error.get("error") or error)
                if isinstance(error, str) and error.strip():
                    return error.strip()
                if isinstance(payload.get("message"), str):
                    return payload["message"].strip()
                return json.dumps(payload, ensure_ascii=False)
        except Exception:
            pass
        return (getattr(response, "text", "") or getattr(response, "reason", "") or "Unknown LM Studio error").strip()

    def model_ids(self) -> tuple[list[str], str | None]:
        try:
            response = self._get(self.v1_url("models"), timeout=8)
            response.raise_for_status()
            rows = response.json().get("data", [])
            if not isinstance(rows, list):
                return [], "Invalid /v1/models response shape"
            return [str(row.get("id") or row.get("model") or row.get("name")).strip() for row in rows if isinstance(row, dict) and (row.get("id") or row.get("model") or row.get("name"))], None
        except Exception as exc:
            return [], str(exc)

    def test_connection(self, selected_model: str = "") -> dict:
        if not self.base_url:
            return {"ok": False, "error": "Empty LM Studio base URL", "base_url": self.base_url}
        try:
            response = self._get(self.v0_url("models"), timeout=6)
            response.raise_for_status()
            rows = response.json().get("data", [])
            v0_count = len(rows) if isinstance(rows, list) else 0
        except Exception as exc:
            return {"ok": False, "error": f"/api/v0/models failed: {exc}", "base_url": self.base_url}
        ids, error = self.model_ids()
        if error:
            return {"ok": False, "error": f"/v1/models failed: {error}", "base_url": self.base_url, "v0_model_count": v0_count, "v1_model_count": 0, "selected_model_visible_in_v1": False}
        visible = not selected_model or selected_model in ids
        diagnostic = None if visible else f"Selected model '{selected_model}' is not visible in /v1/models. Choose a /v1 model id or press USE to load/select one."
        return {"ok": True, "base_url": self.base_url, "v0_model_count": v0_count, "v1_model_count": len(ids), "model_count": v0_count, "selected_model_visible_in_v1": visible, "diagnostic_message": diagnostic, "v1_model_ids": ids}

    def generate(self, model: str, messages: list[dict]) -> str:
        if not model.strip():
            raise ProviderRequestError("LM Studio model not selected. Choose a model in Settings -> Intelligence.")
        ids, error = self.model_ids()
        if error:
            raise ProviderRequestError(f"LM Studio /v1/models check failed: {error}")
        if ids and model not in ids:
            preview = ", ".join(ids[:5]) + (" ..." if len(ids) > 5 else "")
            raise ProviderRequestError(f"LM Studio model id mismatch: '{model}' is not in /v1/models. Available ids: {preview}.")
        endpoint = self.v1_url("chat/completions")
        try:
            response = self._post(endpoint, json={"model": model, "messages": messages, "stream": False}, timeout=180)
            if response.status_code >= 400:
                raise ProviderRequestError(f"LM Studio {response.status_code}: {self.error_text(response)} | endpoint={endpoint} model={model}")
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except ProviderRequestError:
            raise
        except Exception as exc:
            raise ProviderRequestError(f"LM Studio request failed: {exc} | endpoint={endpoint} model={model}") from exc
