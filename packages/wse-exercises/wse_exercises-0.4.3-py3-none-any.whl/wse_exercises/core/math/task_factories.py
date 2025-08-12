"""Defines the calculation exercise components."""

from .base.task_factory import CalcFactory


class AddingTaskFactory(CalcFactory):
    """Create simple adding task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math adding task."""
        return f'{op1} + {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> int:
        """Create an answer to a simple math adding task."""
        return op1 + op2


class DivisionTaskFactory(CalcFactory):
    """Create simple division task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math division task."""
        return f'{op1 * op2} \u00f7 {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> int:
        """Create an answer to a simple math division task."""
        return op1


class MultiplicationTaskFactory(CalcFactory):
    """Create simple multiplication task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math multiplication task."""
        return f'{op1} \u00d7 {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> int:
        """Create an answer to a simple math multiplication task."""
        return op1 * op2


class SubtractionTaskFactory(CalcFactory):
    """Create simple subtraction task."""

    @classmethod
    def create_question(cls, op1: int, op2: int) -> str:
        """Create a question to a simple math subtraction task."""
        return f'{op1} - {op2}'

    @classmethod
    def create_answer(cls, op1: int, op2: int) -> int:
        """Create an answer to a simple math subtraction task."""
        return op1 - op2
