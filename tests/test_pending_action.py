import unittest

from jarvis_assistant.application.pending_action import PendingActionService


class PendingActionServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = PendingActionService()

    def test_decides_confirmation(self):
        self.assertEqual(self.service.decide("Yes, go ahead"), "confirm")

    def test_decides_cancellation(self):
        self.assertEqual(self.service.decide("No, cancel that"), "cancel")

    def test_leaves_unrelated_text_pending(self):
        self.assertEqual(self.service.decide("What would that do?"), "none")


if __name__ == "__main__":
    unittest.main()
