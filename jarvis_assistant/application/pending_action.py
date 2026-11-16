"""Headless interpretation of pending-action confirmations."""

from typing import Literal


PendingActionDecision = Literal["confirm", "cancel", "none"]


class PendingActionService:
    CONFIRM_WORDS = (
        "yes",
        "sure",
        "do it",
        "confirm",
        "okay",
        "ok",
        "please do",
        "go ahead",
        "proceed",
    )
    CANCEL_WORDS = ("no", "cancel", "stop", "don't")

    def decide(self, user_text: str) -> PendingActionDecision:
        lowered = (user_text or "").strip().lower()
        if any(word in lowered for word in self.CONFIRM_WORDS):
            return "confirm"
        if any(word in lowered for word in self.CANCEL_WORDS):
            return "cancel"
        return "none"
