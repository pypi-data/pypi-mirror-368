"""Supply (suministro) related Pydantic models."""

from datetime import datetime
from typing import Optional

from pydantic import Field, field_validator

from edata.models.base import (
    EdataBaseModel,
    TimestampMixin,
    validate_cups,
    validate_reasonable_datetime,
)


class Supply(EdataBaseModel, TimestampMixin):
    """Pydantic model for electricity supply data (suministro eléctrico)."""

    cups: str = Field(
        ...,
        description="CUPS (Código Universal de Punto de Suministro) - Universal Supply Point Code",
        min_length=20,
        max_length=22,
    )
    date_start: datetime = Field(..., description="Supply contract start date")
    date_end: datetime = Field(..., description="Supply contract end date")
    address: Optional[str] = Field(None, description="Supply point address")
    postal_code: Optional[str] = Field(
        None, description="Postal code of the supply point", pattern=r"^\d{5}$"
    )
    province: Optional[str] = Field(None, description="Province name")
    municipality: Optional[str] = Field(None, description="Municipality name")
    distributor: Optional[str] = Field(
        None, description="Electricity distributor company name"
    )
    point_type: int = Field(..., description="Type of supply point", ge=1, le=5)
    distributor_code: str = Field(
        ..., description="Distributor company code", min_length=1
    )

    @field_validator("cups")
    @classmethod
    def validate_cups_format(cls, v: str) -> str:
        """Validate CUPS format."""
        return validate_cups(v)

    @field_validator("date_start", "date_end")
    @classmethod
    def validate_date_range(cls, v: datetime) -> datetime:
        """Validate date is reasonable."""
        return validate_reasonable_datetime(v)

    @field_validator("date_end")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info) -> datetime:
        """Validate that end date is after start date."""
        if (
            hasattr(info.data, "date_start")
            and info.data["date_start"]
            and v <= info.data["date_start"]
        ):
            raise ValueError("End date must be after start date")
        return v

    def __str__(self) -> str:
        """String representation showing anonymized CUPS."""
        return f"Supply(cups=...{self.cups[-5:]}, distributor={self.distributor})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Supply(cups={self.cups}, point_type={self.point_type})"
