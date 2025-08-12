"""Defines base exceptions."""

from typing import Any


class ConversionError(Exception):
    """Base exception for all conversion-related errors."""

    def __init__(
        self,
        message: str,
        *,
        errors: list[Any] | None = None,
    ) -> None:
        """Construct the exception."""
        self.message = message
        self.errors = errors if errors is not None else []
        super().__init__(message)
