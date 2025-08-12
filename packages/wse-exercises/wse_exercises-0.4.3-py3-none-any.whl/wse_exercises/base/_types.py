"""Defines types for base task."""

from typing import Any, TypeVar

from .task import Task

TaskT = TypeVar('TaskT', bound=Task[Any, Any, Any, Any, Any])

TaskT_co = TypeVar(
    'TaskT_co',
    bound=Task[Any, Any, Any, Any, Any],
    covariant=True,
)
TaskT_contr = TypeVar(
    'TaskT_contr',
    bound=Task[Any, Any, Any, Any, Any],
    contravariant=True,
)
