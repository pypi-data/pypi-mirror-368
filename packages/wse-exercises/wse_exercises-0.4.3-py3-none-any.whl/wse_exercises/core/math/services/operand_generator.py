"""Defines operand generators for math exercises."""

from random import randint

from wse_exercises.core.math.base.services import OperandGeneratorABC
from wse_exercises.core.math.exceptions import OperandGeneratorError
from wse_exercises.utils.logger import setup_logging

logger = setup_logging(__name__)


class RandomOperandGenerator(OperandGeneratorABC):
    """Generates random operands in range.

    Example:
    >>> generator = RandomOperandGenerator()
    >>> generator.set_values(1, 10)
    >>> 1 <= generator.generate() <= 10
    True

    """

    _min_value: int
    _max_value: int

    def set_values(self, min_value: int, max_value: int) -> None:
        """Set operand value range."""
        self._min_value = min_value
        self._max_value = max_value

    def generate(self) -> int:
        """Generate random integer within configured range."""
        return randint(self._min_value, self._max_value)


class ExactOperandGenerator(OperandGeneratorABC):
    """Return value by order.

    Example:
    >>> from wse_exercises.core.math import ExactOperandGenerator
    >>> operand_generator = ExactOperandGenerator()
    >>> operand_generator.set_values(3, 4)
    >>> operand_generator.generate()
    3
    >>> operand_generator.generate()
    4

    """

    def __init__(self) -> None:
        """Construct the generator."""
        self._index = 0
        self._values: list[int] = []

    def set_values(self, min_value: int, max_value: int) -> None:
        """Set values for operand generation."""
        self._values = [min_value, max_value]

    def generate(self) -> int:
        """Return value by order."""
        try:
            value = self._values[self._index]
        except IndexError as error:
            raise OperandGeneratorError from error
        self._index += 1
        return value


if __name__ == '__main__':
    import doctest

    doctest.testmod()
