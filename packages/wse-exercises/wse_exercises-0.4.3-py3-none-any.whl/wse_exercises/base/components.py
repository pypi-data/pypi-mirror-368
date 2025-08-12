"""Defines base task components."""

from pydantic import Field

from .model import BaseShema

DEFAULT_TTL = 3600


class Config(BaseShema):
    """Base exercise config model to create task."""

    ttl: int = Field(
        default=DEFAULT_TTL,
        description='Time to complete the task',
    )


class Conditions(BaseShema):
    """Base exercise conditions model to create task."""


class Question(BaseShema):
    """Base task question model."""


class Answer(BaseShema):
    """Base task answer model."""


class TextQuestion(Question):
    """Text representation of question.

    :param str text: Text question.
    """

    text: str


class TextAnswer(Answer):
    """Text representation of answer.

    :param str text: Text answer.
    """

    text: str


class NumberAnswer(Answer):
    """Number representation of answer.

    :param int number: Number answer.
    """

    number: int
