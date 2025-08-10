"""A REData API connector"""

import asyncio
import datetime as dt
import logging

import aiohttp
from dateutil import parser

from edata.models.pricing import PricingData

_LOGGER = logging.getLogger(__name__)

REQUESTS_TIMEOUT = 15

URL_REALTIME_PRICES = (
    "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
    "?time_trunc=hour"
    "&geo_ids={geo_id}"
    "&start_date={start:%Y-%m-%dT%H:%M}&end_date={end:%Y-%m-%dT%H:%M}"
)


class REDataConnector:
    """Main class for REData connector"""

    def __init__(
        self,
    ) -> None:
        """Init method for REDataConnector"""

    async def get_realtime_prices(
        self, dt_from: dt.datetime, dt_to: dt.datetime, is_ceuta_melilla: bool = False
    ) -> list:
        """GET query to fetch realtime pvpc prices, historical data is limited to current month (async version)"""
        url = URL_REALTIME_PRICES.format(
            geo_id=8744 if is_ceuta_melilla else 8741,
            start=dt_from,
            end=dt_to,
        )
        data = []

        timeout = aiohttp.ClientTimeout(total=REQUESTS_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        res_json = await response.json()
                        if res_json:
                            try:
                                res_list = res_json["included"][0]["attributes"][
                                    "values"
                                ]
                            except (IndexError, KeyError):
                                _LOGGER.error(
                                    "%s returned a malformed response: %s ",
                                    url,
                                    await response.text(),
                                )
                                return data

                            for element in res_list:
                                data.append(
                                    PricingData(
                                        datetime=parser.parse(
                                            element["datetime"]
                                        ).replace(tzinfo=None),
                                        value_eur_kwh=element["value"] / 1000,
                                        delta_h=1,
                                    )
                                )
                    else:
                        _LOGGER.error(
                            "%s returned %s with code %s",
                            url,
                            await response.text(),
                            response.status,
                        )
            except asyncio.TimeoutError:
                _LOGGER.error("Timeout error when fetching data from %s", url)
            except aiohttp.ClientError as e:
                _LOGGER.error(
                    "HTTP client error when fetching data from %s: %s", url, e
                )
            except Exception as e:
                _LOGGER.error("Unexpected error when fetching data from %s: %s", url, e)

        return data
