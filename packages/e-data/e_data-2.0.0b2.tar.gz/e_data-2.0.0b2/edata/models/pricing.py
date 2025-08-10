"""Pricing related Pydantic models."""

from datetime import datetime as dt
from typing import Optional

from pydantic import Field, field_validator

from edata.models.base import (
    EdataBaseModel,
    TimestampMixin,
    validate_positive_number,
    validate_reasonable_datetime,
)


class PricingData(EdataBaseModel, TimestampMixin):
    """Pydantic model for electricity pricing data (PVPC prices)."""

    datetime: dt = Field(..., description="Timestamp of the price data")
    value_eur_kwh: float = Field(..., description="Price in EUR per kWh", ge=0)
    delta_h: float = Field(
        default=1.0, description="Duration this price applies (hours)", gt=0, le=24
    )

    @field_validator("datetime")
    @classmethod
    def validate_datetime_range(cls, v: dt) -> dt:
        """Validate datetime is reasonable."""
        return validate_reasonable_datetime(v)

    @field_validator("value_eur_kwh")
    @classmethod
    def validate_price_value(cls, v: float) -> float:
        """Validate price value is positive."""
        return validate_positive_number(v)

    def __str__(self) -> str:
        """String representation."""
        return f"Price({self.datetime}, {self.value_eur_kwh:.4f}€/kWh)"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"PricingData(datetime={self.datetime}, value_eur_kwh={self.value_eur_kwh})"
        )


class PricingRules(EdataBaseModel):
    """Pydantic model for custom pricing rules configuration."""

    # Power term costs (yearly costs in EUR per kW)
    p1_kw_year_eur: float = Field(
        ..., description="P1 power term cost (EUR/kW/year)", ge=0
    )
    p2_kw_year_eur: float = Field(
        ..., description="P2 power term cost (EUR/kW/year)", ge=0
    )

    # Energy term costs (optional for fixed pricing)
    p1_kwh_eur: Optional[float] = Field(
        None, description="P1 energy term cost (EUR/kWh) - None for PVPC", ge=0
    )
    p2_kwh_eur: Optional[float] = Field(
        None, description="P2 energy term cost (EUR/kWh) - None for PVPC", ge=0
    )
    p3_kwh_eur: Optional[float] = Field(
        None, description="P3 energy term cost (EUR/kWh) - None for PVPC", ge=0
    )

    # Surplus compensation (optional)
    surplus_p1_kwh_eur: Optional[float] = Field(
        None, description="P1 surplus compensation (EUR/kWh)", ge=0
    )
    surplus_p2_kwh_eur: Optional[float] = Field(
        None, description="P2 surplus compensation (EUR/kWh)", ge=0
    )
    surplus_p3_kwh_eur: Optional[float] = Field(
        None, description="P3 surplus compensation (EUR/kWh)", ge=0
    )

    # Fixed costs
    meter_month_eur: float = Field(
        ..., description="Monthly meter rental cost (EUR/month)", ge=0
    )
    market_kw_year_eur: float = Field(
        ..., description="Market operator cost (EUR/kW/year)", ge=0
    )

    # Tax multipliers
    electricity_tax: float = Field(
        ..., description="Electricity tax multiplier (e.g., 1.05113 for 5.113%)", ge=1.0
    )
    iva_tax: float = Field(
        ..., description="VAT tax multiplier (e.g., 1.21 for 21%)", ge=1.0
    )

    # Custom formulas (optional)
    energy_formula: Optional[str] = Field(
        "electricity_tax * iva_tax * kwh_eur * kwh",
        description="Custom energy cost formula (Jinja2 template)",
    )
    power_formula: Optional[str] = Field(
        "electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
        description="Custom power cost formula (Jinja2 template)",
    )
    others_formula: Optional[str] = Field(
        "iva_tax * meter_month_eur / 30 / 24",
        description="Custom other costs formula (Jinja2 template)",
    )
    surplus_formula: Optional[str] = Field(
        "electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
        description="Custom surplus compensation formula (Jinja2 template)",
    )
    main_formula: Optional[str] = Field(
        "energy_term + power_term + others_term",
        description="Main cost calculation formula (Jinja2 template)",
    )

    # Billing cycle
    cycle_start_day: int = Field(
        default=1, description="Day of month when billing cycle starts", ge=1, le=30
    )

    @property
    def is_pvpc(self) -> bool:
        """Check if this configuration uses PVPC (variable pricing)."""
        return all(
            price is None
            for price in [self.p1_kwh_eur, self.p2_kwh_eur, self.p3_kwh_eur]
        )

    def __str__(self) -> str:
        """String representation."""
        pricing_type = "PVPC" if self.is_pvpc else "Fixed"
        return f"PricingRules({pricing_type}, P1={self.p1_kw_year_eur}€/kW/year)"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PricingRules(p1_kw_year_eur={self.p1_kw_year_eur}, is_pvpc={self.is_pvpc})"


class PricingAggregated(EdataBaseModel, TimestampMixin):
    """Pydantic model for aggregated pricing/billing data."""

    datetime: dt = Field(
        ..., description="Timestamp representing the start of the billing period"
    )
    value_eur: float = Field(..., description="Total cost in EUR for the period", ge=0)
    energy_term: float = Field(default=0.0, description="Energy term cost (EUR)", ge=0)
    power_term: float = Field(default=0.0, description="Power term cost (EUR)", ge=0)
    others_term: float = Field(default=0.0, description="Other costs term (EUR)", ge=0)
    surplus_term: float = Field(
        default=0.0, description="Surplus compensation term (EUR)", ge=0
    )
    delta_h: float = Field(
        default=1.0, description="Duration of the billing period in hours", gt=0
    )

    @field_validator("datetime")
    @classmethod
    def validate_datetime_range(cls, v: dt) -> dt:
        """Validate datetime is reasonable."""
        return validate_reasonable_datetime(v)

    def __str__(self) -> str:
        """String representation."""
        period = (
            "hour" if self.delta_h <= 1 else "day" if self.delta_h <= 24 else "month"
        )
        return f"Billing({self.datetime.date()}, {self.value_eur:.2f}€/{period})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"PricingAggregated(datetime={self.datetime}, value_eur={self.value_eur}, delta_h={self.delta_h})"
