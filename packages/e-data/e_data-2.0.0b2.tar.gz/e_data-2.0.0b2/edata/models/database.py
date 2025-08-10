from datetime import datetime as DateTime
from typing import List, Optional

from pydantic import Field
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from edata.models import Consumption, Contract, MaxPower, PricingData, Supply


class SupplyModel(Supply, SQLModel, table=True):
    """SQLModel for electricity supply data inheriting from Pydantic model."""

    __tablename__: str = "supplies"

    # Override cups field to add primary key
    cups: str = Field(primary_key=True, min_length=20, max_length=22)

    # Add database-specific fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

    # Relationships
    contracts: List["ContractModel"] = Relationship(back_populates="supply")
    consumptions: List["ConsumptionModel"] = Relationship(back_populates="supply")
    maximeter: List["MaxPowerModel"] = Relationship(back_populates="supply")


class ContractModel(Contract, SQLModel, table=True):
    """SQLModel for electricity contract data inheriting from Pydantic model."""

    __tablename__: str = "contracts"
    __table_args__ = (UniqueConstraint("cups", "date_start"),)

    # Add ID field for database
    id: Optional[int] = Field(default=None, primary_key=True)

    # Add CUPS field for foreign key
    cups: str = Field(foreign_key="supplies.cups")

    # Add database-specific fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

    # Relationships
    supply: Optional["SupplyModel"] = Relationship(back_populates="contracts")


class ConsumptionModel(Consumption, SQLModel, table=True):
    """SQLModel for electricity consumption data inheriting from Pydantic model."""

    __tablename__: str = "consumptions"
    __table_args__ = (UniqueConstraint("cups", "datetime"),)

    # Add ID field for database
    id: Optional[int] = Field(default=None, primary_key=True)

    # Add CUPS field for foreign key
    cups: str = Field(foreign_key="supplies.cups")

    # Add database-specific fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

    # Relationships
    supply: Optional["SupplyModel"] = Relationship(back_populates="consumptions")


class MaxPowerModel(MaxPower, SQLModel, table=True):
    """SQLModel for maximum power demand data inheriting from Pydantic model."""

    __tablename__: str = "maximeter"
    __table_args__ = (UniqueConstraint("cups", "datetime"),)

    # Add ID field for database
    id: Optional[int] = Field(default=None, primary_key=True)

    # Add CUPS field for foreign key
    cups: str = Field(foreign_key="supplies.cups")

    # Add database-specific fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

    # Relationships
    supply: Optional["SupplyModel"] = Relationship(back_populates="maximeter")


class PVPCPricesModel(PricingData, SQLModel, table=True):
    """SQLModel for PVPC pricing data inheriting from Pydantic model."""

    __tablename__: str = "pvpc_prices"
    __table_args__ = (UniqueConstraint("datetime", "geo_id"),)

    # Add ID field for database
    id: Optional[int] = Field(default=None, primary_key=True)

    # Add database-specific fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)

    # Add required fields for geographic specificity
    geo_id: int = Field(
        description="Geographic identifier (8741=Peninsula, 8744=Ceuta/Melilla)"
    )


class BillingModel(SQLModel, table=True):
    """SQLModel for billing calculations per hour."""

    __tablename__: str = "billing"
    __table_args__ = (UniqueConstraint("cups", "datetime", "pricing_config_hash"),)

    # Primary key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign key to supply
    cups: str = Field(foreign_key="supplies.cups")
    datetime: DateTime = Field(description="Hour of the billing calculation")

    # Calculated cost terms (the essential billing data)
    energy_term: float = Field(default=0.0, description="Energy cost term in €")
    power_term: float = Field(default=0.0, description="Power cost term in €")
    others_term: float = Field(default=0.0, description="Other costs term in €")
    surplus_term: float = Field(default=0.0, description="Surplus income term in €")
    total_eur: float = Field(default=0.0, description="Total cost in €")

    # Metadata
    tariff: Optional[str] = Field(
        default=None, description="Tariff period (p1, p2, p3)"
    )
    pricing_config_hash: str = Field(description="Hash of pricing rules configuration")

    # Audit fields
    created_at: DateTime = Field(default_factory=DateTime.now)
    updated_at: DateTime = Field(default_factory=DateTime.now)
