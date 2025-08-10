"""Contract (contrato) related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from edata.models.base import (
    EdataBaseModel,
    TimestampMixin,
    validate_positive_number,
    validate_reasonable_datetime,
)


class Contract(EdataBaseModel, TimestampMixin):
    """Pydantic model for electricity contract data."""

    date_start: datetime = Field(..., description="Contract start date")
    date_end: datetime = Field(..., description="Contract end date")
    marketer: str = Field(..., description="Energy marketer company name", min_length=1)
    distributor_code: str = Field(
        ..., description="Distributor company code", min_length=1
    )
    power_p1: Optional[float] = Field(
        None, description="Contracted power for period P1 (kW)", ge=0
    )
    power_p2: Optional[float] = Field(
        None, description="Contracted power for period P2 (kW)", ge=0
    )

    @field_validator("date_start", "date_end")
    @classmethod
    def validate_date_range(cls, v: datetime) -> datetime:
        """Validate date is reasonable."""
        return validate_reasonable_datetime(v)

    @field_validator("power_p1", "power_p2")
    @classmethod
    def validate_power_values(cls, v: Optional[float]) -> Optional[float]:
        """Validate power values are positive."""
        if v is not None:
            return validate_positive_number(v)
        return v

    def __str__(self) -> str:
        """String representation."""
        return f"Contract(marketer={self.marketer}, power_p1={self.power_p1}kW)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Contract(marketer={self.marketer}, date_start={self.date_start}, date_end={self.date_end})"
