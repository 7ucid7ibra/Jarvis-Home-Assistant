"""Adapters from application ports to concrete providers and storage."""
from .llm_request_adapter import QtLLMRequestAdapter
from .home_assistant_adapter import LegacyHomeAssistantAdapter
from .memory_adapter import LegacyMemoryAdapter
from .telegram_adapter import TelegramBotAdapter
from .web_search_adapter import DuckDuckGoWebSearchAdapter

__all__ = [
    "DuckDuckGoWebSearchAdapter",
    "LegacyHomeAssistantAdapter",
    "LegacyMemoryAdapter",
    "QtLLMRequestAdapter",
    "TelegramBotAdapter",
]
