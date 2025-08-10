"""Consumption (consumo) related Pydantic models."""

from datetime import datetime as dt

from pydantic import Field, field_validator

from edata.models.base import (
    EdataBaseModel,
    EnergyMixin,
    TimestampMixin,
    validate_positive_number,
    validate_reasonable_datetime,
)


class Consumption(EdataBaseModel, TimestampMixin, EnergyMixin):
    """Pydantic model for electricity consumption data."""

    datetime: dt = Field(..., description="Timestamp of the consumption measurement")
    delta_h: float = Field(
        ..., description="Time interval in hours for this measurement", gt=0, le=24
    )
    value_kwh: float = Field(..., description="Energy consumption in kWh", ge=0)
    surplus_kwh: float = Field(
        default=0.0, description="Energy surplus/generation in kWh", ge=0
    )
    real: bool = Field(
        default=True, description="Whether this is a real measurement or estimated"
    )

    @field_validator("datetime")
    @classmethod
    def validate_datetime_range(cls, v: dt) -> dt:
        """Validate datetime is reasonable."""
        return validate_reasonable_datetime(v)

    @field_validator("value_kwh", "surplus_kwh")
    @classmethod
    def validate_energy_values(cls, v: float) -> float:
        """Validate energy values are positive."""
        return validate_positive_number(v)

    def __str__(self) -> str:
        """String representation."""
        return f"Consumption({self.datetime}, {self.value_kwh}kWh)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Consumption(datetime={self.datetime}, value_kwh={self.value_kwh}, real={self.real})"


class ConsumptionAggregated(EdataBaseModel, TimestampMixin, EnergyMixin):
    """Pydantic model for aggregated consumption data (daily/monthly summaries)."""

    datetime: dt = Field(
        ..., description="Timestamp representing the start of the aggregation period"
    )
    value_kwh: float = Field(
        ..., description="Total energy consumption in kWh for the period", ge=0
    )
    value_p1_kwh: float = Field(
        default=0.0, description="Energy consumption in period P1 (kWh)", ge=0
    )
    value_p2_kwh: float = Field(
        default=0.0, description="Energy consumption in period P2 (kWh)", ge=0
    )
    value_p3_kwh: float = Field(
        default=0.0, description="Energy consumption in period P3 (kWh)", ge=0
    )
    surplus_kwh: float = Field(
        default=0.0,
        description="Total energy surplus/generation in kWh for the period",
        ge=0,
    )
    surplus_p1_kwh: float = Field(
        default=0.0, description="Energy surplus in period P1 (kWh)", ge=0
    )
    surplus_p2_kwh: float = Field(
        default=0.0, description="Energy surplus in period P2 (kWh)", ge=0
    )
    surplus_p3_kwh: float = Field(
        default=0.0, description="Energy surplus in period P3 (kWh)", ge=0
    )
    delta_h: float = Field(
        ..., description="Duration of the aggregation period in hours", gt=0
    )

    @field_validator("datetime")
    @classmethod
    def validate_datetime_range(cls, v: dt) -> dt:
        """Validate datetime is reasonable."""
        return validate_reasonable_datetime(v)

    def __str__(self) -> str:
        """String representation."""
        period = "day" if self.delta_h <= 24 else "month"
        return f"ConsumptionAgg({self.datetime.date()}, {self.value_kwh}kWh/{period})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"ConsumptionAggregated(datetime={self.datetime}, value_kwh={self.value_kwh}, delta_h={self.delta_h})"
