"""Model download state machines without Qt dependencies."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from typing import Any

import requests


ProgressCallback = Callable[[str, str, int], None]


class ModelDownloadService:
    def __init__(
        self,
        ollama_base_url: Callable[[], str],
        lmstudio_base_url: Callable[[], str],
        ensure_ollama: Callable[[], bool],
        is_lmstudio_model_installed: Callable[[str], bool],
        on_progress: ProgressCallback | None = None,
        get: Callable[..., Any] = requests.get,
        post: Callable[..., Any] = requests.post,
        delete: Callable[..., Any] = requests.delete,
        clock: Callable[[], float] = time.time,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._ollama_base_url = ollama_base_url
        self._lmstudio_base_url = lmstudio_base_url
        self._ensure_ollama = ensure_ollama
        self._is_lmstudio_model_installed = is_lmstudio_model_installed
        self._on_progress = on_progress or (lambda _key, _status, _pct: None)
        self._get, self._post, self._delete = get, post, delete
        self._clock, self._sleep = clock, sleep
        self._cancel_all = threading.Event()
        self._cancel_events: dict[str, threading.Event] = {}
        self._states: dict[str, dict] = {}

    def states(self) -> dict[str, dict]:
        return {key: state.copy() for key, state in self._states.items()}

    def state(self) -> dict:
        if self._states:
            active = [state for state in self._states.values() if state.get("active")]
            return (active[0] if active else list(self._states.values())[0]).copy()
        return {"active": False, "model": "", "status": "", "pct": -1}

    def cancel(self, name: str | None = None) -> None:
        if name:
            event = self._cancel_events.get(name)
            if event:
                event.set()
            if name in self._states:
                self._states[name]["status"] = "Cancelling download..."
            return
        self._cancel_all.set()
        for event in self._cancel_events.values():
            event.set()
        for state in self._states.values():
            state["status"] = "Cancelling download..."

    def _set_state(self, key: str, model: str, status: str, pct: int, active: bool) -> None:
        self._states[key] = {"active": active, "model": model, "status": status, "pct": pct}
        self._on_progress(key, status, pct)

    def _cancelled(self, event: threading.Event) -> bool:
        return self._cancel_all.is_set() or event.is_set()

    def pull_ollama(self, name: str) -> dict[str, str]:
        key = f"ollama::{name}"
        event = threading.Event()
        self._cancel_events[key] = event
        self._cancel_all.clear()
        self._set_state(key, name, f"Starting download: {name}...", 0, True)
        if not self._ensure_ollama():
            self._set_state(key, name, "Error: Ollama not running", -1, False)
            self._cancel_events.pop(key, None)
            return {"status": "error", "error": "Ollama not running"}
        try:
            response = self._post(f"{self._ollama_base_url().rstrip('/')}/api/pull", json={"name": name, "stream": True}, stream=True, timeout=300)
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        payload = json.loads(line)
                        status = payload.get("status", "")
                        total, completed = payload.get("total", 0), payload.get("completed", 0)
                        pct = int(completed / total * 100) if total else -1
                        if pct >= 0:
                            status = f"{status} ({pct}%)"
                        self._set_state(key, name, status, pct, True)
                    except (TypeError, ValueError):
                        continue
                if self._cancelled(event):
                    self._set_state(key, name, "Download Cancelled.", -1, False)
                    return {"status": "cancelled"}
            self._set_state(key, name, "Download Finished.", -1, False)
            return {"status": "success"}
        except Exception as exc:
            self._set_state(key, name, f"Error: {exc}", -1, False)
            return {"status": "error", "error": str(exc)}
        finally:
            self._cancel_events.pop(key, None)

    def download_lmstudio(self, model_key: str) -> dict[str, str]:
        key = f"lmstudio::{model_key}"
        event = threading.Event()
        self._cancel_events[key] = event
        self._cancel_all.clear()
        self._set_state(key, key, f"Starting download: {model_key}...", 0, True)
        base_url = self._lmstudio_base_url().rstrip("/")
        download_id = None
        try:
            response = self._post(f"{base_url}/api/v0/models/download", json={"modelKey": model_key}, timeout=20)
            response.raise_for_status()
            payload = response.json() if getattr(response, "content", True) else {}
            if isinstance(payload, dict):
                download_id = payload.get("downloadId") or payload.get("id")
            deadline = self._clock() + 1800
            while self._clock() < deadline:
                if self._cancelled(event):
                    if download_id:
                        try:
                            self._delete(f"{base_url}/api/v0/models/downloads/{download_id}", timeout=5)
                        except Exception:
                            pass
                    self._set_state(key, key, "Download Cancelled.", -1, False)
                    return {"status": "cancelled"}
                status, pct, done = "Downloading", -1, False
                if download_id:
                    try:
                        check = self._get(f"{base_url}/api/v0/models/downloads/{download_id}", timeout=8)
                        check.raise_for_status()
                        info = check.json() if getattr(check, "content", True) else {}
                        raw_status = str(info.get("status") or info.get("state") or "downloading")
                        progress = info.get("progress")
                        if isinstance(progress, (int, float)):
                            pct = max(0, min(100, int(progress * 100) if progress <= 1 else int(progress)))
                        status = f"{raw_status} ({pct}%)" if pct >= 0 else raw_status
                        if raw_status.lower() in {"failed", "error"}:
                            raise RuntimeError(info.get("error") or "Download failed")
                        done = raw_status.lower() in {"completed", "finished", "done", "success"}
                    except Exception:
                        pass
                if done or self._is_lmstudio_model_installed(model_key):
                    self._set_state(key, key, "Download Finished.", -1, False)
                    return {"status": "success"}
                self._set_state(key, key, status, pct, True)
                self._sleep(1.0)
            raise TimeoutError("LM Studio download timed out")
        except Exception as exc:
            self._set_state(key, key, f"Error: {exc}", -1, False)
            return {"status": "error", "error": str(exc)}
        finally:
            self._cancel_events.pop(key, None)
