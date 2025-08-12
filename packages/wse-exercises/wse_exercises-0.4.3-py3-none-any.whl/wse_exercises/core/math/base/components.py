"""Defines mathematical task component models."""

from typing import Any

from pydantic import Field, validator

from wse_exercises.base.components import (
    Conditions,
    Config,
    NumberAnswer,
    TextQuestion,
)

MIN_VALUE = 1
MAX_VALUE = 9


class CalcConfig(Config):
    """Simple calculation math task config model."""

    min_value: int = MIN_VALUE
    max_value: int = MAX_VALUE

    @classmethod
    @validator('max_value')
    def check_min_less_than_max(
        cls,
        value: str,
        values: dict[str, Any],
    ) -> str:
        """Check that the minimum value is greater than the maximum."""
        if 'min_value' in values and value <= values['min_value']:
            raise ValueError('max_value must be greater than min_value')
        return value


class CalcConditions(Conditions):
    """Simple calculation math task conditions model."""

    operand_1: int
    operand_2: int
    time: int = Field(default=60, description='Time for task solution')


class CalcQuestion(TextQuestion):
    """Simple calculation math task question model."""


class CalcAnswer(NumberAnswer):
    """Simple calculation math task answer model."""
