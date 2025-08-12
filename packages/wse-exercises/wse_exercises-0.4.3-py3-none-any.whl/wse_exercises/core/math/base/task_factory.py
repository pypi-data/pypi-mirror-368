"""Defines abstraction base class for math task creation."""

from abc import ABC, abstractmethod


class CalcFactory(ABC):
    """Abstract base class for simple math task component factory."""

    @classmethod
    @abstractmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math task.

        :param int op1: First calculation operand
        :param int op2: Second calculation operand
        :return: Text representation of task
        :rtype: str
        """

    @classmethod
    @abstractmethod
    def create_answer(cls, op1: int, op2: int) -> int:
        """Create an answer to a simple math task.

        :param int op1: First calculation operand
        :param int op2: Second calculation operand
        :return: Text representation of answer
        :rtype: int
        """
