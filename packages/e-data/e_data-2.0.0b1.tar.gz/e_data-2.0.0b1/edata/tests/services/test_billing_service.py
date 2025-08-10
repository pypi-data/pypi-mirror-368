"""Tests for BillingService."""

import shutil
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from edata.models.pricing import PricingData, PricingRules
from edata.services.billing import BillingService


class TestBillingService:
    """Test suite for BillingService."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_redata_connector(self):
        """Mock REDataConnector for testing."""
        with patch("edata.services.billing.REDataConnector") as mock_connector_class:
            mock_connector = Mock()
            mock_connector_class.return_value = mock_connector
            yield mock_connector, mock_connector_class

    @pytest.fixture
    def mock_database_service(self):
        """Mock DatabaseService for testing."""
        with patch("edata.services.billing.get_database_service") as mock_get_db:
            mock_db = Mock()
            # Hacer que los métodos async retornen AsyncMock
            mock_db.get_pvpc_prices = AsyncMock(return_value=[])
            mock_db.save_pvpc_price = AsyncMock(return_value=Mock())
            mock_db.get_billing = AsyncMock(return_value=[])
            mock_db.save_billing = AsyncMock(return_value=Mock())
            mock_db.get_consumptions = AsyncMock(return_value=[])
            mock_db.get_contracts = AsyncMock(return_value=[])
            mock_db.generate_pricing_config_hash = Mock(return_value="test_hash")
            mock_db.get_latest_pvpc_price = AsyncMock(return_value=None)
            mock_db.get_latest_billing = AsyncMock(return_value=None)
            mock_get_db.return_value = mock_db
            yield mock_db

    @pytest_asyncio.fixture
    async def billing_service(
        self, temp_dir, mock_redata_connector, mock_database_service
    ):
        """Create a BillingService instance for testing."""
        return BillingService(storage_dir=temp_dir)

    @pytest.fixture
    def sample_pvpc_prices(self):
        """Sample PVPC price data for testing."""
        return [
            PricingData(
                datetime=datetime(2024, 6, 17, 10, 0),
                value_eur_kwh=0.12345,
                delta_h=1.0,
            ),
            PricingData(
                datetime=datetime(2024, 6, 17, 11, 0),
                value_eur_kwh=0.13456,
                delta_h=1.0,
            ),
            PricingData(
                datetime=datetime(2024, 6, 17, 12, 0),
                value_eur_kwh=0.14567,
                delta_h=1.0,
            ),
        ]

    @pytest.fixture
    def sample_pricing_rules_pvpc(self):
        """Sample pricing rules for PVPC configuration."""
        return PricingRules(
            p1_kw_year_eur=30.67,
            p2_kw_year_eur=1.42,
            p1_kwh_eur=None,  # PVPC
            p2_kwh_eur=None,  # PVPC
            p3_kwh_eur=None,  # PVPC
            surplus_p1_kwh_eur=0.05,
            surplus_p2_kwh_eur=0.04,
            surplus_p3_kwh_eur=0.03,
            meter_month_eur=0.81,
            market_kw_year_eur=3.11,
            electricity_tax=1.05113,
            iva_tax=1.21,
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term",
        )

    @pytest.fixture
    def sample_pricing_rules_custom(self):
        """Sample pricing rules for custom pricing configuration."""
        return PricingRules(
            p1_kw_year_eur=30.67,
            p2_kw_year_eur=1.42,
            p1_kwh_eur=0.15,  # Custom prices
            p2_kwh_eur=0.12,
            p3_kwh_eur=0.08,
            surplus_p1_kwh_eur=0.05,
            surplus_p2_kwh_eur=0.04,
            surplus_p3_kwh_eur=0.03,
            meter_month_eur=0.81,
            market_kw_year_eur=3.11,
            electricity_tax=1.05113,
            iva_tax=1.21,
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term",
        )

    @pytest.mark.asyncio
    async def test_initialization(
        self, temp_dir, mock_redata_connector, mock_database_service
    ):
        """Test BillingService initialization."""
        mock_connector, mock_connector_class = mock_redata_connector

        service = BillingService(storage_dir=temp_dir)

        # Verify REDataConnector was initialized
        mock_connector_class.assert_called_once()

        # Verify database service is obtained lazily by calling _get_db_service
        db_service = await service._get_db_service()
        assert db_service is mock_database_service

    @pytest.mark.asyncio
    async def test_update_pvpc_prices_success(
        self,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pvpc_prices,
    ):
        """Test successful PVPC price update."""
        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 0, 0)
        end_date = datetime(2024, 6, 17, 23, 59)

        # Mock REData connector response
        mock_connector.get_realtime_prices = AsyncMock(return_value=sample_pvpc_prices)

        # Mock database service responses - no existing prices
        mock_database_service.get_pvpc_prices.return_value = []

        # Execute PVPC update
        result = await billing_service.update_pvpc_prices(
            start_date=start_date, end_date=end_date, is_ceuta_melilla=False
        )

        # Verify REData connector was called correctly
        mock_connector.get_realtime_prices.assert_called_once_with(
            dt_from=start_date, dt_to=end_date, is_ceuta_melilla=False
        )

        # Verify database service was called for each price
        assert mock_database_service.save_pvpc_price.call_count == len(
            sample_pvpc_prices
        )

        # Verify result structure
        assert result["success"] is True
        assert result["region"] == "Peninsula"
        assert result["geo_id"] == 8741
        assert result["stats"]["fetched"] == len(sample_pvpc_prices)
        assert result["stats"]["saved"] == len(sample_pvpc_prices)
        assert result["stats"]["updated"] == 0

    @patch("edata.utils.get_pvpc_tariff")
    def test_get_custom_prices_success(
        self,
        mock_get_pvpc_tariff,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_custom,
    ):
        """Test successful custom price calculation."""
        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 10, 0)  # Monday 10 AM
        end_date = datetime(2024, 6, 17, 13, 0)  # Monday 1 PM (3 hours)

        # Mock tariff calculation to cycle through periods
        mock_get_pvpc_tariff.side_effect = ["p1", "p1", "p1"]  # All P1 hours

        # Execute custom price calculation (not async)
        result = billing_service.get_custom_prices(
            pricing_rules=sample_pricing_rules_custom,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify tariff function was called for each hour
        assert mock_get_pvpc_tariff.call_count == 3

        # Verify result structure
        assert len(result) == 3
        assert all(isinstance(price, PricingData) for price in result)
        assert all(
            price.value_eur_kwh == sample_pricing_rules_custom.p1_kwh_eur
            for price in result
        )

    @pytest.mark.asyncio
    async def test_get_stored_pvpc_prices(
        self, billing_service, mock_redata_connector, mock_database_service
    ):
        """Test getting stored PVPC prices from database."""
        start_date = datetime(2024, 6, 17, 0, 0)
        end_date = datetime(2024, 6, 17, 23, 59)
        geo_id = 8741

        # Mock database service response
        mock_prices = [Mock(), Mock(), Mock()]
        mock_database_service.get_pvpc_prices.return_value = mock_prices

        # Execute get stored prices
        result = await billing_service.get_stored_pvpc_prices(
            start_date=start_date, end_date=end_date, geo_id=geo_id
        )

        # Verify database service was called correctly
        mock_database_service.get_pvpc_prices.assert_called_once_with(
            start_date, end_date, geo_id
        )

        # Verify result
        assert result == mock_prices

    @pytest.mark.asyncio
    async def test_get_prices_pvpc(
        self,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_pvpc,
    ):
        """Test automatic price retrieval with PVPC configuration."""
        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 0, 0)
        end_date = datetime(2024, 6, 17, 23, 59)

        # Mock stored PVPC prices
        mock_pvpc_prices = [
            Mock(
                datetime=datetime(2024, 6, 17, 10, 0), value_eur_kwh=0.15, delta_h=1.0
            ),
            Mock(
                datetime=datetime(2024, 6, 17, 11, 0), value_eur_kwh=0.16, delta_h=1.0
            ),
        ]
        mock_database_service.get_pvpc_prices.return_value = mock_pvpc_prices

        # Execute automatic price retrieval with PVPC rules
        result = await billing_service.get_prices(
            pricing_rules=sample_pricing_rules_pvpc,
            start_date=start_date,
            end_date=end_date,
            is_ceuta_melilla=False,
        )

        # Should call PVPC retrieval
        mock_database_service.get_pvpc_prices.assert_called_once()
        assert len(result) == 2
        assert all(isinstance(price, PricingData) for price in result)

    @patch("edata.utils.get_pvpc_tariff")
    @pytest.mark.asyncio
    async def test_get_prices_custom(
        self,
        mock_get_pvpc_tariff,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_custom,
    ):
        """Test automatic price retrieval with custom configuration."""
        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 11, 0)

        # Mock tariff calculation
        mock_get_pvpc_tariff.return_value = "p1"

        # Execute automatic price retrieval with custom rules
        result = await billing_service.get_prices(
            pricing_rules=sample_pricing_rules_custom,
            start_date=start_date,
            end_date=end_date,
        )

        # Should call custom calculation (not database)
        mock_database_service.get_pvpc_prices.assert_not_called()
        assert len(result) == 1
        assert isinstance(result[0], PricingData)
        assert result[0].value_eur_kwh == sample_pricing_rules_custom.p1_kwh_eur

    @pytest.mark.asyncio
    async def test_get_prices_pvpc_no_data(
        self,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_pvpc,
    ):
        """Test automatic price retrieval with PVPC configuration but no data."""
        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 0, 0)
        end_date = datetime(2024, 6, 17, 23, 59)

        # Mock no PVPC prices available
        mock_database_service.get_pvpc_prices.return_value = []

        # Execute automatic price retrieval with PVPC rules
        result = await billing_service.get_prices(
            pricing_rules=sample_pricing_rules_pvpc,
            start_date=start_date,
            end_date=end_date,
            is_ceuta_melilla=False,
        )

        # Should return None when no data available
        assert result is None
        mock_database_service.get_pvpc_prices.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_prices_custom_no_prices_defined(
        self, billing_service, mock_redata_connector, mock_database_service
    ):
        """Test automatic price retrieval with custom configuration but no prices defined."""
        from edata.models.pricing import PricingRules

        mock_connector, mock_connector_class = mock_redata_connector
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 11, 0)

        # Create pricing rules with no energy prices defined
        empty_pricing_rules = PricingRules(
            p1_kw_year_eur=30.67,
            p2_kw_year_eur=1.42,
            p1_kwh_eur=None,  # No custom prices
            p2_kwh_eur=None,
            p3_kwh_eur=None,
            surplus_p1_kwh_eur=0.05,
            surplus_p2_kwh_eur=0.04,
            surplus_p3_kwh_eur=0.03,
            meter_month_eur=0.81,
            market_kw_year_eur=3.11,
            electricity_tax=1.05113,
            iva_tax=1.21,
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term",
        )

        # Mock empty PVPC prices since rules indicate PVPC usage
        mock_database_service.get_pvpc_prices.return_value = []

        # Execute automatic price retrieval with empty custom rules
        result = await billing_service.get_prices(
            pricing_rules=empty_pricing_rules, start_date=start_date, end_date=end_date
        )

        # Should return None when no PVPC prices available
        assert result is None
        # Should have tried to get PVPC prices since no custom prices are defined
        mock_database_service.get_pvpc_prices.assert_called_once_with(
            start_date, end_date, 8741
        )

    @pytest.mark.asyncio
    @patch("edata.utils.get_pvpc_tariff")
    async def test_get_cost_calculation(
        self,
        mock_get_pvpc_tariff,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_custom,
    ):
        """Test cost calculation functionality."""
        from datetime import datetime

        from edata.models.pricing import PricingAggregated

        mock_connector, mock_connector_class = mock_redata_connector
        cups = "ES0123456789012345AB"
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 12, 0)  # 2 hours

        # Mock no existing billing data initially
        mock_database_service.get_billing.return_value = []

        # Mock the pricing config hash generation
        mock_database_service.generate_pricing_config_hash.return_value = (
            "test_hash_12345678"
        )

        # Mock consumption data
        mock_consumptions = [
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "value_kwh": 0.5,
                    "surplus_kwh": 0.0,
                },
            )(),
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 11, 0),
                    "value_kwh": 0.6,
                    "surplus_kwh": 0.0,
                },
            )(),
        ]
        mock_database_service.get_consumptions.return_value = mock_consumptions

        # Mock contract data
        mock_contracts = [
            type(
                "MockContract",
                (),
                {
                    "power_p1": 4.0,
                    "power_p2": 4.0,
                    "date_start": datetime(2024, 6, 17, 0, 0),
                    "date_end": datetime(2024, 6, 18, 0, 0),
                },
            )()
        ]
        mock_database_service.get_contracts.return_value = mock_contracts

        # Mock the save_billing method to return a success response
        mock_database_service.save_billing.return_value = type("MockBilling", (), {})()

        # Mock billing data after calculation
        mock_billing_results = [
            type(
                "MockBilling",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "total_eur": 0.05,
                    "energy_term": 0.03,
                    "power_term": 0.015,
                    "others_term": 0.005,
                    "surplus_term": 0.0,
                },
            )(),
            type(
                "MockBilling",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 11, 0),
                    "total_eur": 0.06,
                    "energy_term": 0.036,
                    "power_term": 0.015,
                    "others_term": 0.005,
                    "surplus_term": 0.0,
                },
            )(),
        ]

        # Configure get_billing to return empty first, then billing results after update_missing_costs
        mock_database_service.get_billing.side_effect = [
            [],
            mock_billing_results,
            mock_billing_results,
        ]

        # Mock tariff calculation - need one call per hour in the data
        mock_get_pvpc_tariff.return_value = (
            "p1"  # Use return_value instead of side_effect
        )

        # Execute cost calculation
        result = await billing_service.get_cost(
            cups=cups,
            pricing_rules=sample_pricing_rules_custom,
            start_date=start_date,
            end_date=end_date,
        )

        # Validate result aggregation from mocked billing data
        assert isinstance(result, PricingAggregated)
        assert result.datetime == start_date
        assert result.value_eur == 0.11  # 0.05 + 0.06
        assert result.energy_term == 0.066  # 0.03 + 0.036
        assert result.power_term == 0.03  # 0.015 + 0.015
        assert result.others_term == 0.01  # 0.005 + 0.005
        assert result.surplus_term == 0.0
        assert result.delta_h == 2  # 2 billing records

        # Verify database calls
        mock_database_service.get_consumptions.assert_called_once_with(
            cups, start_date, end_date
        )
        mock_database_service.get_contracts.assert_called_once_with(cups)

    @pytest.mark.asyncio
    async def test_get_cost_no_consumption_data(
        self,
        billing_service,
        mock_redata_connector,
        mock_database_service,
        sample_pricing_rules_custom,
    ):
        """Test cost calculation with no consumption data."""
        from datetime import datetime

        from edata.models.pricing import PricingAggregated

        mock_connector, mock_connector_class = mock_redata_connector
        cups = "ES0123456789012345AB"
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 12, 0)

        # Mock no existing billing data initially
        mock_database_service.get_billing.return_value = []

        # Mock the pricing config hash generation
        mock_database_service.generate_pricing_config_hash.return_value = (
            "test_hash_12345678"
        )

        # Mock no consumption data
        mock_database_service.get_consumptions.return_value = []

        # Execute cost calculation
        result = await billing_service.get_cost(
            cups=cups,
            pricing_rules=sample_pricing_rules_custom,
            start_date=start_date,
            end_date=end_date,
        )

        # Should return default values when update_missing_costs fails
        assert isinstance(result, PricingAggregated)
        assert result.value_eur == 0.0
        assert result.energy_term == 0.0
        assert result.power_term == 0.0
        assert result.others_term == 0.0
        assert result.surplus_term == 0.0
        assert result.delta_h == 2.0  # (end_date - start_date).total_seconds() / 3600

    @pytest.mark.asyncio
    async def test_get_cost_no_pricing_data(
        self, billing_service, mock_redata_connector, mock_database_service
    ):
        """Test cost calculation with no pricing data available."""
        from datetime import datetime

        from edata.models.pricing import PricingAggregated, PricingRules

        mock_connector, mock_connector_class = mock_redata_connector
        cups = "ES0123456789012345AB"
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 12, 0)

        # Mock no existing billing data initially
        mock_database_service.get_billing.return_value = []

        # Mock the pricing config hash generation
        mock_database_service.generate_pricing_config_hash.return_value = (
            "test_hash_12345678"
        )

        # Mock consumption data present
        mock_consumptions = [
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "value_kwh": 0.5,
                    "surplus_kwh": 0.0,
                },
            )()
        ]
        mock_database_service.get_consumptions.return_value = mock_consumptions

        # Mock contract data present
        mock_contracts = [
            type(
                "MockContract",
                (),
                {
                    "power_p1": 4.0,
                    "power_p2": 4.0,
                    "date_start": datetime(2024, 6, 17, 0, 0),
                    "date_end": datetime(2024, 6, 18, 0, 0),
                },
            )()
        ]
        mock_database_service.get_contracts.return_value = mock_contracts

        # Mock no PVPC prices available
        mock_database_service.get_pvpc_prices.return_value = []

        # Create PVPC pricing rules
        pvpc_pricing_rules = PricingRules(
            p1_kw_year_eur=30.67,
            p2_kw_year_eur=1.42,
            p1_kwh_eur=None,  # PVPC
            p2_kwh_eur=None,
            p3_kwh_eur=None,
            surplus_p1_kwh_eur=0.05,
            surplus_p2_kwh_eur=0.04,
            surplus_p3_kwh_eur=0.03,
            meter_month_eur=0.81,
            market_kw_year_eur=3.11,
            electricity_tax=1.05113,
            iva_tax=1.21,
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term",
        )

        # Execute cost calculation
        result = await billing_service.get_cost(
            cups=cups,
            pricing_rules=pvpc_pricing_rules,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify result when no pricing data available
        assert isinstance(result, PricingAggregated)
        assert result.datetime == start_date
        assert result.value_eur == 0.0
        assert result.energy_term == 0.0
        assert result.power_term == 0.0
        assert result.others_term == 0.0
        assert result.surplus_term == 0.0

    @pytest.mark.asyncio
    async def test_jinja2_formula_evaluation(
        self, billing_service, mock_redata_connector, mock_database_service
    ):
        """Test Jinja2 formula evaluation with predictable values."""
        from datetime import datetime

        from edata.models.pricing import PricingAggregated, PricingRules

        mock_connector, mock_connector_class = mock_redata_connector
        cups = "ES0123456789012345AB"
        start_date = datetime(2024, 6, 17, 10, 0)  # P1 period (Monday 10:00)
        end_date = datetime(2024, 6, 17, 11, 0)  # 1 hour

        # Mock no existing billing data initially
        mock_database_service.get_billing.return_value = []

        # Mock the pricing config hash generation
        mock_database_service.generate_pricing_config_hash.return_value = (
            "test_hash_12345678"
        )

        # Mock predictable consumption data: 1 kWh consumed, 0.5 kWh surplus
        mock_consumptions = [
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "value_kwh": 1.0,
                    "surplus_kwh": 0.5,
                },
            )()
        ]
        mock_database_service.get_consumptions.return_value = mock_consumptions

        # Mock predictable contract data: 5kW P1, 3kW P2
        mock_contracts = [
            type(
                "MockContract",
                (),
                {
                    "power_p1": 5.0,
                    "power_p2": 3.0,
                    "date_start": datetime(2024, 6, 17, 0, 0),
                    "date_end": datetime(2024, 6, 18, 0, 0),
                },
            )()
        ]
        mock_database_service.get_contracts.return_value = mock_contracts

        # Mock predictable PVPC prices: 0.10 €/kWh
        mock_pvpc_prices = [
            type(
                "MockPVPCPrice",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "value_eur_kwh": 0.10,
                    "delta_h": 1.0,
                },
            )()
        ]
        mock_database_service.get_pvpc_prices.return_value = mock_pvpc_prices

        # Mock the save_billing method to return a success response
        mock_database_service.save_billing.return_value = type("MockBilling", (), {})()

        # Mock billing result after calculation (with predictable values)
        # Energy term: 1.05 * 1.21 * 0.10 * 1.0 = 0.12705
        expected_energy_term = 1.05 * 1.21 * 0.10 * 1.0
        # Power term: 1.05 * 1.21 * (5 * (40 + 4) + 3 * 20) / 365 / 24
        expected_power_term = 1.05 * 1.21 * (5 * (40 + 4) + 3 * 20) / 365 / 24
        # Others term: 1.21 * 3.0 / 30 / 24
        expected_others_term = 1.21 * 3.0 / 30 / 24
        # Surplus term: 1.05 * 1.21 * 0.5 * 0.06
        expected_surplus_term = 1.05 * 1.21 * 0.5 * 0.06
        # Total: energy + power + others - surplus
        expected_total = (
            expected_energy_term
            + expected_power_term
            + expected_others_term
            - expected_surplus_term
        )

        mock_billing_result = [
            type(
                "MockBilling",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "total_eur": expected_total,
                    "energy_term": expected_energy_term,
                    "power_term": expected_power_term,
                    "others_term": expected_others_term,
                    "surplus_term": expected_surplus_term,
                },
            )()
        ]

        # Configure get_billing to return empty first, then billing results after update_missing_costs
        mock_database_service.get_billing.side_effect = [
            [],
            mock_billing_result,
            mock_billing_result,
        ]

        # Create PVPC pricing rules with simplified formulas for testing
        test_pricing_rules = PricingRules(
            p1_kw_year_eur=40.0,  # €40/kW/year
            p2_kw_year_eur=20.0,  # €20/kW/year
            p1_kwh_eur=None,  # Use PVPC (0.10 €/kWh)
            p2_kwh_eur=None,
            p3_kwh_eur=None,
            surplus_p1_kwh_eur=0.06,  # €0.06/kWh surplus in P1
            surplus_p2_kwh_eur=0.04,  # €0.04/kWh surplus in P2
            surplus_p3_kwh_eur=0.02,  # €0.02/kWh surplus in P3
            meter_month_eur=3.0,  # €3/month meter
            market_kw_year_eur=4.0,  # €4/kW/year market
            electricity_tax=1.05,  # 5% electricity tax
            iva_tax=1.21,  # 21% IVA
            # Simplified formulas for predictable calculation
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term - surplus_term",
        )

        # Execute cost calculation
        result = await billing_service.get_cost(
            cups=cups,
            pricing_rules=test_pricing_rules,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify the result matches our mocked billing data
        assert isinstance(result, PricingAggregated)
        assert result.datetime == start_date
        assert result.delta_h == 1  # 1 billing record

        # Verify that the aggregated values match our expected calculations
        assert round(result.energy_term, 4) == round(expected_energy_term, 4)
        assert round(result.power_term, 4) == round(expected_power_term, 4)
        assert round(result.others_term, 4) == round(expected_others_term, 4)
        assert round(result.surplus_term, 4) == round(expected_surplus_term, 4)
        assert round(result.value_eur, 4) == round(expected_total, 4)
        assert round(result.value_eur, 5) == round(expected_total, 5)

    @pytest.mark.asyncio
    async def test_update_missing_costs(
        self, billing_service, mock_redata_connector, mock_database_service
    ):
        """Test update_missing_costs method."""
        from datetime import datetime

        from edata.models.pricing import PricingRules

        mock_connector, mock_connector_class = mock_redata_connector
        cups = "ES0123456789012345AB"
        start_date = datetime(2024, 6, 17, 10, 0)
        end_date = datetime(2024, 6, 17, 12, 0)

        # Mock consumption data
        mock_consumptions = [
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 10, 0),
                    "value_kwh": 0.5,
                    "surplus_kwh": 0.0,
                },
            )(),
            type(
                "MockConsumption",
                (),
                {
                    "datetime": datetime(2024, 6, 17, 11, 0),
                    "value_kwh": 0.7,
                    "surplus_kwh": 0.1,
                },
            )(),
        ]
        mock_database_service.get_consumptions.return_value = mock_consumptions

        # Mock contract data
        mock_contracts = [
            type(
                "MockContract",
                (),
                {
                    "power_p1": 4.0,
                    "power_p2": 4.0,
                    "date_start": datetime(2024, 6, 17, 0, 0),
                    "date_end": datetime(2024, 6, 18, 0, 0),
                },
            )()
        ]
        mock_database_service.get_contracts.return_value = mock_contracts

        # Mock no existing billing records
        mock_database_service.get_billing.return_value = []

        # Mock successful billing save
        mock_billing_record = type("MockBilling", (), {"id": 1})()
        mock_database_service.save_billing.return_value = mock_billing_record

        # Mock hash generation
        mock_database_service.generate_pricing_config_hash.return_value = (
            "test_hash_123"
        )

        # Create custom pricing rules (no PVPC)
        custom_pricing_rules = PricingRules(
            p1_kw_year_eur=30.0,
            p2_kw_year_eur=20.0,
            p1_kwh_eur=0.15,  # Custom prices - no PVPC
            p2_kwh_eur=0.12,
            p3_kwh_eur=0.10,
            surplus_p1_kwh_eur=0.06,
            surplus_p2_kwh_eur=0.04,
            surplus_p3_kwh_eur=0.02,
            meter_month_eur=3.0,
            market_kw_year_eur=4.0,
            electricity_tax=1.05,
            iva_tax=1.21,
            energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
            power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
            others_formula="iva_tax * meter_month_eur / 30 / 24",
            surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
            main_formula="energy_term + power_term + others_term - surplus_term",
        )

        # Execute update_missing_costs
        result = await billing_service.update_missing_costs(
            cups=cups,
            pricing_rules=custom_pricing_rules,
            start_date=start_date,
            end_date=end_date,
        )

        # Verify successful result
        assert result["success"] is True
        assert result["cups"] == cups
        assert result["pricing_config_hash"] == "test_hash_123"

        # Verify statistics
        stats = result["stats"]
        assert stats["total_consumptions"] == 2
        assert stats["processed"] > 0  # Should have processed some records

        # Verify database methods were called
        mock_database_service.get_consumptions.assert_called_once_with(
            cups, start_date, end_date
        )
        mock_database_service.get_contracts.assert_called_once_with(cups)
        mock_database_service.get_billing.assert_called_once()
        mock_database_service.generate_pricing_config_hash.assert_called_once()

        # Verify save_billing was called (at least once)
        assert mock_database_service.save_billing.call_count > 0

    @pytest.mark.asyncio
    async def test_get_daily_costs_with_existing_data(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test get_daily_costs with existing billing data."""
        from edata.models.database import BillingModel

        # Create mock billing records for 2 days
        base_date = datetime(2024, 1, 1, 0, 0, 0)
        mock_billing_records = []

        # Create 48 hours of billing data (2 days)
        for hour in range(48):
            record = BillingModel(
                datetime=base_date + timedelta(hours=hour),
                cups="ES0012345678901234567890AB",
                pricing_config_hash="test_hash",
                total_eur=1.5 + (hour * 0.1),  # Varying costs
                energy_term=1.0 + (hour * 0.05),
                power_term=0.3,
                others_term=0.1,
                surplus_term=0.1 + (hour * 0.05),
            )
            mock_billing_records.append(record)

        # Setup mocks
        mock_database_service.generate_pricing_config_hash.return_value = "test_hash"
        mock_database_service.get_billing.return_value = mock_billing_records

        # Test parameters
        cups = "ES0012345678901234567890AB"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2, 23, 59, 59)

        # Call method
        result = await billing_service.get_daily_costs(
            cups, sample_pricing_rules_custom, start_date, end_date
        )

        # Assertions
        assert len(result) == 2  # Two days
        from edata.models.pricing import PricingAggregated

        assert all(isinstance(item, PricingAggregated) for item in result)

        # Check first day
        first_day = result[0]
        assert first_day.datetime.date() == datetime(2024, 1, 1).date()
        assert first_day.delta_h == 24  # 24 hours
        assert first_day.value_eur > 0

        # Check second day
        second_day = result[1]
        assert second_day.datetime.date() == datetime(2024, 1, 2).date()
        assert second_day.delta_h == 24  # 24 hours
        assert (
            second_day.value_eur > first_day.value_eur
        )  # Should be higher due to increasing pattern

    @pytest.mark.asyncio
    async def test_get_daily_costs_without_existing_data(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test get_daily_costs when no billing data exists."""
        # Setup mocks - no existing data
        mock_database_service.generate_pricing_config_hash.return_value = "test_hash"
        mock_database_service.get_billing.side_effect = [
            [],
            [],
        ]  # First call empty, second still empty

        # Mock update_missing_costs to fail
        with patch.object(billing_service, "update_missing_costs") as mock_update:
            mock_update.return_value = {"success": False, "error": "Test error"}

            # Test parameters
            cups = "ES0012345678901234567890AB"
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2024, 1, 1, 23, 59, 59)

            # Call method
            result = await billing_service.get_daily_costs(
                cups, sample_pricing_rules_custom, start_date, end_date
            )

            # Assertions
            assert result == []  # Should return empty list when update fails
            mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_monthly_costs_with_existing_data(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test get_monthly_costs with existing billing data."""
        from edata.models.database import BillingModel

        # Create mock billing records for 2 days in same month
        base_date = datetime(2024, 1, 1, 0, 0, 0)
        mock_billing_records = []

        # Create 48 hours of billing data (2 days)
        for hour in range(48):
            record = BillingModel(
                datetime=base_date + timedelta(hours=hour),
                cups="ES0012345678901234567890AB",
                pricing_config_hash="test_hash",
                total_eur=1.5 + (hour * 0.1),  # Varying costs
                energy_term=1.0 + (hour * 0.05),
                power_term=0.3,
                others_term=0.1,
                surplus_term=0.1 + (hour * 0.05),
            )
            mock_billing_records.append(record)

        # Setup mocks
        mock_database_service.generate_pricing_config_hash.return_value = "test_hash"
        mock_database_service.get_billing.return_value = mock_billing_records

        # Test parameters
        cups = "ES0012345678901234567890AB"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31, 23, 59, 59)

        # Call method
        result = await billing_service.get_monthly_costs(
            cups, sample_pricing_rules_custom, start_date, end_date
        )

        # Assertions
        assert len(result) == 1  # One month
        from edata.models.pricing import PricingAggregated

        assert all(isinstance(item, PricingAggregated) for item in result)

        # Check month
        month_data = result[0]
        assert month_data.datetime.date() == datetime(2024, 1, 1).date()
        assert month_data.delta_h == 48  # 48 hours from mock data
        assert month_data.value_eur > 0

    @pytest.mark.asyncio
    async def test_get_monthly_costs_multiple_months(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test get_monthly_costs with data spanning multiple months."""
        from edata.models.database import BillingModel

        # Create billing records spanning two months
        records = []

        # January data (24 hours)
        for hour in range(24):
            record = BillingModel(
                datetime=datetime(2024, 1, 15) + timedelta(hours=hour),
                cups="ES0012345678901234567890AB",
                pricing_config_hash="test_hash",
                total_eur=1.0,
                energy_term=0.7,
                power_term=0.2,
                others_term=0.1,
                surplus_term=0.0,
            )
            records.append(record)

        # February data (24 hours)
        for hour in range(24):
            record = BillingModel(
                datetime=datetime(2024, 2, 15) + timedelta(hours=hour),
                cups="ES0012345678901234567890AB",
                pricing_config_hash="test_hash",
                total_eur=1.2,
                energy_term=0.8,
                power_term=0.3,
                others_term=0.1,
                surplus_term=0.0,
            )
            records.append(record)

        # Setup mocks
        mock_database_service.generate_pricing_config_hash.return_value = "test_hash"
        mock_database_service.get_billing.return_value = records

        # Test parameters
        cups = "ES0012345678901234567890AB"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 2, 28, 23, 59, 59)

        # Call method
        result = await billing_service.get_monthly_costs(
            cups, sample_pricing_rules_custom, start_date, end_date
        )

        # Assertions
        assert len(result) == 2  # Two months

        # Check January
        jan_data = result[0]
        assert jan_data.datetime.date() == datetime(2024, 1, 1).date()
        assert jan_data.delta_h == 24
        assert jan_data.value_eur == 24.0  # 24 hours * 1.0 EUR

        # Check February
        feb_data = result[1]
        assert feb_data.datetime.date() == datetime(2024, 2, 1).date()
        assert feb_data.delta_h == 24
        assert feb_data.value_eur == 28.8  # 24 hours * 1.2 EUR

    @pytest.mark.asyncio
    async def test_get_daily_costs_error_handling(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test error handling in get_daily_costs."""
        # Setup mocks to raise exception
        mock_database_service.generate_pricing_config_hash.side_effect = Exception(
            "Database error"
        )

        # Test parameters
        cups = "ES0012345678901234567890AB"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 1, 23, 59, 59)

        # Call method and expect exception
        with pytest.raises(Exception, match="Database error"):
            await billing_service.get_daily_costs(
                cups, sample_pricing_rules_custom, start_date, end_date
            )

    @pytest.mark.asyncio
    async def test_get_monthly_costs_error_handling(
        self, billing_service, mock_database_service, sample_pricing_rules_custom
    ):
        """Test error handling in get_monthly_costs."""
        # Setup mocks to raise exception
        mock_database_service.generate_pricing_config_hash.side_effect = Exception(
            "Database error"
        )

        # Test parameters
        cups = "ES0012345678901234567890AB"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31, 23, 59, 59)

        # Call method and expect exception
        with pytest.raises(Exception, match="Database error"):
            await billing_service.get_monthly_costs(
                cups, sample_pricing_rules_custom, start_date, end_date
            )
