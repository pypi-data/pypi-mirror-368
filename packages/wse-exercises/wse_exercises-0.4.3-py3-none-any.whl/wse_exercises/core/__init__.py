"""Core business logic package for WSE Exercise Series."""

__all__ = [
    'MathEnum',
    'MATH_EXERCISES',
]

from .math import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from .math.enums import MathEnum

MATH_EXERCISES = {
    MathEnum.ADDING: AddingExercise,
    MathEnum.SUBTRACTION: SubtractionExercise,
    MathEnum.MULTIPLICATION: MultiplicationExercise,
    MathEnum.DIVISION: DivisionExercise,
}
