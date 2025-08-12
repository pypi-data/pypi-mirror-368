"""Defines abstract base classes for math exercises services."""

from abc import ABC, abstractmethod


class OperandGeneratorABC(ABC):
    """Protocol for generator of integer operands."""

    @abstractmethod
    def set_values(self, min_value: int, max_value: int) -> None:
        """Set value range for operands generate."""

    @abstractmethod
    def generate(self) -> int:
        """Generate integer within configured range."""
