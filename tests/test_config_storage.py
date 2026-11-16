import json
import tempfile
import unittest
from pathlib import Path

from jarvis_assistant.core.config import Config


class FakeSecrets:
    def __init__(self, available=True):
        self.values = {}
        self.available = available

    def get_secret(self, key):
        return self.values.get(key)

    def set_secret(self, key, value):
        self.values[key] = value

    def delete_secret(self, key):
        self.values.pop(key, None)

    def is_available(self):
        return self.available


class ConfigStorageTests(unittest.TestCase):
    def test_save_keeps_secrets_out_of_json_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            secrets = FakeSecrets()
            config = Config(str(path), secret_backend=secrets, migrate_legacy_data=False)
            config.assistant_name = "jarvis"
            config.api_key = "private-key"
            config.save()

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual("JARVIS", payload["assistant_name"])
            self.assertNotIn("api_key", payload)
            self.assertEqual("private-key", secrets.values["api_key"])

    def test_legacy_secret_migration_moves_value_and_scrubs_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps({"api_key": "legacy-key", "language": "en"}), encoding="utf-8")
            secrets = FakeSecrets()

            config = Config(str(path), secret_backend=secrets, migrate_legacy_data=False)

            self.assertEqual("legacy-key", secrets.values["api_key"])
            self.assertEqual("en", config.language)
            self.assertNotIn("api_key", json.loads(path.read_text(encoding="utf-8")))

    def test_url_history_is_normalized_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            secrets = FakeSecrets()
            config = Config(str(Path(directory) / "settings.json"), secret_backend=secrets, migrate_legacy_data=False)
            config.ollama_url_history = ["localhost:11434/api/tags", "http://localhost:11434", 9]

            self.assertEqual(
                ["http://127.0.0.1:11434", "http://localhost:11434"],
                config.ollama_url_history,
            )


if __name__ == "__main__":
    unittest.main()
