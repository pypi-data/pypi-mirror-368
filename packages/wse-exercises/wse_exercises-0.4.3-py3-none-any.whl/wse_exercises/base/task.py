"""Defines base class for task."""

from datetime import datetime, timezone
from typing import Generic

from pydantic import Field

from wse_exercises import (
    AnswerT,
    ConditionsT,
    ConfigT,
    ExerciseT,
    QuestionT,
)

from .model import BaseShema


class Task(
    BaseShema,
    Generic[ConfigT, ConditionsT, QuestionT, AnswerT, ExerciseT],
):
    """Base class for DTO exercise task."""

    config: ConfigT
    conditions: ConditionsT
    question: QuestionT
    answer: AnswerT
    exercise_name: ExerciseT
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
