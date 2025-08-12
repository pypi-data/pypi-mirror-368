"""Defines mathematical exercises.

>>> from wse_exercises.core.math import (
...     AddingExercise,
...     ExactOperandGenerator,
... )
>>> exercise = AddingExercise(
...     operand_generator=ExactOperandGenerator(),
...     config={'min_value': 2, 'max_value': 9},
... )
>>> task = exercise.create_task()
>>> task.question.text
'2 + 9'
>>> task.answer.number
11
"""

from .base.exercise import CalcExercise
from .enums import MathEnum
from .task_factories import (
    AddingTaskFactory,
    DivisionTaskFactory,
    MultiplicationTaskFactory,
    SubtractionTaskFactory,
)


class AddingExercise(CalcExercise):
    """Adding exercise."""

    exercise_name = MathEnum.ADDING
    task_factory = AddingTaskFactory


class DivisionExercise(CalcExercise):
    """Division exercise."""

    exercise_name = MathEnum.DIVISION
    task_factory = DivisionTaskFactory


class MultiplicationExercise(CalcExercise):
    """Multiplication exercise."""

    exercise_name = MathEnum.MULTIPLICATION
    task_factory = MultiplicationTaskFactory


class SubtractionExercise(CalcExercise):
    """Subtraction exercise."""

    exercise_name = MathEnum.SUBTRACTION
    task_factory = SubtractionTaskFactory


if __name__ == '__main__':
    import doctest

    doctest.testmod()
