"""Defines mixins."""

import uuid
from datetime import datetime
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError, validator

from .exeptions import ConversionError

T = TypeVar('T', bound='ConvertMixin')


class ConvertMixin(BaseModel):
    """Mixin providing conversion between dict/json."""

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> T:
        """Instantiate the class from a dictionary of attributes."""
        if not isinstance(data, dict):
            raise ConversionError(
                f'Expected dict, got {type(data).__name__}',
            )
        try:
            return cls.parse_obj(data)
        except ValidationError as e:
            raise ConversionError(
                'Data validate filed',
                errors=e.errors(),
            ) from e

    @classmethod
    def from_json(cls: Type[T], data: str | bytes) -> T:
        """Instantiate the class from a JSON string or bytes."""
        if not isinstance(data, (str, bytes)):
            raise ConversionError(
                f'Expected str/bytes, got {type(data).__name__}',
            )
        try:
            return cls.parse_raw(data)
        except ValidationError as e:
            raise ConversionError(
                'JSON validation failed',
                errors=e.errors(),
            ) from e

    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""

        def convert_datetime(data: dict[str, Any]) -> dict[str, Any]:
            dict_data: dict[str, Any] = {}

            for key, value in data.items():
                if isinstance(value, datetime):
                    dict_data[key] = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    dict_data[key] = str(value)
                elif isinstance(value, dict):
                    dict_data[key] = convert_datetime(value)
                else:
                    dict_data[key] = value

            return dict_data

        return convert_datetime(self.dict())

    def to_json(self) -> str:
        """Serialize the instance to a JSON string."""
        return self.json()

    @classmethod
    @validator('*', pre=True)
    def _validate_uuid_fields(cls, value: object) -> object:
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except (ValueError, AttributeError):
                pass
        return value
