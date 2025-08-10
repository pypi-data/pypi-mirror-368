"""Tests for REData (online)"""

from datetime import datetime, timedelta

import pytest

from edata.connectors.redata import REDataConnector


@pytest.mark.asyncio
async def test_get_realtime_prices():
    """Test a successful 'get_realtime_prices' query"""
    connector = REDataConnector()
    yesterday = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
    response = await connector.get_realtime_prices(
        yesterday, yesterday + timedelta(days=1) - timedelta(minutes=1), False
    )
    assert len(response) == 24


@pytest.mark.asyncio
async def test_async_get_realtime_prices():
    """Test a successful 'get_realtime_prices' query (legacy test name)"""
    connector = REDataConnector()
    yesterday = datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
    response = await connector.get_realtime_prices(
        yesterday, yesterday + timedelta(days=1) - timedelta(minutes=1), False
    )
    assert len(response) == 24
