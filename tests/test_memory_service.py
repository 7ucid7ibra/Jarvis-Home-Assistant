import unittest

from jarvis_assistant.application.memory_service import MemoryService


class FakeMemory:
    def __init__(self):
        self.facts = {}

    def add_fact(self, key, value):
        self.facts[key] = value


class MemoryServiceTests(unittest.TestCase):
    def test_remember_that_strips_command_prefix(self):
        memory = FakeMemory()
        service = MemoryService(memory, clock=lambda: 123.9)

        result = service.remember("Remember that my favorite color is blue")

        self.assertTrue(result.stored)
        self.assertEqual(result.fact, "my favorite color is blue")
        self.assertEqual(memory.facts, {"fact_123": "my favorite color is blue"})

    def test_rejects_short_facts_without_persisting(self):
        memory = FakeMemory()
        service = MemoryService(memory, clock=lambda: 123.0)

        result = service.remember("ok")

        self.assertFalse(result.stored)
        self.assertEqual(memory.facts, {})


if __name__ == "__main__":
    unittest.main()
