from ..domain.ports import MemoryPort


class LegacyMemoryAdapter(MemoryPort):
    """Expose the legacy JSON memory manager through the application port."""

    def __init__(self, manager):
        self._manager = manager

    def add_fact(self, key: str, value: str) -> None:
        self._manager.add_fact(key, value)

    def get_all_context(self) -> str:
        return self._manager.get_all_context()
