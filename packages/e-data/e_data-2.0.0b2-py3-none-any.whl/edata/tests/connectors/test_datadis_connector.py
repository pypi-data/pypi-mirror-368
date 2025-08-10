"""Datadis connector module testing."""

import datetime
from unittest.mock import AsyncMock, patch

import pytest

from edata.connectors.datadis import DatadisConnector

MOCK_USERNAME = "fake_user"
MOCK_PASSWORD = "fake_password"

SUPPLIES_RESPONSE = [
    {
        "cups": "ESXXXXXXXXXXXXXXXXTEST",
        "validDateFrom": "2022/01/01",
        "validDateTo": "",
        "pointType": 5,
        "distributorCode": "2",
        "address": "fake address, fake 12345",
        "postalCode": "12345",
        "province": "FAKE PROVINCE",
        "municipality": "FAKE MUNICIPALITY",
        "distributor": "FAKE DISTRIBUTOR",
    }
]

SUPPLIES_EXPECTATIONS = [
    {
        "cups": "ESXXXXXXXXXXXXXXXXTEST",
        "date_start": datetime.datetime(2022, 1, 1, 0, 0),
        "date_end": datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        + datetime.timedelta(days=1),
        "point_type": 5,
        "distributor_code": "2",
        "address": "fake address, fake 12345",
        "postal_code": "12345",
        "province": "FAKE PROVINCE",
        "municipality": "FAKE MUNICIPALITY",
        "distributor": "FAKE DISTRIBUTOR",
    }
]

CONTRACTS_RESPONSE = [
    {
        "startDate": "2022/10/22",
        "endDate": "2022/10/22",
        "marketer": "fake_marketer",
        "contractedPowerkW": [1.5, 1.5],
    }
]

CONTRACTS_EXPECTATIONS = [
    {
        "date_start": datetime.datetime(2022, 10, 22, 0, 0),
        "date_end": datetime.datetime(2022, 10, 22, 0, 0),
        "marketer": "fake_marketer",
        "distributor_code": "2",
        "power_p1": 1.5,
        "power_p2": 1.5,
    }
]

CONSUMPTIONS_RESPONSE = [
    {
        "cups": "ESXXXXXXXXXXXXXXXXTEST",
        "date": "2022/10/22",
        "time": "01:00",
        "consumptionKWh": 1.0,
        "obtainMethod": "Real",
    },
    {
        "cups": "ESXXXXXXXXXXXXXXXXTEST",
        "date": "2022/10/22",
        "time": "02:00",
        "consumptionKWh": 1.0,
        "obtainMethod": "Real",
    },
]

CONSUMPTIONS_EXPECTATIONS = [
    {
        "datetime": datetime.datetime(2022, 10, 22, 0, 0),
        "delta_h": 1,
        "value_kwh": 1.0,
        "surplus_kwh": 0,
        "real": True,
    },
    {
        "datetime": datetime.datetime(2022, 10, 22, 1, 0),
        "delta_h": 1,
        "value_kwh": 1.0,
        "surplus_kwh": 0,
        "real": True,
    },
]

MAXIMETER_RESPONSE = [
    {
        "cups": "ESXXXXXXXXXXXXXXXXTEST",
        "date": "2022/03/01",
        "time": "12:00",
        "maxPower": 1.0,
    }
]

MAXIMETER_EXPECTATIONS = [
    {
        "datetime": datetime.datetime(2022, 3, 1, 12, 0),
        "value_kw": 1.0,
    }
]


# Tests for async methods (now the only methods available)


@pytest.mark.asyncio
@patch.object(DatadisConnector, "_get_token", AsyncMock(return_value=True))
@patch.object(DatadisConnector, "_get", AsyncMock(return_value=SUPPLIES_RESPONSE))
async def test_get_supplies():
    """Test a successful 'get_supplies' query."""
    connector = DatadisConnector(MOCK_USERNAME, MOCK_PASSWORD)
    result = await connector.get_supplies()
    # Note: Now returns Pydantic models instead of dicts
    # Convert to dicts for comparison with expectations
    result_dicts = [supply.model_dump() for supply in result]
    assert result_dicts == SUPPLIES_EXPECTATIONS


@pytest.mark.asyncio
@patch.object(DatadisConnector, "_get_token", AsyncMock(return_value=True))
@patch.object(DatadisConnector, "_get", AsyncMock(return_value=CONTRACTS_RESPONSE))
async def test_get_contract_detail():
    """Test a successful 'get_contract_detail' query."""
    connector = DatadisConnector(MOCK_USERNAME, MOCK_PASSWORD)
    result = await connector.get_contract_detail("ESXXXXXXXXXXXXXXXXTEST", "2")
    # Note: Now returns Pydantic models instead of dicts
    result_dicts = [contract.model_dump() for contract in result]
    assert result_dicts == CONTRACTS_EXPECTATIONS


@pytest.mark.asyncio
@patch.object(DatadisConnector, "_get_token", AsyncMock(return_value=True))
@patch.object(DatadisConnector, "_get", AsyncMock(return_value=CONSUMPTIONS_RESPONSE))
async def test_get_consumption_data():
    """Test a successful 'get_consumption_data' query."""
    connector = DatadisConnector(MOCK_USERNAME, MOCK_PASSWORD)
    result = await connector.get_consumption_data(
        "ESXXXXXXXXXXXXXXXXTEST",
        "2",
        datetime.datetime(2022, 10, 22, 0, 0, 0),
        datetime.datetime(2022, 10, 22, 2, 0, 0),
        "0",  # measurement_type as string
        5,
    )
    # Note: Now returns Pydantic models instead of dicts
    result_dicts = [consumption.model_dump() for consumption in result]
    assert result_dicts == CONSUMPTIONS_EXPECTATIONS


@pytest.mark.asyncio
@patch.object(DatadisConnector, "_get_token", AsyncMock(return_value=True))
@patch.object(DatadisConnector, "_get", AsyncMock(return_value=MAXIMETER_RESPONSE))
async def test_get_max_power():
    """Test a successful 'get_max_power' query."""
    connector = DatadisConnector(MOCK_USERNAME, MOCK_PASSWORD)
    result = await connector.get_max_power(
        "ESXXXXXXXXXXXXXXXXTEST",
        "2",
        datetime.datetime(2022, 3, 1, 0, 0, 0),
        datetime.datetime(2022, 4, 1, 0, 0, 0),
    )
    # Note: Now returns Pydantic models instead of dicts
    result_dicts = [maxpower.model_dump() for maxpower in result]
    assert result_dicts == MAXIMETER_EXPECTATIONS
