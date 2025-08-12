"""Defines the math task Data Transfer Objects."""

from wse_exercises.base.task import Task

from .base.components import (
    CalcAnswer,
    CalcConditions,
    CalcConfig,
    CalcQuestion,
)
from .enums import MathEnum


class CalcTask(
    Task[
        CalcConfig,
        CalcConditions,
        CalcQuestion,
        CalcAnswer,
        MathEnum,
    ]
):
    """Base simple math task with text question/answer.

    :param config: Contains the min and max values of the operands.
    :param conditions: Contain the first and second operand values.
    :param question: The text representation of question.
    :param answer: The text representation of answer.
    :param exercise_name: Exercise name.
    :param created: The data and time of task creation.
    """

    config: CalcConfig
    conditions: CalcConditions
    question: CalcQuestion
    answer: CalcAnswer
    exercise_name: MathEnum
