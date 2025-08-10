"""Maximeter (maxímetro) related Pydantic models."""

from datetime import datetime as dt

from pydantic import Field, field_validator

from edata.models.base import (
    EdataBaseModel,
    TimestampMixin,
    validate_positive_number,
    validate_reasonable_datetime,
)


class MaxPower(EdataBaseModel, TimestampMixin):
    """Pydantic model for maximum power demand data."""

    datetime: dt = Field(..., description="Timestamp when maximum power was recorded")
    value_kw: float = Field(..., description="Maximum power demand in kW", ge=0)

    @field_validator("datetime")
    @classmethod
    def validate_datetime_range(cls, v: dt) -> dt:
        """Validate datetime is reasonable."""
        return validate_reasonable_datetime(v)

    @field_validator("value_kw")
    @classmethod
    def validate_power_value(cls, v: float) -> float:
        """Validate power value is positive."""
        return validate_positive_number(v)

    def __str__(self) -> str:
        """String representation."""
        return f"MaxPower({self.datetime}, {self.value_kw}kW)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"MaxPower(datetime={self.datetime}, value_kw={self.value_kw})"
