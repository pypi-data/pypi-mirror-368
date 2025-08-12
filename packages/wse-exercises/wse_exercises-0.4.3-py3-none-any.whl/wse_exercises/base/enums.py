"""Defines base class for enumeration."""

from enum import Enum


class BaseEnum(str, Enum):
    """Base class for enumerations."""

    value: str

    def __str__(self) -> str:
        """Return value text."""
        return self.value


class ExerciseEnum(BaseEnum):
    """Base class for exercise enumerations."""
