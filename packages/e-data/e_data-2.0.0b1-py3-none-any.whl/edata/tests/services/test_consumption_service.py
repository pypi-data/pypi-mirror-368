"""Tests for ConsumptionService."""

import shutil
import tempfile
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from edata.connectors.datadis import DatadisConnector
from edata.models.consumption import Consumption, ConsumptionAggregated
from edata.services.consumption import ConsumptionService


class TestConsumptionService:
    """Test suite for ConsumptionService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_datadis_connector(self):
        """Mock DatadisConnector for testing."""
        with patch(
            "edata.services.consumption.DatadisConnector"
        ) as mock_connector_class:
            mock_connector = Mock(spec=DatadisConnector)
            mock_connector_class.return_value = mock_connector
            yield mock_connector, mock_connector_class

    @pytest.fixture
    def mock_database_service(self):
        """Mock DatabaseService for testing."""
        with patch("edata.services.consumption.get_database_service") as mock_get_db:
            mock_db = Mock()
            # Hacer que los métodos async retornen AsyncMock
            mock_db.get_consumptions = AsyncMock(return_value=[])
            mock_db.save_consumption = AsyncMock(return_value=Mock())
            mock_db.get_latest_consumption = AsyncMock(return_value=None)
            mock_get_db.return_value = mock_db
            yield mock_db

    @pytest_asyncio.fixture
    async def consumption_service(
        self, temp_dir, mock_datadis_connector, mock_database_service
    ):
        """Create a ConsumptionService instance for testing."""
        mock_connector, mock_connector_class = mock_datadis_connector
        return ConsumptionService(
            datadis_connector=mock_connector,
            storage_dir=temp_dir,
        )

    @pytest.fixture
    def sample_consumptions(self):
        """Sample consumption data for testing."""
        return [
            Consumption(
                datetime=datetime(2024, 6, 15, 10, 0),
                delta_h=1.0,
                value_kwh=0.5,
                surplus_kwh=0.0,
                real=True,
            ),
            Consumption(
                datetime=datetime(2024, 6, 15, 11, 0),
                delta_h=1.0,
                value_kwh=0.7,
                surplus_kwh=0.0,
                real=True,
            ),
            Consumption(
                datetime=datetime(2024, 6, 15, 12, 0),
                delta_h=1.0,
                value_kwh=0.6,
                surplus_kwh=0.0,
                real=True,
            ),
        ]

    @pytest.mark.asyncio
    async def test_initialization(
        self, temp_dir, mock_datadis_connector, mock_database_service
    ):
        """Test ConsumptionService initialization."""
        mock_connector, mock_connector_class = mock_datadis_connector

        service = ConsumptionService(
            datadis_connector=mock_connector,
            storage_dir=temp_dir,
        )

        # Verify service stores the connector and storage directory
        assert service._datadis == mock_connector
        assert service._storage_dir == temp_dir

        # Verify database service is obtained lazily by calling _get_db_service
        db_service = await service._get_db_service()
        assert db_service is mock_database_service

    @pytest.mark.asyncio
    async def test_update_consumptions_success(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test successful consumption update."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions

        # Mock database service responses - no existing consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute update
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify datadis connector was called correctly
        mock_connector.get_consumption_data.assert_called_once_with(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
            measurement_type="0",
            point_type=5,
            authorized_nif=None,
        )

        # Verify database service was called for each consumption
        assert mock_database_service.save_consumption.call_count == len(
            sample_consumptions
        )

        # Verify result structure
        assert result["success"] is True
        assert result["cups"] == cups
        assert result["period"]["start"] == start_date.isoformat()
        assert result["period"]["end"] == end_date.isoformat()
        assert result["stats"]["fetched"] == len(sample_consumptions)
        assert result["stats"]["saved"] == len(sample_consumptions)
        assert result["stats"]["updated"] == 0

    @pytest.mark.asyncio
    async def test_update_consumptions_with_existing_data(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption update with some existing data."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions

        # Mock get_latest_consumption to return an existing consumption before the start date
        mock_latest = Mock()
        mock_latest.datetime = datetime(2024, 6, 14, 23, 0)  # Day before start_date
        mock_database_service.get_latest_consumption.return_value = mock_latest

        # Mock database service responses - first consumption exists, others don't
        def mock_get_consumptions(cups, start_date, end_date):
            if start_date == sample_consumptions[0].datetime:
                return [Mock()]  # Existing consumption
            return []  # No existing consumption

        mock_database_service.get_consumptions.side_effect = mock_get_consumptions

        # Execute update
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify result
        assert result["success"] is True
        assert result["stats"]["fetched"] == len(sample_consumptions)
        assert result["stats"]["saved"] == 2  # Two new consumptions
        assert result["stats"]["updated"] == 1  # One updated consumption

    @pytest.mark.asyncio
    async def test_update_consumptions_with_optional_parameters(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption update with optional parameters."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)
        measurement_type = "1"
        point_type = 3
        authorized_nif = "12345678A"

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute update with optional parameters
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
            measurement_type=measurement_type,
            point_type=point_type,
            authorized_nif=authorized_nif,
        )

        # Verify datadis connector was called with optional parameters
        mock_connector.get_consumption_data.assert_called_once_with(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
            measurement_type=measurement_type,
            point_type=point_type,
            authorized_nif=authorized_nif,
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_consumptions_error_handling(
        self, consumption_service, mock_datadis_connector, mock_database_service
    ):
        """Test consumption update error handling."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector to raise an exception
        error_message = "API connection failed"
        mock_connector.get_consumption_data.side_effect = Exception(error_message)

        # Mock database service to return None for get_latest_consumption (no existing data)
        mock_database_service.get_latest_consumption.return_value = None

        # Execute update
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify error result
        assert result["success"] is False
        assert result["cups"] == cups
        assert result["error"] == error_message
        assert result["period"]["start"] == start_date.isoformat()
        assert result["period"]["end"] == end_date.isoformat()

        # Verify database service was not called
        mock_database_service.save_consumption.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_consumptions_with_force_full_update(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption update with force_full_update=True ignores existing data."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector response
        mock_connector.get_consumption_data.return_value = sample_consumptions

        # Mock get_latest_consumption to return existing data
        mock_latest = Mock()
        mock_latest.datetime = datetime(
            2024, 6, 15, 12, 0
        )  # Within the requested range
        mock_database_service.get_latest_consumption.return_value = mock_latest

        # Mock database service responses - no existing consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute update with force_full_update=True
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
            force_full_update=True,
        )

        # Verify datadis connector was called with original start_date (not optimized)
        mock_connector.get_consumption_data.assert_called_once_with(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,  # Should use original start_date, not optimized
            end_date=end_date,
            measurement_type="0",
            point_type=5,
            authorized_nif=None,
        )

        # Verify result
        assert result["success"] is True
        assert result["stats"]["fetched"] == len(sample_consumptions)

    @pytest.mark.asyncio
    async def test_update_consumptions_incremental_optimization(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test that consumption update optimizes by starting from last consumption date."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector response
        mock_connector.get_consumption_data.return_value = sample_consumptions

        # Mock get_latest_consumption to return existing data
        mock_latest = Mock()
        mock_latest.datetime = datetime(2024, 6, 15, 8, 0)  # 8 AM on same day
        mock_database_service.get_latest_consumption.return_value = mock_latest

        # Mock database service responses - no existing consumptions for the new range
        mock_database_service.get_consumptions.return_value = []

        # Execute update
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify datadis connector was called with optimized start_date (9 AM)
        expected_optimized_start = datetime(2024, 6, 15, 9, 0)  # last + 1 hour
        mock_connector.get_consumption_data.assert_called_once_with(
            cups=cups,
            distributor_code=distributor_code,
            start_date=expected_optimized_start,  # Should be optimized
            end_date=end_date,
            measurement_type="0",
            point_type=5,
            authorized_nif=None,
        )

        # Verify result includes message about optimization
        assert result["success"] is True
        assert "message" in result
        assert "missing data" in result["message"]

    @pytest.mark.asyncio
    async def test_update_consumptions_up_to_date(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
    ):
        """Test consumption update when data is already up to date."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock get_latest_consumption to return data beyond end_date
        mock_latest = Mock()
        mock_latest.datetime = datetime(2024, 6, 16, 1, 0)  # After end_date
        mock_database_service.get_latest_consumption.return_value = mock_latest

        # Execute update
        result = await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify datadis connector was NOT called (data is up to date)
        mock_connector.get_consumption_data.assert_not_called()

        # Verify result indicates no new data needed
        assert result["success"] is True
        assert result["stats"]["fetched"] == 0
        assert result["stats"]["skipped"] == "up_to_date"
        assert "up to date" in result["message"]

    @pytest.mark.asyncio
    async def test_update_consumption_range_by_months_single_month(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption range update for a single month."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 1, 0, 0)
        end_date = datetime(2024, 6, 30, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute range update
        result = await consumption_service.update_consumption_range_by_months(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify result structure
        assert result["success"] is True
        assert result["cups"] == cups
        assert result["months_processed"] == 1
        assert result["total_stats"]["consumptions_fetched"] == len(sample_consumptions)
        assert result["total_stats"]["consumptions_saved"] == len(sample_consumptions)
        assert result["total_stats"]["consumptions_updated"] == 0
        assert len(result["monthly_results"]) == 1

        # Verify monthly result
        monthly_result = result["monthly_results"][0]
        assert monthly_result["month"] == "2024-06"
        assert monthly_result["consumption"]["success"] is True

    @pytest.mark.asyncio
    async def test_update_consumption_range_by_months_multiple_months(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption range update for multiple months."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 5, 15, 0, 0)
        end_date = datetime(2024, 7, 15, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute range update
        result = await consumption_service.update_consumption_range_by_months(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Should process 3 months: May (partial), June (full), July (partial)
        assert result["months_processed"] == 3
        assert len(result["monthly_results"]) == 3

        # Verify month identifiers
        months = [r["month"] for r in result["monthly_results"]]
        assert "2024-05" in months
        assert "2024-06" in months
        assert "2024-07" in months

        # Verify total stats
        expected_total_fetched = len(sample_consumptions) * 3
        assert result["total_stats"]["consumptions_fetched"] == expected_total_fetched

    @pytest.mark.asyncio
    async def test_update_consumption_range_by_months_with_errors(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption range update with some months failing."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 1, 0, 0)
        end_date = datetime(2024, 8, 31, 23, 59)

        # Mock datadis connector to fail on second call
        call_count = 0

        def mock_get_consumption_data(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # Second month fails
                raise Exception("API rate limit exceeded")
            return sample_consumptions

        mock_connector.get_consumption_data.side_effect = mock_get_consumption_data
        mock_database_service.get_consumptions.return_value = []

        # Execute range update
        result = await consumption_service.update_consumption_range_by_months(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Should process 3 months but with one failure
        assert result["months_processed"] == 3
        assert result["success"] is False  # Overall failure due to one failed month

        # Check individual month results
        successful_months = [
            r for r in result["monthly_results"] if r["consumption"]["success"]
        ]
        failed_months = [
            r for r in result["monthly_results"] if not r["consumption"]["success"]
        ]

        assert len(successful_months) == 2
        assert len(failed_months) == 1

    @pytest.mark.asyncio
    async def test_update_consumption_range_year_boundary(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test consumption range update across year boundary."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2023, 12, 1, 0, 0)
        end_date = datetime(2024, 2, 28, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute range update
        result = await consumption_service.update_consumption_range_by_months(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Should process 3 months: December 2023, January 2024, February 2024
        assert result["months_processed"] == 3

        # Verify month identifiers
        months = [r["month"] for r in result["monthly_results"]]
        assert "2023-12" in months
        assert "2024-01" in months
        assert "2024-02" in months

    @pytest.mark.asyncio
    async def test_get_stored_consumptions_no_filters(
        self, consumption_service, mock_database_service, sample_consumptions
    ):
        """Test getting stored consumptions without date filters."""
        cups = "ES1234567890123456789"

        # Mock database service response
        mock_database_service.get_consumptions.return_value = sample_consumptions

        # Execute get stored consumptions
        result = await consumption_service.get_stored_consumptions(cups)

        # Verify database service was called correctly
        mock_database_service.get_consumptions.assert_called_once_with(cups, None, None)

        # Verify result
        assert result == sample_consumptions

    @pytest.mark.asyncio
    async def test_get_stored_consumptions_with_filters(
        self, consumption_service, mock_database_service, sample_consumptions
    ):
        """Test getting stored consumptions with date filters."""
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock database service response
        filtered_consumptions = sample_consumptions[:2]  # Return first two
        mock_database_service.get_consumptions.return_value = filtered_consumptions

        # Execute get stored consumptions with filters
        result = await consumption_service.get_stored_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Verify database service was called correctly
        mock_database_service.get_consumptions.assert_called_once_with(
            cups, start_date, end_date
        )

        # Verify result
        assert result == filtered_consumptions

    @pytest.mark.asyncio
    async def test_initialization_default_parameters(
        self, temp_dir, mock_datadis_connector, mock_database_service
    ):
        """Test ConsumptionService initialization with default parameters."""
        mock_connector, mock_connector_class = mock_datadis_connector

        service = ConsumptionService(datadis_connector=mock_connector)

        # Verify service stores the connector with default storage directory
        assert service._datadis == mock_connector
        assert service._storage_dir is None

    @patch("edata.services.consumption._LOGGER")
    @pytest.mark.asyncio
    async def test_logging_during_operations(
        self,
        mock_logger,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_consumptions,
    ):
        """Test that appropriate logging occurs during operations."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        distributor_code = "123"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock datadis connector response (now returns Pydantic models)
        mock_connector.get_consumption_data.return_value = sample_consumptions
        mock_database_service.get_consumptions.return_value = []

        # Execute update
        await consumption_service.update_consumptions(
            cups=cups,
            distributor_code=distributor_code,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify logging calls
        assert mock_logger.info.call_count >= 2  # Start and completion logs

        # Verify log messages contain expected information
        log_calls = [call.args[0] for call in mock_logger.info.call_args_list]
        assert any("Updating consumptions" in msg for msg in log_calls)
        assert any("Consumption update completed" in msg for msg in log_calls)

    @pytest.fixture
    def sample_db_consumptions(self):
        """Sample database consumption data for aggregation testing."""
        from edata.services.database import ConsumptionModel as DbConsumption

        # Use Monday (weekday 0) instead of Saturday for proper tariff testing
        base_date = datetime(2024, 6, 17)  # Monday, June 17, 2024

        # Create 48 hours of hourly data (2 days: Monday and Tuesday)
        db_consumptions = []
        for hour in range(48):
            dt = base_date + timedelta(hours=hour)
            # Vary consumption by hour to test tariff periods
            if 10 <= dt.hour <= 13 or 18 <= dt.hour <= 21:  # P1 hours
                kwh = 1.5
            elif dt.hour in [8, 9, 14, 15, 16, 17, 22, 23]:  # P2 hours
                kwh = 1.0
            else:  # P3 hours
                kwh = 0.5

            db_cons = Mock(spec=DbConsumption)
            db_cons.datetime = dt
            db_cons.delta_h = 1.0
            db_cons.value_kwh = kwh
            db_cons.surplus_kwh = (
                0.1 if hour % 10 == 0 else 0.0
            )  # Some surplus every 10 hours
            db_cons.real = True

            db_consumptions.append(db_cons)

        return db_consumptions

    @pytest.mark.asyncio
    async def test_get_daily_consumptions(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_db_consumptions,
    ):
        """Test daily consumption aggregation."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 17, 0, 0)  # Monday
        end_date = datetime(2024, 6, 18, 23, 59)  # Tuesday

        # Mock database service to return sample data
        mock_database_service.get_consumptions.return_value = sample_db_consumptions

        # Execute daily aggregation
        daily_consumptions = await consumption_service.get_daily_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Verify database service was called correctly
        mock_database_service.get_consumptions.assert_called_once_with(
            cups, start_date, end_date
        )

        # Should have 2 days of data
        assert len(daily_consumptions) == 2

        # Verify first day aggregation
        day1 = daily_consumptions[0]
        assert isinstance(day1, ConsumptionAggregated)
        assert day1.datetime.date() == date(2024, 6, 17)  # Monday
        assert day1.delta_h == 24.0  # 24 hours

        # Verify total consumption (should be sum of all hourly values)
        expected_day1_total = (8 * 1.5) + (8 * 1.0) + (8 * 0.5)  # P1 + P2 + P3 hours
        assert day1.value_kwh == expected_day1_total

        # Verify P1 consumption (hours 10-13, 18-21)
        expected_p1 = 8 * 1.5  # 8 P1 hours at 1.5 kWh each
        assert day1.value_p1_kwh == expected_p1

        # Verify some surplus was recorded
        assert day1.surplus_kwh > 0

        # Verify second day
        day2 = daily_consumptions[1]
        assert day2.datetime.date() == date(2024, 6, 18)  # Tuesday
        assert day2.delta_h == 24.0

    @pytest.mark.asyncio
    async def test_get_monthly_consumptions(
        self,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
        sample_db_consumptions,
    ):
        """Test monthly consumption aggregation."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 17, 0, 0)  # Monday
        end_date = datetime(2024, 6, 18, 23, 59)  # Tuesday

        # Mock database service to return sample data
        mock_database_service.get_consumptions.return_value = sample_db_consumptions

        # Execute monthly aggregation
        monthly_consumptions = await consumption_service.get_monthly_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Verify database service was called correctly
        mock_database_service.get_consumptions.assert_called_once_with(
            cups, start_date, end_date
        )

        # Should have 1 month of data (both days in same month)
        assert len(monthly_consumptions) == 1

        # Verify monthly aggregation
        month = monthly_consumptions[0]
        assert isinstance(month, ConsumptionAggregated)
        assert month.datetime.replace(day=1).date() == date(2024, 6, 1)
        assert month.delta_h == 48.0  # 48 hours total

        # Verify total consumption (should be sum of both days)
        expected_total = 2 * ((8 * 1.5) + (8 * 1.0) + (8 * 0.5))
        assert month.value_kwh == expected_total

        # Verify P1 consumption
        expected_p1 = 2 * (8 * 1.5)  # 2 days * 8 P1 hours * 1.5 kWh
        assert month.value_p1_kwh == expected_p1

    @pytest.mark.asyncio
    async def test_get_monthly_consumptions_with_cycle_start_day(
        self, consumption_service, mock_datadis_connector, mock_database_service
    ):
        """Test monthly consumption aggregation with custom cycle start day."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 1, 0, 0)
        end_date = datetime(2024, 6, 30, 23, 59)

        # Create sample data spanning across billing cycle boundary
        from edata.services.database import ConsumptionModel as DbConsumption

        db_consumptions = []

        # Data on June 14th (before cycle start)
        dt1 = datetime(2024, 6, 14, 12, 0)
        db_cons1 = Mock(spec=DbConsumption)
        db_cons1.datetime = dt1
        db_cons1.delta_h = 1.0
        db_cons1.value_kwh = 2.0
        db_cons1.surplus_kwh = 0.0
        db_cons1.real = True
        db_consumptions.append(db_cons1)

        # Data on June 16th (after cycle start)
        dt2 = datetime(2024, 6, 16, 12, 0)
        db_cons2 = Mock(spec=DbConsumption)
        db_cons2.datetime = dt2
        db_cons2.delta_h = 1.0
        db_cons2.value_kwh = 3.0
        db_cons2.surplus_kwh = 0.0
        db_cons2.real = True
        db_consumptions.append(db_cons2)

        mock_database_service.get_consumptions.return_value = db_consumptions

        # Execute with cycle start day = 15
        monthly_consumptions = await consumption_service.get_monthly_consumptions(
            cups=cups, start_date=start_date, end_date=end_date, cycle_start_day=15
        )

        # Should have 2 months (May billing period and June billing period)
        assert len(monthly_consumptions) == 2

        # Verify the months
        months = sorted([m.datetime for m in monthly_consumptions])
        assert months[0].month == 5  # May billing period (for June 14th data)
        assert months[1].month == 6  # June billing period (for June 16th data)

    @pytest.mark.asyncio
    async def test_get_daily_consumptions_empty_data(
        self, consumption_service, mock_datadis_connector, mock_database_service
    ):
        """Test daily consumption aggregation with no data."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 17, 0, 0)  # Monday
        end_date = datetime(2024, 6, 17, 23, 59)  # Monday

        # Mock database service to return empty data
        mock_database_service.get_consumptions.return_value = []

        # Execute daily aggregation
        daily_consumptions = await consumption_service.get_daily_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Should return empty list
        assert len(daily_consumptions) == 0

    @pytest.mark.asyncio
    async def test_get_monthly_consumptions_empty_data(
        self, consumption_service, mock_datadis_connector, mock_database_service
    ):
        """Test monthly consumption aggregation with no data."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 15, 0, 0)
        end_date = datetime(2024, 6, 15, 23, 59)

        # Mock database service to return empty data
        mock_database_service.get_consumptions.return_value = []

        # Execute monthly aggregation
        monthly_consumptions = await consumption_service.get_monthly_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Should return empty list
        assert len(monthly_consumptions) == 0

    @pytest.mark.asyncio
    @patch("edata.services.consumption.get_pvpc_tariff")
    async def test_tariff_calculation_in_aggregations(
        self,
        mock_get_pvpc_tariff,
        consumption_service,
        mock_datadis_connector,
        mock_database_service,
    ):
        """Test that tariff calculation is used correctly in aggregations."""
        mock_connector, mock_connector_class = mock_datadis_connector
        cups = "ES1234567890123456789"
        start_date = datetime(2024, 6, 17, 0, 0)  # Monday
        end_date = datetime(2024, 6, 17, 23, 59)  # Monday

        # Create single consumption data
        from edata.services.database import ConsumptionModel as DbConsumption

        db_cons = Mock(spec=DbConsumption)
        db_cons.datetime = datetime(2024, 6, 17, 12, 0)  # Monday noon
        db_cons.delta_h = 1.0
        db_cons.value_kwh = 2.0
        db_cons.surplus_kwh = 0.1
        db_cons.real = True

        mock_database_service.get_consumptions.return_value = [db_cons]

        # Mock tariff calculation to return P2
        mock_get_pvpc_tariff.return_value = "p2"

        # Execute daily aggregation with await
        daily_consumptions = await consumption_service.get_daily_consumptions(
            cups=cups, start_date=start_date, end_date=end_date
        )

        # Verify tariff function was called
        mock_get_pvpc_tariff.assert_called_with(datetime(2024, 6, 17, 12, 0))

        # Verify P2 values were set correctly
        assert len(daily_consumptions) == 1
        day = daily_consumptions[0]
        assert day.value_p2_kwh == 2.0
        assert day.surplus_p2_kwh == 0.1
        assert day.value_p1_kwh == 0.0
        assert day.value_p3_kwh == 0.0
