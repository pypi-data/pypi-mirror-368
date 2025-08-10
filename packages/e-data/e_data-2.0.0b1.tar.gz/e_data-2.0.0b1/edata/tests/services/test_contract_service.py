"""Tests for ContractService."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from edata.models.database import ContractModel
from edata.services.contract import ContractService


@pytest_asyncio.fixture
async def contract_service():
    """Create a contract service with mocked dependencies."""
    with patch("edata.services.contract.get_database_service") as mock_db_factory:
        mock_db = Mock()
        # Hacer que los métodos de la base de datos retornen AsyncMock
        mock_db.get_contracts = AsyncMock(return_value=[])
        mock_db.save_contract = AsyncMock(return_value=Mock())
        mock_db_factory.return_value = mock_db

        # Create a mock DatadisConnector
        mock_datadis_connector = Mock()
        service = ContractService(datadis_connector=mock_datadis_connector)
        service._db_service = mock_db
        return service


@pytest.fixture
def sample_contracts():
    """Sample contract data for testing."""
    return [
        ContractModel(
            cups="ES0012345678901234567890AB",
            date_start=datetime(2023, 1, 1),
            date_end=datetime(2023, 12, 31),
            marketer="Test Marketer 1",
            distributor_code="123",
            power_p1=4.6,
            power_p2=4.6,
        ),
        ContractModel(
            cups="ES0012345678901234567890AB",
            date_start=datetime(2024, 1, 1),
            date_end=datetime(2024, 12, 31),
            marketer="Test Marketer 2",
            distributor_code="123",
            power_p1=5.0,
            power_p2=5.0,
        ),
    ]


class TestContractService:
    """Test class for ContractService."""

    @pytest.mark.asyncio
    async def test_update_contracts_success(self, contract_service, sample_contracts):
        """Test successful contract update."""
        # Setup mocks - now returns Pydantic models instead of dicts
        contract_service._datadis.get_contract_detail = AsyncMock(
            return_value=[
                ContractModel(
                    cups="ES0012345678901234567890AB",
                    date_start=datetime(2024, 1, 1),
                    date_end=datetime(2024, 12, 31),
                    marketer="Test Marketer",
                    distributor_code="123",
                    power_p1=5.0,
                    power_p2=5.0,
                )
            ]
        )
        contract_service._db_service.get_contracts.return_value = []
        contract_service._db_service.save_contract.return_value = sample_contracts[0]

        # Execute
        result = await contract_service.update_contracts(
            cups="ES0012345678901234567890AB", distributor_code="123"
        )

        # Verify
        assert result["success"] is True
        assert result["stats"]["fetched"] == 1
        assert result["stats"]["saved"] == 1
        assert result["stats"]["updated"] == 0
        contract_service._datadis.get_contract_detail.assert_called_once()
        contract_service._db_service.save_contract.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contracts(self, contract_service, sample_contracts):
        """Test getting contracts."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = sample_contracts

        # Execute
        result = await contract_service.get_contracts("ES0012345678901234567890AB")

        # Verify
        assert len(result) == 2
        assert result[0].power_p1 == 4.6
        assert result[1].power_p1 == 5.0
        contract_service._db_service.get_contracts.assert_called_once_with(
            cups="ES0012345678901234567890AB"
        )

    @pytest.mark.asyncio
    async def test_get_active_contract(self, contract_service, sample_contracts):
        """Test getting active contract."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = sample_contracts

        # Execute - test with date in 2024
        result = await contract_service.get_active_contract(
            "ES0012345678901234567890AB", datetime(2024, 6, 15)
        )

        # Verify
        assert result is not None
        assert result.power_p1 == 5.0  # Should return 2024 contract
        assert result.date_start.year == 2024

    @pytest.mark.asyncio
    async def test_get_most_recent_contract(self, contract_service, sample_contracts):
        """Test getting most recent contract."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = sample_contracts

        # Execute - use the correct method name
        result = await contract_service.get_latest_contract(
            "ES0012345678901234567890AB"
        )

        # Verify
        assert result is not None
        assert result.power_p1 == 5.0  # Should return 2024 contract (most recent)
        assert result.date_start.year == 2024

    @pytest.mark.asyncio
    async def test_get_contract_stats(self, contract_service, sample_contracts):
        """Test getting contract statistics."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = sample_contracts

        # Execute
        result = await contract_service.get_contract_stats("ES0012345678901234567890AB")

        # Verify
        assert result["total_contracts"] == 2
        assert result["power_ranges"]["p1_kw"]["min"] == 4.6
        assert result["power_ranges"]["p1_kw"]["max"] == 5.0
        assert result["power_ranges"]["p2_kw"]["min"] == 4.6
        assert result["power_ranges"]["p2_kw"]["max"] == 5.0
        assert result["date_range"]["earliest_start"] == datetime(2023, 1, 1)
        assert result["date_range"]["latest_end"] == datetime(2024, 12, 31)

    @pytest.mark.asyncio
    async def test_update_contracts_no_data(self, contract_service):
        """Test contract update with no data returned."""
        # Setup mocks
        contract_service._datadis.get_contract_detail = AsyncMock(return_value=[])

        # Execute
        result = await contract_service.update_contracts(
            cups="ES0012345678901234567890AB", distributor_code="123"
        )

        # Verify
        assert result["success"] is True
        assert result["stats"]["fetched"] == 0
        assert result["stats"]["saved"] == 0

    @pytest.mark.asyncio
    async def test_update_contracts_error(self, contract_service):
        """Test contract update with error."""
        # Setup mocks
        contract_service._datadis.get_contract_detail = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Execute
        result = await contract_service.update_contracts(
            cups="ES0012345678901234567890AB", distributor_code="123"
        )

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert result["error"] == "API Error"

    @pytest.mark.asyncio
    async def test_get_contract_summary(self, contract_service, sample_contracts):
        """Test getting contract summary."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = sample_contracts

        # Execute
        result = await contract_service.get_contract_summary("ES001234567890123456AB")

        # Verify
        assert result["contract_p1_kW"] == 5.0  # From the most recent contract (2024)
        assert result["contract_p2_kW"] == 5.0

    @pytest.mark.asyncio
    async def test_get_contract_summary_no_data(self, contract_service):
        """Test getting contract summary with no data."""
        # Setup mocks
        contract_service._db_service.get_contracts.return_value = []

        # Execute
        result = await contract_service.get_contract_summary("ES001234567890123456AB")

        # Verify
        assert result["contract_p1_kW"] is None
        assert result["contract_p2_kW"] is None
