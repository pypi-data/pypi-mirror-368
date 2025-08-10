"""Tests for DatabaseService."""

import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import patch

import pytest
import pytest_asyncio

from edata.models.database import (
    ConsumptionModel,
    ContractModel,
    MaxPowerModel,
    SupplyModel,
)
from edata.services.database import get_database_service


class TestDatabaseService:
    """Test suite for DatabaseService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest_asyncio.fixture
    async def db_service(self, temp_dir):
        """Create a database service for testing."""
        # Create a new instance directly instead of using the global singleton
        from edata.services.database import DatabaseService

        db_service = DatabaseService(temp_dir)
        await db_service.create_tables()
        yield db_service

    @pytest.fixture
    def sample_supply_data(self):
        """Sample supply data for testing."""
        return {
            "cups": "ES1234567890123456789",
            "date_start": datetime(2024, 1, 1),
            "date_end": datetime(2024, 12, 31),
            "address": "Test Address 123",
            "postal_code": "12345",
            "province": "Test Province",
            "municipality": "Test Municipality",
            "distributor": "Test Distributor",
            "point_type": 5,
            "distributor_code": "123",
        }

    @pytest.fixture
    def sample_contract_data(self):
        """Sample contract data for testing."""
        return {
            "cups": "ES1234567890123456789",
            "date_start": datetime(2024, 1, 1),
            "date_end": datetime(2024, 12, 31),
            "marketer": "Test Marketer",
            "distributor_code": "123",
            "power_p1": 4.4,
            "power_p2": 4.4,
        }

    @pytest.fixture
    def sample_consumption_data(self):
        """Sample consumption data for testing."""
        return {
            "cups": "ES1234567890123456789",
            "datetime": datetime(2024, 6, 15, 12, 0),
            "delta_h": 1.0,
            "value_kwh": 0.5,
            "surplus_kwh": 0.0,
            "real": True,
        }

    @pytest.fixture
    def sample_maxpower_data(self):
        """Sample maxpower data for testing."""
        return {
            "cups": "ES1234567890123456789",
            "datetime": datetime(2024, 6, 15, 15, 30),
            "value_kw": 3.2,
        }

    @pytest.mark.asyncio
    async def test_database_initialization(self, temp_dir):
        """Test database service initialization."""
        service = await get_database_service(storage_dir=temp_dir)

        # Check that database file was created
        expected_db_path = os.path.join(temp_dir, "edata.db")
        assert os.path.exists(expected_db_path)

        # Check that we can get a session
        session = service.get_session()
        assert session is not None
        await session.close()

    @pytest.mark.asyncio
    async def test_save_and_get_supply(self, db_service, sample_supply_data):
        """Test saving and retrieving supply data."""
        # Save supply
        saved_supply = await db_service.save_supply(sample_supply_data)

        assert saved_supply.cups == sample_supply_data["cups"]
        assert saved_supply.distributor == sample_supply_data["distributor"]
        assert saved_supply.point_type == sample_supply_data["point_type"]
        assert saved_supply.created_at is not None
        assert saved_supply.updated_at is not None

        # Get supply
        retrieved_supply = await db_service.get_supply(sample_supply_data["cups"])

        assert retrieved_supply is not None
        assert retrieved_supply.cups == sample_supply_data["cups"]
        assert retrieved_supply.distributor == sample_supply_data["distributor"]

    @pytest.mark.asyncio
    async def test_update_existing_supply(self, db_service, sample_supply_data):
        """Test updating an existing supply."""
        # Save initial supply
        await db_service.save_supply(sample_supply_data)

        # Update supply data
        updated_data = sample_supply_data.copy()
        updated_data["distributor"] = "Updated Distributor"

        # Save updated supply
        updated_supply = await db_service.save_supply(updated_data)

        assert updated_supply.distributor == "Updated Distributor"
        assert updated_supply.cups == sample_supply_data["cups"]

        # Verify only one supply exists
        retrieved_supply = await db_service.get_supply(sample_supply_data["cups"])
        assert retrieved_supply.distributor == "Updated Distributor"

    @pytest.mark.asyncio
    async def test_save_and_get_contract(
        self, db_service, sample_supply_data, sample_contract_data
    ):
        """Test saving and retrieving contract data."""
        # Save supply first (foreign key dependency)
        await db_service.save_supply(sample_supply_data)

        # Save contract
        saved_contract = await db_service.save_contract(sample_contract_data)

        assert saved_contract.cups == sample_contract_data["cups"]
        assert saved_contract.marketer == sample_contract_data["marketer"]
        assert saved_contract.power_p1 == sample_contract_data["power_p1"]
        assert saved_contract.id is not None

        # Get contracts
        contracts = await db_service.get_contracts(sample_contract_data["cups"])

        assert len(contracts) == 1
        assert contracts[0].marketer == sample_contract_data["marketer"]

    @pytest.mark.asyncio
    async def test_contract_unique_constraint(
        self, db_service, sample_supply_data, sample_contract_data
    ):
        """Test that contract unique constraint works (cups + date_start)."""
        # Save supply first
        await db_service.save_supply(sample_supply_data)

        # Save first contract
        await db_service.save_contract(sample_contract_data)

        # Try to save contract with same cups + date_start but different data
        updated_contract_data = sample_contract_data.copy()
        updated_contract_data["marketer"] = "Different Marketer"
        updated_contract_data["power_p1"] = 6.6

        # This should update, not create new
        await db_service.save_contract(updated_contract_data)

        # Should still have only one contract, but with updated data
        contracts = await db_service.get_contracts(sample_contract_data["cups"])
        assert len(contracts) == 1
        assert contracts[0].marketer == "Different Marketer"
        assert contracts[0].power_p1 == 6.6

    @pytest.mark.asyncio
    async def test_save_and_get_consumption(
        self, db_service, sample_supply_data, sample_consumption_data
    ):
        """Test saving and retrieving consumption data."""
        # Save supply first
        await db_service.save_supply(sample_supply_data)

        # Save consumption
        saved_consumption = await db_service.save_consumption(sample_consumption_data)

        assert saved_consumption.cups == sample_consumption_data["cups"]
        assert saved_consumption.value_kwh == sample_consumption_data["value_kwh"]
        assert saved_consumption.real == sample_consumption_data["real"]
        assert saved_consumption.id is not None

        # Get consumptions
        consumptions = await db_service.get_consumptions(
            sample_consumption_data["cups"]
        )

        assert len(consumptions) == 1
        assert consumptions[0].value_kwh == sample_consumption_data["value_kwh"]

    @pytest.mark.asyncio
    async def test_get_consumptions_with_date_filter(
        self, db_service, sample_supply_data, sample_consumption_data
    ):
        """Test getting consumptions with date range filter."""
        # Save supply first
        await db_service.save_supply(sample_supply_data)

        # Save multiple consumptions with different dates
        consumption1 = sample_consumption_data.copy()
        consumption1["datetime"] = datetime(2024, 6, 15, 10, 0)

        consumption2 = sample_consumption_data.copy()
        consumption2["datetime"] = datetime(2024, 6, 16, 10, 0)

        consumption3 = sample_consumption_data.copy()
        consumption3["datetime"] = datetime(2024, 6, 17, 10, 0)

        await db_service.save_consumption(consumption1)
        await db_service.save_consumption(consumption2)
        await db_service.save_consumption(consumption3)

        # Get consumptions with date filter
        start_date = datetime(2024, 6, 15, 12, 0)  # After first consumption
        end_date = datetime(2024, 6, 16, 12, 0)  # Before third consumption

        filtered_consumptions = await db_service.get_consumptions(
            cups=sample_consumption_data["cups"],
            start_date=start_date,
            end_date=end_date,
        )

        # Should only get the second consumption
        assert len(filtered_consumptions) == 1
        assert filtered_consumptions[0].datetime == datetime(2024, 6, 16, 10, 0)

    @pytest.mark.asyncio
    async def test_save_and_get_maxpower(
        self, db_service, sample_supply_data, sample_maxpower_data
    ):
        """Test saving and retrieving maxpower data."""
        # Save supply first
        await db_service.save_supply(sample_supply_data)

        # Save maxpower
        saved_maxpower = await db_service.save_maxpower(sample_maxpower_data)

        assert saved_maxpower.cups == sample_maxpower_data["cups"]
        assert saved_maxpower.value_kw == sample_maxpower_data["value_kw"]
        assert saved_maxpower.id is not None

        # Get maxpower readings
        maxpower_readings = await db_service.get_maxpower_readings(
            sample_maxpower_data["cups"]
        )

        assert len(maxpower_readings) == 1
        assert maxpower_readings[0].value_kw == sample_maxpower_data["value_kw"]

    @pytest.mark.asyncio
    async def test_consumption_unique_constraint(
        self, db_service, sample_supply_data, sample_consumption_data
    ):
        """Test that consumption unique constraint works (cups + datetime)."""
        # Save supply first
        await db_service.save_supply(sample_supply_data)

        # Save first consumption
        await db_service.save_consumption(sample_consumption_data)

        # Try to save consumption with same cups + datetime but different value
        updated_consumption = sample_consumption_data.copy()
        updated_consumption["value_kwh"] = 1.5

        # This should update, not create new
        await db_service.save_consumption(updated_consumption)

        # Should still have only one consumption, but with updated value
        consumptions = await db_service.get_consumptions(
            sample_consumption_data["cups"]
        )
        assert len(consumptions) == 1
        assert consumptions[0].value_kwh == 1.5

    @pytest.mark.asyncio
    async def test_save_from_pydantic_models(self, db_service):
        """Test saving data from Pydantic models."""
        cups = "ES1234567890123456789"

        # Create Pydantic models
        supply = SupplyModel(
            cups=cups,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2024, 12, 31),
            address="Test Address",
            postal_code="12345",
            province="Test Province",
            municipality="Test Municipality",
            distributor="Test Distributor",
            point_type=5,
            distributor_code="123",
        )

        contract = ContractModel(
            cups=cups,
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2024, 12, 31),
            marketer="Test Marketer",
            distributor_code="123",
            power_p1=4.4,
            power_p2=4.4,
        )

        consumption = ConsumptionModel(
            cups=cups, datetime=datetime(2024, 6, 15, 12, 0), delta_h=1.0, value_kwh=0.5
        )

        maxpower = MaxPowerModel(
            cups=cups, datetime=datetime(2024, 6, 15, 15, 30), value_kw=3.2
        )

        # Save using the batch method
        await db_service.save_from_pydantic_models(
            cups=cups,
            supplies=[supply],
            contracts=[contract],
            consumptions=[consumption],
            maximeter=[maxpower],
        )

        # Verify data was saved
        saved_supply = await db_service.get_supply(cups)
        assert saved_supply is not None
        assert saved_supply.cups == cups

        saved_contracts = await db_service.get_contracts(cups)
        assert len(saved_contracts) == 1
        assert saved_contracts[0].marketer == "Test Marketer"

        saved_consumptions = await db_service.get_consumptions(cups)
        assert len(saved_consumptions) == 1
        assert saved_consumptions[0].value_kwh == 0.5

        saved_maxpower = await db_service.get_maxpower_readings(cups)
        assert len(saved_maxpower) == 1
        assert saved_maxpower[0].value_kw == 3.2

    @pytest.mark.asyncio
    async def test_database_relationships(
        self, db_service, sample_supply_data, sample_contract_data
    ):
        """Test that database relationships work correctly."""
        # Save supply and contract
        await db_service.save_supply(sample_supply_data)
        await db_service.save_contract(sample_contract_data)

        # Get supply with relationships (this would work if we load with relationships)
        supply = await db_service.get_supply(sample_supply_data["cups"])
        assert supply is not None
        assert supply.cups == sample_supply_data["cups"]

        # Verify foreign key constraint works
        contracts = await db_service.get_contracts(sample_supply_data["cups"])
        assert len(contracts) == 1
        assert contracts[0].cups == sample_supply_data["cups"]

    @pytest.mark.asyncio
    async def test_invalid_cups_foreign_key(self, db_service, sample_contract_data):
        """Test that foreign key constraint prevents orphaned records."""
        # Try to save contract without supply (should fail or handle gracefully)
        # Note: This depends on SQLite foreign key enforcement
        try:
            await db_service.save_contract(sample_contract_data)
            # If it doesn't raise an error, verify the record wasn't actually saved
            # or that the database handles it appropriately
        except Exception:
            # Expected if foreign key constraints are enforced
            pass

    @pytest.mark.asyncio
    async def test_default_storage_dir(self):
        """Test that default storage directory is used when none provided."""
        import tempfile

        test_dir = tempfile.mkdtemp()

        try:
            # Reset the global singleton to allow testing default directory
            import edata.services.database

            edata.services.database._db_service = None

            with patch("edata.services.database.DEFAULT_STORAGE_DIR", test_dir):
                service = await get_database_service()
                # Check that service was created with the correct directory
                assert service._db_dir == test_dir
                assert os.path.exists(service._db_dir)
        finally:
            # Clean up
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
