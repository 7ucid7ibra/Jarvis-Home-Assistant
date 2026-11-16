import unittest

from jarvis_assistant.infrastructure.memory_adapter import LegacyMemoryAdapter


class FakeMemoryManager:
    def __init__(self):
        self.facts = {}

    def add_fact(self, key, value):
        self.facts[key] = value

    def get_all_context(self):
        return "User Facts:"


class MemoryAdapterTests(unittest.TestCase):
    def test_forwards_fact_and_context_operations(self):
        manager = FakeMemoryManager()
        adapter = LegacyMemoryAdapter(manager)

        adapter.add_fact("name", "Ada")

        self.assertEqual(manager.facts, {"name": "Ada"})
        self.assertEqual(adapter.get_all_context(), "User Facts:")


if __name__ == "__main__":
    unittest.main()
