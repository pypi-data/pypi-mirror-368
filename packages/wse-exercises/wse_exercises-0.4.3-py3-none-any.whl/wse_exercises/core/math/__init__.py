"""WSE mathematical exercises."""

__all__ = [
    'AddingExercise',
    'DivisionExercise',
    'ExactOperandGenerator',
    'MultiplicationExercise',
    'RandomOperandGenerator',
    'CalcAnswer',
    'CalcConditions',
    'CalcConfig',
    'CalcQuestion',
    'SubtractionExercise',
    'CalcTask',
]

from .base.components import (
    CalcAnswer,
    CalcConditions,
    CalcConfig,
    CalcQuestion,
)
from .exercises import (
    AddingExercise,
    DivisionExercise,
    MultiplicationExercise,
    SubtractionExercise,
)
from .services.operand_generator import (
    ExactOperandGenerator,
    RandomOperandGenerator,
)
from .task import (
    CalcTask,
)
