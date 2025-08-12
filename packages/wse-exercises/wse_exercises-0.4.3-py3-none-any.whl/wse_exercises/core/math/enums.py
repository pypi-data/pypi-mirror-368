"""Defines enumeration of available exercise types."""

from wse_exercises.base.enums import ExerciseEnum


class MathEnum(ExerciseEnum):
    """Enumeration of available exercise types."""

    ADDING = 'adding'
    DIVISION = 'division'
    MULTIPLICATION = 'multiplication'
    SUBTRACTION = 'subtraction'
