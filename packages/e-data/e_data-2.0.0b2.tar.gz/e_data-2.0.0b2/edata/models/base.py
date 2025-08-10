"""Base models and common functionality for edata Pydantic models."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, field_validator


class EdataBaseModel(BaseModel):
    """Base model for all edata entities with common configuration."""

    model_config = ConfigDict(
        # Validate assignments to ensure data integrity
        validate_assignment=True,
        # Use enum values instead of enum objects for serialization
        use_enum_values=True,
        # Extra fields are forbidden to catch typos and ensure schema compliance
        extra="forbid",
        # Validate default values
        validate_default=True,
        # Allow serialization of datetime objects
        arbitrary_types_allowed=False,
        # Convert strings to datetime objects when possible
        str_strip_whitespace=True,
    )

    def model_dump_for_storage(self) -> Dict[str, Any]:
        """Serialize model for storage, handling special types like datetime."""
        return self.model_dump(mode="json")

    @classmethod
    def from_storage(cls, data: Dict[str, Any]):
        """Create model instance from storage data."""
        return cls.model_validate(data)


class TimestampMixin(BaseModel):
    """Mixin for models that have datetime fields."""

    @field_validator("*", mode="before")
    @classmethod
    def validate_datetime_fields(cls, v, info):
        """Convert datetime strings to datetime objects if needed."""
        field_name = info.field_name
        if field_name and ("datetime" in field_name or "date" in field_name):
            if isinstance(v, str):
                try:
                    from dateutil import parser

                    return parser.parse(v)
                except (ValueError, TypeError):
                    pass
        return v


class EnergyMixin(BaseModel):
    """Mixin for models dealing with energy values."""

    @field_validator("*", mode="before")
    @classmethod
    def validate_energy_fields(cls, v, info):
        """Validate energy-related fields."""
        field_name = info.field_name
        if field_name and ("kwh" in field_name.lower() or "kw" in field_name.lower()):
            if v is not None and v < 0:
                raise ValueError(f"{field_name} cannot be negative")
        return v


def validate_cups(v: str) -> str:
    """Validate CUPS (Spanish electricity supply point code) format."""
    if not v:
        raise ValueError("CUPS cannot be empty")

    # Remove spaces and convert to uppercase
    cups = v.replace(" ", "").upper()

    # Basic CUPS format validation (ES + 18-20 alphanumeric characters)
    if not cups.startswith("ES"):
        raise ValueError("CUPS must start with 'ES'")

    if len(cups) < 20 or len(cups) > 22:
        raise ValueError("CUPS must be 20-22 characters long")

    return cups


def validate_positive_number(v: float) -> float:
    """Validate that a number is positive."""
    if v is not None and v < 0:
        raise ValueError("Value must be positive")
    return v


def validate_reasonable_datetime(v: datetime) -> datetime:
    """Validate that datetime is within reasonable bounds."""
    if v.year < 2000:
        raise ValueError("Date cannot be before year 2000")

    # Allow future dates for contracts and supplies (they can be valid until future dates)
    # Only restrict to really unreasonable future dates
    if v.year > datetime.now().year + 50:
        raise ValueError("Date cannot be more than 50 years in the future")

    return v
