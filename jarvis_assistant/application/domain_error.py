"""Errors raised by application use cases."""


class EmptyUserInputError(ValueError):
    """Raised when a conversation turn has no meaningful user input."""

