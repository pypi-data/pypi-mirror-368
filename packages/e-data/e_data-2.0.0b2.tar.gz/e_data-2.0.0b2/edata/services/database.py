"""Database service for edata using SQLModel and SQLite with async support."""

import hashlib
import os
from datetime import datetime as DateTime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel, desc, select

from edata.const import DEFAULT_STORAGE_DIR
from edata.models.database import (
    BillingModel,
    ConsumptionModel,
    ContractModel,
    MaxPowerModel,
    PVPCPricesModel,
    SupplyModel,
)


class DatabaseService:
    """Service for managing the SQLite database with async support."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize database service.

        Args:
            storage_dir: Directory to store database, defaults to same as cache
        """
        if storage_dir is None:
            storage_dir = DEFAULT_STORAGE_DIR

        self._db_dir = os.path.join(storage_dir)
        os.makedirs(self._db_dir, exist_ok=True)

        db_path = os.path.join(self._db_dir, "edata.db")
        # Use aiosqlite for async SQLite operations
        self._engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")

    async def create_tables(self):
        """Create tables asynchronously."""
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    def get_session(self) -> AsyncSession:
        """Get an async database session."""
        return AsyncSession(self._engine)

    async def save_supply(self, supply_data: dict) -> SupplyModel:
        """Save or update a supply record."""
        async with self.get_session() as session:
            # Check if supply exists
            existing = await session.get(SupplyModel, supply_data["cups"])

            if existing:
                # Update existing record
                for key, value in supply_data.items():
                    if hasattr(existing, key) and key != "cups":
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                supply = SupplyModel(**supply_data)
                session.add(supply)
                await session.commit()
                await session.refresh(supply)
                return supply

    async def save_contract(self, contract_data: dict) -> ContractModel:
        """Save or update a contract record."""
        async with self.get_session() as session:
            # Check if contract exists (by cups + date_start)
            stmt = select(ContractModel).where(
                ContractModel.cups == contract_data["cups"],
                ContractModel.date_start == contract_data["date_start"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                for key, value in contract_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                contract = ContractModel(**contract_data)
                session.add(contract)
                await session.commit()
                await session.refresh(contract)
                return contract

    async def save_consumption(self, consumption_data: dict) -> ConsumptionModel:
        """Save or update a consumption record."""
        async with self.get_session() as session:
            # Check if consumption exists (by cups + datetime)
            stmt = select(ConsumptionModel).where(
                ConsumptionModel.cups == consumption_data["cups"],
                ConsumptionModel.datetime == consumption_data["datetime"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                for key, value in consumption_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                consumption = ConsumptionModel(**consumption_data)
                session.add(consumption)
                await session.commit()
                await session.refresh(consumption)
                return consumption

    async def save_maxpower(self, maxpower_data: dict) -> MaxPowerModel:
        """Save or update a maxpower record."""
        async with self.get_session() as session:
            # Check if maxpower exists (by cups + datetime)
            stmt = select(MaxPowerModel).where(
                MaxPowerModel.cups == maxpower_data["cups"],
                MaxPowerModel.datetime == maxpower_data["datetime"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                for key, value in maxpower_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                maxpower = MaxPowerModel(**maxpower_data)
                session.add(maxpower)
                await session.commit()
                await session.refresh(maxpower)
                return maxpower

    async def get_supply(self, cups: str) -> Optional[SupplyModel]:
        """Get a supply by CUPS."""
        async with self.get_session() as session:
            return await session.get(SupplyModel, cups)

    async def get_supplies(self, cups: Optional[str] = None) -> List[SupplyModel]:
        """Get supplies, optionally filtered by CUPS."""
        async with self.get_session() as session:
            stmt = select(SupplyModel)
            if cups:
                stmt = stmt.where(SupplyModel.cups == cups)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_supply(
        self, cups: Optional[str] = None
    ) -> Optional[SupplyModel]:
        """Get the most recently updated supply, optionally filtered by CUPS."""
        async with self.get_session() as session:
            stmt = select(SupplyModel)
            if cups:
                stmt = stmt.where(SupplyModel.cups == cups)
            stmt = stmt.order_by(desc(SupplyModel.updated_at))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_contracts(self, cups: str) -> List[ContractModel]:
        """Get all contracts for a CUPS."""
        async with self.get_session() as session:
            stmt = select(ContractModel).where(ContractModel.cups == cups)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_contract(self, cups: str) -> Optional[ContractModel]:
        """Get the most recently started contract for a CUPS."""
        async with self.get_session() as session:
            stmt = select(ContractModel).where(ContractModel.cups == cups)
            stmt = stmt.order_by(desc(ContractModel.date_start))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_consumptions(
        self,
        cups: str,
        start_date: Optional[DateTime] = None,
        end_date: Optional[DateTime] = None,
    ) -> List[ConsumptionModel]:
        """Get consumptions for a CUPS within date range."""
        async with self.get_session() as session:
            stmt = select(ConsumptionModel).where(ConsumptionModel.cups == cups)

            if start_date:
                stmt = stmt.where(ConsumptionModel.datetime >= start_date)
            if end_date:
                stmt = stmt.where(ConsumptionModel.datetime <= end_date)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_consumption(self, cups: str) -> Optional[ConsumptionModel]:
        """Get the most recent consumption record for a CUPS."""
        async with self.get_session() as session:
            stmt = select(ConsumptionModel).where(ConsumptionModel.cups == cups)
            stmt = stmt.order_by(desc(ConsumptionModel.datetime))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_maxpower_readings(
        self,
        cups: str,
        start_date: Optional[DateTime] = None,
        end_date: Optional[DateTime] = None,
    ) -> List[MaxPowerModel]:
        """Get maxpower readings for a CUPS within date range."""
        async with self.get_session() as session:
            stmt = select(MaxPowerModel).where(MaxPowerModel.cups == cups)

            if start_date:
                stmt = stmt.where(MaxPowerModel.datetime >= start_date)
            if end_date:
                stmt = stmt.where(MaxPowerModel.datetime <= end_date)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_maxpower(self, cups: str) -> Optional[MaxPowerModel]:
        """Get the most recent maxpower reading for a CUPS."""
        async with self.get_session() as session:
            stmt = select(MaxPowerModel).where(MaxPowerModel.cups == cups)
            stmt = stmt.order_by(desc(MaxPowerModel.datetime))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def save_pvpc_price(self, price_data: dict) -> PVPCPricesModel:
        """Save or update a PVPC price record."""
        async with self.get_session() as session:
            # Check if price exists (by datetime and geo_id)
            stmt = select(PVPCPricesModel).where(
                PVPCPricesModel.datetime == price_data["datetime"]
            )
            if "geo_id" in price_data:
                stmt = stmt.where(PVPCPricesModel.geo_id == price_data["geo_id"])

            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                for key, value in price_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                price = PVPCPricesModel(**price_data)
                session.add(price)
                await session.commit()
                await session.refresh(price)
                return price

    async def get_pvpc_prices(
        self,
        start_date: Optional[DateTime] = None,
        end_date: Optional[DateTime] = None,
        geo_id: Optional[int] = None,
    ) -> List[PVPCPricesModel]:
        """Get PVPC prices within date range."""
        async with self.get_session() as session:
            stmt = select(PVPCPricesModel)

            if start_date:
                stmt = stmt.where(PVPCPricesModel.datetime >= start_date)
            if end_date:
                stmt = stmt.where(PVPCPricesModel.datetime <= end_date)
            if geo_id is not None:
                stmt = stmt.where(PVPCPricesModel.geo_id == geo_id)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_pvpc_price(
        self, geo_id: Optional[int] = None
    ) -> Optional[PVPCPricesModel]:
        """Get the most recent PVPC price, optionally filtered by geo_id."""
        async with self.get_session() as session:
            stmt = select(PVPCPricesModel)

            if geo_id is not None:
                stmt = stmt.where(PVPCPricesModel.geo_id == geo_id)

            stmt = stmt.order_by(desc(PVPCPricesModel.datetime))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def save_billing(self, billing_data: dict) -> BillingModel:
        """Save or update a billing record."""
        async with self.get_session() as session:
            # Check if billing exists (by cups + datetime + pricing_config_hash)
            stmt = select(BillingModel).where(
                BillingModel.cups == billing_data["cups"],
                BillingModel.datetime == billing_data["datetime"],
                BillingModel.pricing_config_hash == billing_data["pricing_config_hash"],
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record
                for key, value in billing_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = DateTime.now()
                session.add(existing)
                await session.commit()
                await session.refresh(existing)
                return existing
            else:
                # Create new record
                billing = BillingModel(**billing_data)
                session.add(billing)
                await session.commit()
                await session.refresh(billing)
                return billing

    async def get_billing(
        self,
        cups: str,
        start_date: Optional[DateTime] = None,
        end_date: Optional[DateTime] = None,
        pricing_config_hash: Optional[str] = None,
    ) -> List[BillingModel]:
        """Get billing records for a CUPS within date range."""
        async with self.get_session() as session:
            stmt = select(BillingModel).where(BillingModel.cups == cups)

            if start_date:
                stmt = stmt.where(BillingModel.datetime >= start_date)
            if end_date:
                stmt = stmt.where(BillingModel.datetime <= end_date)
            if pricing_config_hash:
                stmt = stmt.where(
                    BillingModel.pricing_config_hash == pricing_config_hash
                )

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_latest_billing(
        self, cups: str, pricing_config_hash: Optional[str] = None
    ) -> Optional[BillingModel]:
        """Get the most recent billing record for a CUPS."""
        async with self.get_session() as session:
            stmt = select(BillingModel).where(BillingModel.cups == cups)

            if pricing_config_hash:
                stmt = stmt.where(
                    BillingModel.pricing_config_hash == pricing_config_hash
                )

            stmt = stmt.order_by(desc(BillingModel.datetime))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def delete_billing(
        self,
        cups: str,
        pricing_config_hash: str,
        start_date: Optional[DateTime] = None,
        end_date: Optional[DateTime] = None,
    ) -> int:
        """Delete billing records for a specific configuration and optional date range."""
        async with self.get_session() as session:
            stmt = select(BillingModel).where(
                BillingModel.cups == cups,
                BillingModel.pricing_config_hash == pricing_config_hash,
            )

            if start_date:
                stmt = stmt.where(BillingModel.datetime >= start_date)
            if end_date:
                stmt = stmt.where(BillingModel.datetime <= end_date)

            result = await session.execute(stmt)
            billing_records = list(result.scalars().all())
            count = len(billing_records)

            for record in billing_records:
                await session.delete(record)

            await session.commit()
            return count

    @staticmethod
    def generate_pricing_config_hash(pricing_rules_dict: dict) -> str:
        """Generate a hash for pricing rules configuration."""
        # Create a normalized string representation for hashing
        config_str = str(sorted(pricing_rules_dict.items()))
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    async def save_from_pydantic_models(
        self,
        cups: str,
        supplies: List,
        contracts: List,
        consumptions: List,
        maximeter: List,
    ):
        """Save data from Pydantic models to database."""
        # Save supplies
        for supply in supplies:
            supply_dict = supply.model_dump()
            await self.save_supply(supply_dict)

        # Save contracts with CUPS
        for contract in contracts:
            contract_dict = contract.model_dump()
            contract_dict["cups"] = cups
            await self.save_contract(contract_dict)

        # Save consumptions with CUPS
        for consumption in consumptions:
            consumption_dict = consumption.model_dump()
            consumption_dict["cups"] = cups
            await self.save_consumption(consumption_dict)

        # Save maximeter readings with CUPS
        for maxpower in maximeter:
            maxpower_dict = maxpower.model_dump()
            maxpower_dict["cups"] = cups
            await self.save_maxpower(maxpower_dict)


# Global database service instance
_db_service: Optional[DatabaseService] = None


async def get_database_service(storage_dir: Optional[str] = None) -> DatabaseService:
    """Get the global database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService(storage_dir)
        # Initialize tables on first access
        await _db_service.create_tables()
    return _db_service
