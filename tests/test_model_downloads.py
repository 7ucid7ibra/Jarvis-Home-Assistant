import json
import unittest

from jarvis_assistant.infrastructure.model_downloads import ModelDownloadService


class FakeResponse:
    def __init__(self, payload=None, lines=None):
        self._payload = payload or {}
        self._lines = lines or []
        self.content = b"{}"
        self.status_code = 200

    def json(self):
        return self._payload

    def iter_lines(self):
        return iter(self._lines)

    def raise_for_status(self):
        return None


class ModelDownloadServiceTests(unittest.TestCase):
    def make_service(self, **kwargs):
        return ModelDownloadService(
            ollama_base_url=lambda: "http://ollama:11434",
            lmstudio_base_url=lambda: "http://lmstudio:1234",
            ensure_ollama=lambda: True,
            is_lmstudio_model_installed=lambda _name: False,
            sleep=lambda _seconds: None,
            **kwargs,
        )

    def test_ollama_stream_updates_progress_and_finishes(self):
        progress = []
        response = FakeResponse(lines=[json.dumps({"status": "pulling", "total": 100, "completed": 50}).encode()])
        service = self.make_service(post=lambda *args, **kwargs: response, on_progress=lambda *event: progress.append(event))

        result = service.pull_ollama("qwen")

        self.assertEqual({"status": "success"}, result)
        self.assertIn(("ollama::qwen", "pulling (50%)", 50), progress)
        self.assertEqual("Download Finished.", service.state()["status"])
        self.assertFalse(service.state()["active"])

    def test_lmstudio_polling_completes_without_a_qt_timer(self):
        progress = []
        get_calls = []

        def post(*args, **kwargs):
            return FakeResponse({"downloadId": "download-1"})

        def get(url, **kwargs):
            get_calls.append(url)
            return FakeResponse({"status": "completed", "progress": 1})

        service = self.make_service(post=post, get=get, on_progress=lambda *event: progress.append(event))
        result = service.download_lmstudio("model-key")

        self.assertEqual({"status": "success"}, result)
        self.assertTrue(any(url.endswith("/downloads/download-1") for url in get_calls))
        self.assertEqual("Download Finished.", service.state()["status"])

    def test_unavailable_ollama_reports_failure_without_http_request(self):
        called = False

        def post(*args, **kwargs):
            nonlocal called
            called = True
            return FakeResponse()

        service = ModelDownloadService(
            ollama_base_url=lambda: "http://ollama:11434",
            lmstudio_base_url=lambda: "http://lmstudio:1234",
            ensure_ollama=lambda: False,
            is_lmstudio_model_installed=lambda _name: False,
            post=post,
        )
        result = service.pull_ollama("qwen")

        self.assertEqual("error", result["status"])
        self.assertFalse(called)
        self.assertEqual("Error: Ollama not running", service.state()["status"])

    def test_cancellation_marks_the_stream_as_cancelled(self):
        holder = {}

        def on_progress(key, status, pct):
            if status.startswith("Starting"):
                holder["service"].cancel(key)

        response = FakeResponse(lines=[json.dumps({"status": "pulling"}).encode()])
        service = self.make_service(post=lambda *args, **kwargs: response, on_progress=on_progress)
        holder["service"] = service

        self.assertEqual({"status": "cancelled"}, service.pull_ollama("qwen"))
        self.assertEqual("Download Cancelled.", service.state()["status"])


if __name__ == "__main__":
    unittest.main()
