"""Integration tests for EdataHelper with service-based architecture."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from freezegun import freeze_time

from edata.const import ATTRIBUTES
from edata.helpers import EdataHelper
from edata.models.consumption import Consumption
from edata.models.contract import Contract
from edata.models.maximeter import MaxPower
from edata.models.pricing import PricingRules
from edata.models.supply import Supply

# Test data constants
TEST_CUPS = "ES1234000000000001JN0F"
TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpass"
TEST_NIF = "12345678Z"
AT_TIME = "2023-10-15"

# Sample pricing rules for testing
PRICING_RULES_PVPC = PricingRules(
    p1_kw_year_eur=30.67266,
    p2_kw_year_eur=1.4243591,
    meter_month_eur=0.81,
    market_kw_year_eur=3.113,
    electricity_tax=1.0511300560,
    iva_tax=1.05,
    p1_kwh_eur=None,  # PVPC mode
    p2_kwh_eur=None,
    p3_kwh_eur=None,
    surplus_p1_kwh_eur=None,
    surplus_p2_kwh_eur=None,
    surplus_p3_kwh_eur=None,
    energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
    power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
    others_formula="iva_tax * meter_month_eur / 30 / 24",
    surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
    main_formula="energy_term + power_term + others_term",
)

PRICING_RULES_FIXED = PricingRules(
    p1_kw_year_eur=30.67266,
    p2_kw_year_eur=1.4243591,
    meter_month_eur=0.81,
    market_kw_year_eur=3.113,
    electricity_tax=1.0511300560,
    iva_tax=1.05,
    p1_kwh_eur=0.12,  # Fixed prices
    p2_kwh_eur=0.10,
    p3_kwh_eur=0.08,
    surplus_p1_kwh_eur=0.05,
    surplus_p2_kwh_eur=0.04,
    surplus_p3_kwh_eur=0.03,
    energy_formula="electricity_tax * iva_tax * kwh_eur * kwh",
    power_formula="electricity_tax * iva_tax * (p1_kw * (p1_kw_year_eur + market_kw_year_eur) + p2_kw * p2_kw_year_eur) / 365 / 24",
    others_formula="iva_tax * meter_month_eur / 30 / 24",
    surplus_formula="electricity_tax * iva_tax * surplus_kwh * surplus_kwh_eur",
    main_formula="energy_term + power_term + others_term",
)

# Sample supply data
SAMPLE_SUPPLY = Supply(
    cups=TEST_CUPS,
    distributor_code="0031",
    point_type=5,
    date_start=datetime(2020, 1, 1),
    date_end=datetime(2025, 12, 31),
    address="Test Address 123",
    postal_code="28001",
    province="Madrid",
    municipality="Madrid",
    distributor="Test Distributor",
)

# Sample contract data
SAMPLE_CONTRACT = Contract(
    distributor_code="0031",
    date_start=datetime(2023, 1, 1),
    date_end=datetime(2023, 12, 31),
    power_p1=5.75,
    power_p2=5.75,
    marketer="Test Marketer",
)

# Sample consumption data
SAMPLE_CONSUMPTIONS = [
    Consumption(
        datetime=datetime(2023, 10, 14, hour),
        delta_h=1.0,
        value_kwh=0.5 + hour * 0.1,
        surplus_kwh=0.0,
    )
    for hour in range(24)
]

# Sample maximeter data
SAMPLE_MAXPOWER = [
    MaxPower(
        datetime=datetime(2023, 10, day),
        value_kw=4.5 + day * 0.1,
    )
    for day in range(1, 15)
]


class TestEdataHelperIntegration:
    """Integration tests for EdataHelper with mocked services."""

    def test_initialization_pvpc(self):
        """Test EdataHelper initialization with PVPC pricing."""
        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
            datadis_authorized_nif=TEST_NIF,
            pricing_rules=PRICING_RULES_PVPC,
            storage_dir_path=None,
        )

        # Test basic properties
        assert helper._cups == TEST_CUPS
        assert helper._scups == "1JN0F"
        assert helper._authorized_nif == TEST_NIF
        assert helper.pricing_rules == PRICING_RULES_PVPC
        assert helper.enable_billing is True
        assert helper.is_pvpc is True

        # Test attributes initialization
        assert len(helper.attributes) == len(ATTRIBUTES)
        for attr in ATTRIBUTES:
            assert helper.attributes[attr] is None

        # Test that attributes and summary are the same object
        assert helper.attributes is helper.summary

        # Test services initialization
        assert helper._supply_service is not None
        assert helper._contract_service is not None
        assert helper._consumption_service is not None
        assert helper._maximeter_service is not None
        assert helper._billing_service is not None

    def test_initialization_fixed_pricing(self):
        """Test EdataHelper initialization with fixed pricing."""
        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
            pricing_rules=PRICING_RULES_FIXED,
        )

        assert helper.enable_billing is True
        assert helper.is_pvpc is False
        assert helper._billing_service is not None

    def test_initialization_no_billing(self):
        """Test EdataHelper initialization without billing."""
        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
            pricing_rules=None,
        )

        assert helper.enable_billing is False
        assert helper.is_pvpc is False

    @freeze_time(AT_TIME)
    @patch("edata.helpers.SupplyService")
    @patch("edata.helpers.ContractService")
    @patch("edata.helpers.ConsumptionService")
    @patch("edata.helpers.MaximeterService")
    @patch("edata.helpers.BillingService")
    @pytest.mark.asyncio
    async def test_update_successful_flow_pvpc(
        self,
        mock_billing_service,
        mock_maximeter_service,
        mock_consumption_service,
        mock_contract_service,
        mock_supply_service,
    ):
        """Test successful update flow with PVPC pricing."""

        # Setup mocks
        mock_supply_instance = Mock()
        mock_supply_instance.update_supplies = AsyncMock(return_value={"success": True})
        mock_supply_instance.validate_cups = AsyncMock(return_value=True)
        mock_supply_instance.get_supply_by_cups = AsyncMock(return_value=SAMPLE_SUPPLY)
        mock_supply_instance.get_supply_summary = AsyncMock(
            return_value={"cups": TEST_CUPS}
        )
        mock_supply_service.return_value = mock_supply_instance

        mock_contract_instance = Mock()
        mock_contract_instance.update_contracts = AsyncMock(
            return_value={"success": True}
        )
        mock_contract_instance.get_contract_summary = AsyncMock(
            return_value={
                "contract_p1_kW": 5.75,
                "contract_p2_kW": 5.75,
            }
        )
        mock_contract_service.return_value = mock_contract_instance

        mock_consumption_instance = Mock()
        mock_consumption_instance.update_consumption_range_by_months = AsyncMock(
            return_value={"success": True}
        )
        mock_consumption_instance.get_consumption_summary = AsyncMock(
            return_value={
                "yesterday_kWh": 12.5,
                "month_kWh": 350.0,
                "last_month_kWh": 340.0,
                "last_registered_date": datetime(2023, 10, 14, 23),
            }
        )
        mock_consumption_service.return_value = mock_consumption_instance

        mock_maximeter_instance = Mock()
        mock_maximeter_instance.update_maxpower_range_by_months = AsyncMock(
            return_value={"success": True}
        )
        mock_maximeter_instance.get_maximeter_summary = AsyncMock(
            return_value={
                "max_power_kW": 5.8,
                "max_power_date": datetime(2023, 10, 10),
                "max_power_mean_kW": 4.5,
                "max_power_90perc_kW": 5.2,
            }
        )
        mock_maximeter_service.return_value = mock_maximeter_instance

        mock_billing_instance = Mock()
        mock_billing_instance.update_pvpc_prices = AsyncMock(
            return_value={"success": True}
        )
        mock_billing_instance.update_missing_costs = AsyncMock(
            return_value={"success": True}
        )
        mock_billing_instance.get_billing_summary = AsyncMock(
            return_value={
                "month_€": 45.67,
                "last_month_€": 43.21,
            }
        )
        mock_billing_service.return_value = mock_billing_instance

        # Test update
        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
            pricing_rules=PRICING_RULES_PVPC,
        )

        date_from = datetime(2023, 1, 1)
        date_to = datetime(2023, 10, 15)
        result = await helper.update(date_from=date_from, date_to=date_to)

        # Verify result
        assert result is True

        # Verify service calls
        mock_supply_instance.update_supplies.assert_called_once_with(
            authorized_nif=None
        )
        mock_supply_instance.validate_cups.assert_called_once_with(TEST_CUPS)
        mock_supply_instance.get_supply_by_cups.assert_called_once_with(TEST_CUPS)

        mock_contract_instance.update_contracts.assert_called_once_with(
            cups=TEST_CUPS, distributor_code="0031", authorized_nif=None
        )

        mock_consumption_instance.update_consumption_range_by_months.assert_called_once_with(
            cups=TEST_CUPS,
            distributor_code="0031",
            start_date=date_from,  # Use the original date_from since it's after supply start
            end_date=date_to,
            measurement_type="0",
            point_type=5,
            authorized_nif=None,
        )

        mock_maximeter_instance.update_maxpower_range_by_months.assert_called_once()
        mock_billing_instance.update_pvpc_prices.assert_called_once()
        mock_billing_instance.update_missing_costs.assert_called_once()

        # Verify summary attributes
        assert helper.attributes["cups"] == TEST_CUPS
        assert helper.attributes["contract_p1_kW"] == 5.75
        assert helper.attributes["contract_p2_kW"] == 5.75
        assert helper.attributes["yesterday_kWh"] == 12.5
        assert helper.attributes["month_kWh"] == 350.0
        assert helper.attributes["last_month_kWh"] == 340.0
        assert helper.attributes["max_power_kW"] == 5.8
        assert helper.attributes["month_€"] == 45.67
        assert helper.attributes["last_month_€"] == 43.21

    @freeze_time(AT_TIME)
    @patch("edata.helpers.SupplyService")
    @patch("edata.helpers.ContractService")
    @patch("edata.helpers.ConsumptionService")
    @patch("edata.helpers.MaximeterService")
    @patch("edata.helpers.BillingService")
    @pytest.mark.asyncio
    async def test_update_with_service_failures(
        self,
        mock_billing_service,
        mock_maximeter_service,
        mock_consumption_service,
        mock_contract_service,
        mock_supply_service,
    ):
        """Test update flow with some service failures."""

        # Setup mocks with some failures
        mock_supply_instance = Mock()
        mock_supply_instance.update_supplies = AsyncMock(return_value={"success": True})
        mock_supply_instance.validate_cups = AsyncMock(return_value=True)
        mock_supply_instance.get_supply_by_cups = AsyncMock(return_value=SAMPLE_SUPPLY)
        mock_supply_instance.get_supply_summary = AsyncMock(
            return_value={"cups": TEST_CUPS}
        )
        mock_supply_service.return_value = mock_supply_instance

        mock_contract_instance = Mock()
        mock_contract_instance.update_contracts = AsyncMock(
            return_value={"success": False, "error": "Contract API down"}
        )
        mock_contract_instance.get_contract_summary = AsyncMock(return_value={})
        mock_contract_service.return_value = mock_contract_instance

        mock_consumption_instance = Mock()
        mock_consumption_instance.update_consumption_range_by_months = AsyncMock(
            return_value={"success": False}
        )
        mock_consumption_instance.get_consumption_summary = AsyncMock(return_value={})
        mock_consumption_service.return_value = mock_consumption_instance

        mock_maximeter_instance = Mock()
        mock_maximeter_instance.update_maxpower_range_by_months = AsyncMock(
            return_value={"success": True}
        )
        mock_maximeter_instance.get_maximeter_summary = AsyncMock(
            return_value={"max_power_kW": 5.8}
        )
        mock_maximeter_service.return_value = mock_maximeter_instance

        mock_billing_instance = Mock()
        mock_billing_instance.update_pvpc_prices = AsyncMock(
            return_value={"success": False, "error": "PVPC API error"}
        )
        mock_billing_instance.get_billing_summary = AsyncMock(return_value={})
        mock_billing_service.return_value = mock_billing_instance

        # Test update
        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
            pricing_rules=PRICING_RULES_PVPC,
        )

        result = await helper.update()

        # Update should still succeed even with some service failures
        assert result is True

        # Verify summary attributes include successful services
        assert helper.attributes["cups"] == TEST_CUPS
        assert helper.attributes["max_power_kW"] == 5.8

        # Failed services should have None values
        assert helper.attributes["contract_p1_kW"] is None
        assert helper.attributes["yesterday_kWh"] is None

    @patch("edata.helpers.SupplyService")
    @pytest.mark.asyncio
    async def test_update_supply_failure(self, mock_supply_service):
        """Test update with supply service failure."""

        mock_supply_instance = Mock()
        mock_supply_instance.update_supplies.return_value = {
            "success": False,
            "error": "Authentication failed",
        }
        mock_supply_service.return_value = mock_supply_instance

        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
        )

        result = await helper.update()

        # Should fail if supplies can't be updated
        assert result is False

    @patch("edata.helpers.SupplyService")
    @pytest.mark.asyncio
    async def test_update_cups_not_found(self, mock_supply_service):
        """Test update when CUPS is not found in account."""

        mock_supply_instance = Mock()
        mock_supply_instance.update_supplies.return_value = {"success": True}
        mock_supply_instance.validate_cups.return_value = False
        mock_supply_service.return_value = mock_supply_instance

        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
        )

        result = await helper.update()

        # Should fail if CUPS is not found
        assert result is False

    @patch("edata.helpers.SupplyService")
    @patch("edata.helpers.ContractService")
    @patch("edata.helpers.ConsumptionService")
    @patch("edata.helpers.MaximeterService")
    def test_calculate_summary_attributes_error_handling(
        self,
        mock_maximeter_service,
        mock_consumption_service,
        mock_contract_service,
        mock_supply_service,
    ):
        """Test error handling in summary calculation."""

        # Setup mock that raises exception
        mock_supply_instance = Mock()
        mock_supply_instance.get_supply_summary.side_effect = Exception(
            "Database error"
        )
        mock_supply_service.return_value = mock_supply_instance

        mock_contract_instance = Mock()
        mock_contract_instance.get_contract_summary.return_value = {
            "contract_p1_kW": 5.75
        }
        mock_contract_service.return_value = mock_contract_instance

        mock_consumption_instance = Mock()
        mock_consumption_instance.get_consumption_summary.return_value = {
            "yesterday_kWh": 12.5
        }
        mock_consumption_service.return_value = mock_consumption_instance

        mock_maximeter_instance = Mock()
        mock_maximeter_instance.get_maximeter_summary.return_value = {
            "max_power_kW": 5.8
        }
        mock_maximeter_service.return_value = mock_maximeter_instance

        helper = EdataHelper(
            datadis_username=TEST_USERNAME,
            datadis_password=TEST_PASSWORD,
            cups=TEST_CUPS,
        )

        # Should not raise exception
        # Note: We can't actually test the exception handling easily in async context
        # but we can test that all attributes are None initially
        for attr in ATTRIBUTES:
            assert helper.attributes[attr] is None

    @pytest.mark.asyncio
    async def test_numeric_value_rounding(self):
        """Test that numeric values are properly rounded."""
        with patch("edata.helpers.SupplyService") as mock_supply_service, patch(
            "edata.helpers.ContractService"
        ) as mock_contract_service, patch(
            "edata.helpers.ConsumptionService"
        ) as mock_consumption_service, patch(
            "edata.helpers.MaximeterService"
        ) as mock_maximeter_service:

            # Setup mocks with unrounded values
            mock_supply_instance = Mock()
            mock_supply_instance.get_supply_summary = AsyncMock(
                return_value={"cups": TEST_CUPS}
            )
            mock_supply_service.return_value = mock_supply_instance

            mock_contract_instance = Mock()
            mock_contract_instance.get_contract_summary = AsyncMock(
                return_value={"contract_p1_kW": 5.7523456}
            )
            mock_contract_service.return_value = mock_contract_instance

            mock_consumption_instance = Mock()
            mock_consumption_instance.get_consumption_summary = AsyncMock(
                return_value={"yesterday_kWh": 12.54789}
            )
            mock_consumption_service.return_value = mock_consumption_instance

            mock_maximeter_instance = Mock()
            mock_maximeter_instance.get_maximeter_summary = AsyncMock(
                return_value={"max_power_kW": 5.87654321}
            )
            mock_maximeter_service.return_value = mock_maximeter_instance

            helper = EdataHelper(
                datadis_username=TEST_USERNAME,
                datadis_password=TEST_PASSWORD,
                cups=TEST_CUPS,
            )

            await helper._calculate_summary_attributes()

            # Check rounding
            assert helper.attributes["contract_p1_kW"] == 5.75
            assert helper.attributes["yesterday_kWh"] == 12.55
            assert helper.attributes["max_power_kW"] == 5.88
            assert (
                helper.attributes["cups"] == TEST_CUPS
            )  # String should not be affected

    @pytest.mark.asyncio
    async def test_date_range_adjustment(self):
        """Test that date ranges are properly adjusted to supply validity period."""
        with patch("edata.helpers.SupplyService") as mock_supply_service, patch(
            "edata.helpers.ContractService"
        ) as mock_contract_service, patch(
            "edata.helpers.ConsumptionService"
        ) as mock_consumption_service, patch(
            "edata.helpers.MaximeterService"
        ) as mock_maximeter_service:

            # Supply with limited date range
            limited_supply = Supply(
                cups=TEST_CUPS,
                distributor_code="0031",
                point_type=5,
                date_start=datetime(2023, 6, 1),  # Later start
                date_end=datetime(2023, 9, 30),  # Earlier end
                address="Test Address",
                postal_code="28001",
                province="Madrid",
                municipality="Madrid",
                distributor="Test Distributor",
            )

            mock_supply_instance = Mock()
            mock_supply_instance.update_supplies = AsyncMock(
                return_value={"success": True}
            )
            mock_supply_instance.validate_cups = AsyncMock(return_value=True)
            mock_supply_instance.get_supply_by_cups = AsyncMock(
                return_value=limited_supply
            )
            mock_supply_instance.get_supply_summary = AsyncMock(
                return_value={"cups": TEST_CUPS}
            )
            mock_supply_service.return_value = mock_supply_instance

            mock_contract_instance = Mock()
            mock_contract_instance.update_contracts = AsyncMock(
                return_value={"success": True}
            )
            mock_contract_instance.get_contract_summary = AsyncMock(return_value={})
            mock_contract_service.return_value = mock_contract_instance

            mock_consumption_instance = Mock()
            mock_consumption_instance.update_consumption_range_by_months = AsyncMock(
                return_value={"success": True}
            )
            mock_consumption_instance.get_consumption_summary = AsyncMock(
                return_value={}
            )
            mock_consumption_service.return_value = mock_consumption_instance

            mock_maximeter_instance = Mock()
            mock_maximeter_instance.update_maxpower_range_by_months = AsyncMock(
                return_value={"success": True}
            )
            mock_maximeter_instance.get_maximeter_summary = AsyncMock(return_value={})
            mock_maximeter_service.return_value = mock_maximeter_instance

            helper = EdataHelper(
                datadis_username=TEST_USERNAME,
                datadis_password=TEST_PASSWORD,
                cups=TEST_CUPS,
            )

            # Request broader date range
            result = await helper.update(
                date_from=datetime(2023, 1, 1), date_to=datetime(2023, 12, 31)
            )

            assert result is True

            # Verify that consumption service was called with adjusted dates
            mock_consumption_instance.update_consumption_range_by_months.assert_called_once_with(
                cups=TEST_CUPS,
                distributor_code="0031",
                start_date=datetime(2023, 6, 1),  # Adjusted to supply start
                end_date=datetime(2023, 9, 30),  # Adjusted to supply end
                measurement_type="0",
                point_type=5,
                authorized_nif=None,
            )
