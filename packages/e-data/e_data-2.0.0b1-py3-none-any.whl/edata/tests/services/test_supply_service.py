"""Tests for SupplyService."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from edata.models.database import SupplyModel
from edata.services.supply import SupplyService


@pytest_asyncio.fixture
async def supply_service():
    """Create a supply service with mocked dependencies."""
    with patch("edata.services.supply.get_database_service") as mock_db_factory:
        mock_db = Mock()
        # Hacer que los métodos de la base de datos retornen AsyncMock
        mock_db.get_supplies = AsyncMock(return_value=[])
        mock_db.save_supply = AsyncMock(return_value=Mock())
        mock_db_factory.return_value = mock_db

        # Create a mock DatadisConnector
        mock_datadis_connector = Mock()
        service = SupplyService(datadis_connector=mock_datadis_connector)
        service._db_service = mock_db
        return service


@pytest.fixture
def sample_supplies():
    """Sample supply data for testing."""
    return [
        SupplyModel(
            cups="ES001234567890123456AB",
            distributor_code="123",
            point_type=5,
            date_start=datetime(2023, 1, 1),
            date_end=datetime(2024, 12, 31),
            address="Test Address 1",
            postal_code="12345",
            province="Test Province 1",
            municipality="Test Municipality 1",
            distributor="Test Distributor 1",
        ),
        SupplyModel(
            cups="ES987654321098765432BA",
            distributor_code="456",
            point_type=4,
            date_start=datetime(2023, 6, 1),
            date_end=datetime(2025, 6, 1),
            address="Test Address 2",
            postal_code="67890",
            province="Test Province 2",
            municipality="Test Municipality 2",
            distributor="Test Distributor 2",
        ),
    ]


class TestSupplyService:
    """Test class for SupplyService."""

    @pytest.mark.asyncio
    async def test_update_supplies_success(self, supply_service):
        """Test successful supply update."""
        # Setup mocks - now returns Pydantic models
        supply_service._datadis.get_supplies = AsyncMock(
            return_value=[
                SupplyModel(
                    cups="ES001234567890123456AB",
                    distributor_code="123",
                    point_type=5,
                    date_start=datetime(2023, 1, 1),
                    date_end=datetime(2024, 12, 31),
                    address="Test Address",
                    postal_code="12345",
                    province="Test Province",
                    municipality="Test Municipality",
                    distributor="Test Distributor",
                )
            ]
        )
        supply_service._db_service.get_supplies.side_effect = [
            [],
            [Mock()],
        ]  # No existing, then 1 stored
        supply_service._db_service.save_supply.return_value = Mock()

        # Execute
        result = await supply_service.update_supplies()

        # Verify
        assert result["success"] is True
        assert result["stats"]["fetched"] == 1
        assert result["stats"]["saved"] == 1
        assert result["stats"]["updated"] == 0
        supply_service._datadis.get_supplies.assert_called_once()
        supply_service._db_service.save_supply.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_supplies(self, supply_service, sample_supplies):
        """Test getting supplies."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = sample_supplies

        # Execute
        result = await supply_service.get_supplies()

        # Verify
        assert len(result) == 2
        assert result[0].cups == "ES001234567890123456AB"
        assert result[1].cups == "ES987654321098765432BA"
        supply_service._db_service.get_supplies.assert_called_once_with(cups=None)

    @pytest.mark.asyncio
    async def test_get_supply_by_cups(self, supply_service, sample_supplies):
        """Test getting supply by CUPS."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = [sample_supplies[0]]

        # Execute
        result = await supply_service.get_supply_by_cups("ES001234567890123456AB")

        # Verify
        assert result is not None
        assert result.cups == "ES001234567890123456AB"
        assert result.distributor == "Test Distributor 1"
        supply_service._db_service.get_supplies.assert_called_once_with(
            cups="ES001234567890123456AB"
        )

    @pytest.mark.asyncio
    async def test_get_cups_list(self, supply_service, sample_supplies):
        """Test getting CUPS list."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = sample_supplies

        # Execute
        result = await supply_service.get_cups_list()

        # Verify
        assert len(result) == 2
        assert "ES001234567890123456AB" in result
        assert "ES987654321098765432BA" in result

    @pytest.mark.asyncio
    async def test_get_active_supplies(self, supply_service, sample_supplies):
        """Test getting active supplies."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = sample_supplies

        # Execute - test with date in 2024 (both should be active)
        result = await supply_service.get_active_supplies(datetime(2024, 6, 15))

        # Verify
        assert len(result) == 2  # Both supplies should be active in 2024
        for supply in result:
            assert supply.date_start <= datetime(2024, 6, 15) <= supply.date_end

    @pytest.mark.asyncio
    async def test_get_supply_stats(self, supply_service, sample_supplies):
        """Test getting supply statistics."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = sample_supplies

        # Execute
        result = await supply_service.get_supply_stats()

        # Verify
        # Verify
        assert result["total_supplies"] == 2
        assert result["total_cups"] == 2
        assert result["date_range"]["earliest_start"] == datetime(2023, 1, 1)
        assert result["date_range"]["latest_end"] == datetime(2025, 6, 1)
        assert result["point_types"] == {5: 1, 4: 1}
        assert result["distributors"] == {
            "Test Distributor 1": 1,
            "Test Distributor 2": 1,
        }

    @pytest.mark.asyncio
    async def test_validate_cups(self, supply_service, sample_supplies):
        """Test CUPS validation."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = [sample_supplies[0]]

        # Execute
        result = await supply_service.validate_cups("ES001234567890123456AB")

        # Verify
        assert result is True

        # Test invalid CUPS
        supply_service._db_service.get_supplies.return_value = []
        result = await supply_service.validate_cups("INVALID_CUPS")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_distributor_code(self, supply_service, sample_supplies):
        """Test getting distributor code."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = [sample_supplies[0]]

        # Execute
        result = await supply_service.get_distributor_code("ES001234567890123456AB")

        # Verify
        assert result == "123"

    @pytest.mark.asyncio
    async def test_get_point_type(self, supply_service, sample_supplies):
        """Test getting point type."""
        # Setup mocks
        supply_service._db_service.get_supplies.return_value = [sample_supplies[0]]

        # Execute
        result = await supply_service.get_point_type("ES001234567890123456AB")

        # Verify
        assert result == 5

    @pytest.mark.asyncio
    async def test_update_supplies_no_data(self, supply_service):
        """Test supply update with no data returned."""
        # Setup mocks
        supply_service._datadis.get_supplies = AsyncMock(return_value=[])

        # Execute
        result = await supply_service.update_supplies()

        # Verify
        assert result["success"] is True
        assert result["stats"]["fetched"] == 0
        assert result["stats"]["saved"] == 0

    @pytest.mark.asyncio
    async def test_update_supplies_error(self, supply_service):
        """Test supply update with error."""
        # Setup mocks
        supply_service._datadis.get_supplies = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Execute
        result = await supply_service.update_supplies()

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "API Error"
