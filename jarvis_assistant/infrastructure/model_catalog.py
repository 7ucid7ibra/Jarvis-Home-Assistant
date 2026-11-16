"""Read-only model catalog access separate from provider request handling."""

import json
from pathlib import Path
from typing import Any


class ModelCatalogRepository:
    def __init__(self, catalog_directory: Path | None = None):
        self._directory = catalog_directory or Path(__file__).resolve().parent.parent

    def load(self, provider: str) -> list[dict[str, Any]]:
        filename = "lmstudio_model_catalog.json" if provider.strip().lower() == "lmstudio" else "model_catalog.json"
        try:
            with (self._directory / filename).open(encoding="utf-8") as handle:
                payload = json.load(handle)
            models = payload.get("models", [])
            return models if isinstance(models, list) else []
        except (OSError, ValueError, TypeError):
            return []
