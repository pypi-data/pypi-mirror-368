"""Tests for MaximeterService."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from edata.models.database import MaxPowerModel
from edata.services.maximeter import MaximeterService


@pytest_asyncio.fixture
async def maximeter_service():
    """Create a maximeter service with mocked dependencies."""
    with patch("edata.services.maximeter.get_database_service") as mock_db_factory:
        mock_db = Mock()
        # Hacer que los métodos de la base de datos retornen AsyncMock
        mock_db.get_maxpower = AsyncMock(return_value=[])
        mock_db.save_maxpower = AsyncMock(return_value=Mock())
        mock_db_factory.return_value = mock_db

        # Create a mock DatadisConnector
        mock_datadis_connector = Mock()
        service = MaximeterService(datadis_connector=mock_datadis_connector)
        service._db_service = mock_db
        return service


@pytest.fixture
def sample_maximeter():
    """Sample maximeter data for testing."""
    return [
        MaxPowerModel(
            cups="ES001234567890123456AB",
            datetime=datetime(2023, 1, 15, 14, 30),
            value_kw=2.5,
        ),
        MaxPowerModel(
            cups="ES001234567890123456AB",
            datetime=datetime(2023, 2, 20, 16, 45),
            value_kw=3.2,
        ),
        MaxPowerModel(
            cups="ES001234567890123456AB",
            datetime=datetime(2023, 3, 10, 12, 15),
            value_kw=1.8,
        ),
    ]


class TestMaximeterService:
    """Test class for MaximeterService."""

    @pytest.mark.asyncio
    async def test_get_maximeter_summary(self, maximeter_service, sample_maximeter):
        """Test getting maximeter summary."""
        # Setup mocks
        maximeter_service.get_stored_maxpower = AsyncMock(return_value=sample_maximeter)

        # Execute
        result = await maximeter_service.get_maximeter_summary("ES001234567890123456AB")

        # Verify
        assert result["max_power_kW"] == 3.2  # max value
        assert result["max_power_date"] == datetime(2023, 2, 20, 16, 45)
        assert result["max_power_mean_kW"] == 2.5  # (2.5 + 3.2 + 1.8) / 3
        assert result["max_power_90perc_kW"] == 3.2  # 90th percentile

    @pytest.mark.asyncio
    async def test_get_maximeter_summary_no_data(self, maximeter_service):
        """Test getting maximeter summary with no data."""
        # Setup mocks
        maximeter_service.get_stored_maxpower = AsyncMock(return_value=[])

        # Execute
        result = await maximeter_service.get_maximeter_summary("ES001234567890123456AB")

        # Verify
        assert result["max_power_kW"] is None
        assert result["max_power_date"] is None
        assert result["max_power_mean_kW"] is None
        assert result["max_power_90perc_kW"] is None
