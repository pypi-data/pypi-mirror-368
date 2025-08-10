"""Datadis API connector.

To fetch data from datadis.es private API.
There a few issues that are workarounded:
 - You have to wait 24h between two identical requests.
 - Datadis server does not like ranges greater than 1 month.
"""

import asyncio
import hashlib
import logging
import os
import tempfile
from datetime import datetime, timedelta

import aiohttp
import diskcache
from dateutil.relativedelta import relativedelta

from edata import utils
from edata.models import Consumption, Contract, MaxPower, Supply

_LOGGER = logging.getLogger(__name__)

# Request timeout constant
REQUESTS_TIMEOUT = 30

# Token-related constants
URL_TOKEN = "https://datadis.es/nikola-auth/tokens/login"
TOKEN_USERNAME = "username"
TOKEN_PASSWD = "password"

# Supplies-related constants
URL_GET_SUPPLIES = "https://datadis.es/api-private/api/get-supplies"
GET_SUPPLIES_MANDATORY_FIELDS = [
    "cups",
    "validDateFrom",
    "validDateTo",
    "pointType",
    "distributorCode",
]

# Contracts-related constants
URL_GET_CONTRACT_DETAIL = "https://datadis.es/api-private/api/get-contract-detail"
GET_CONTRACT_DETAIL_MANDATORY_FIELDS = [
    "startDate",
    "endDate",
    "marketer",
    "contractedPowerkW",
]

# Consumption-related constants
URL_GET_CONSUMPTION_DATA = "https://datadis.es/api-private/api/get-consumption-data"
GET_CONSUMPTION_DATA_MANDATORY_FIELDS = [
    "time",
    "date",
    "consumptionKWh",
    "obtainMethod",
]
MAX_CONSUMPTIONS_MONTHS = (
    1  # max consumptions in a single request (fixed to 1 due to datadis limitations)
)

# Maximeter-related constants
URL_GET_MAX_POWER = "https://datadis.es/api-private/api/get-max-power"
GET_MAX_POWER_MANDATORY_FIELDS = ["time", "date", "maxPower"]

# Timing constants
TIMEOUT = 3 * 60  # requests timeout
QUERY_LIMIT = timedelta(hours=24)  # a datadis limitation, again...

# Cache-related constants
RECENT_CACHE_SUBDIR = "cache"


class DatadisConnector:
    """A Datadis private API connector."""

    def __init__(
        self,
        username: str,
        password: str,
        enable_smart_fetch: bool = True,
        storage_path: str | None = None,
    ) -> None:
        """DatadisConnector constructor."""

        # initialize some things
        self._usr = username
        self._pwd = password
        self._token = {}
        self._smart_fetch = enable_smart_fetch
        self._warned_queries = []
        if storage_path is not None:
            self._recent_cache_dir = os.path.join(storage_path, RECENT_CACHE_SUBDIR)
        else:
            self._recent_cache_dir = os.path.join(
                tempfile.gettempdir(), RECENT_CACHE_SUBDIR
            )

        os.makedirs(self._recent_cache_dir, exist_ok=True)

        # Initialize diskcache for persistent caching
        self._cache = diskcache.Cache(
            self._recent_cache_dir,
            size_limit=100 * 1024 * 1024,  # 100MB limit
            eviction_policy="least-recently-used",
        )

    async def login(self):
        """Test to login with provided credentials."""
        return await self._get_token()

    async def get_supplies(self, authorized_nif: str | None = None) -> list[Supply]:
        """Datadis 'get_supplies' query (async version)."""

        data = {}

        # If authorized_nif is provided, we have to include it as parameter
        if authorized_nif is not None:
            data["authorizedNif"] = authorized_nif

        # Request the resource using get method
        response = await self._get(
            URL_GET_SUPPLIES, request_data=data, ignore_recent_queries=True
        )

        # Response is a list of serialized supplies.
        # We will iter through them to transform them into Supply objects
        supplies = []
        # Build tomorrow Y/m/d string since we will use it as the 'date_end' of
        # active supplies
        tomorrow_str = (datetime.today() + timedelta(days=1)).strftime("%Y/%m/%d")
        for i in response:
            # check data integrity (maybe this can be supressed if datadis proves to be reliable)
            if all(k in i for k in GET_SUPPLIES_MANDATORY_FIELDS):
                supplies.append(
                    Supply(
                        cups=i["cups"],  # the supply identifier
                        date_start=datetime.strptime(
                            (
                                i["validDateFrom"]
                                if i["validDateFrom"] != ""
                                else "1970/01/01"
                            ),
                            "%Y/%m/%d",
                        ),  # start date of the supply. 1970/01/01 if unset.
                        date_end=datetime.strptime(
                            (
                                i["validDateTo"]
                                if i["validDateTo"] != ""
                                else tomorrow_str
                            ),
                            "%Y/%m/%d",
                        ),  # end date of the supply, tomorrow if unset
                        # the following parameters are not crucial, so they can be none
                        address=i.get("address", None),
                        postal_code=i.get("postalCode", None),
                        province=i.get("province", None),
                        municipality=i.get("municipality", None),
                        distributor=i.get("distributor", None),
                        # these two are mandatory, we will use them to fetch contracts data
                        point_type=i["pointType"],
                        distributor_code=i["distributorCode"],
                    )
                )
            else:
                _LOGGER.warning(
                    "Weird data structure while fetching supplies data, got %s",
                    response,
                )
        return supplies

    async def _get(
        self,
        url: str,
        request_data: dict | None = None,
        refresh_token: bool = False,
        is_retry: bool = False,
        ignore_recent_queries: bool = False,
    ):
        """Get request for Datadis API (async version)."""

        if request_data is None:
            data = {}
        else:
            data = request_data

        # build get parameters
        params = "?" if len(data) > 0 else ""
        for param in data:
            key = param
            value = data[param]
            params = params + f"{key}={value}&"
        anonym_params = "?" if len(data) > 0 else ""

        # build anonymized params for logging
        for anonym_param in data:
            key = anonym_param
            if key == "cups":
                value = "xxxx" + data[anonym_param][-5:]
            elif key == "authorizedNif":
                value = "xxxx"
            else:
                value = data[anonym_param]
            anonym_params = anonym_params + f"{key}={value}&"

        # Check diskcache first (unless ignoring cache)
        if not ignore_recent_queries:
            cache_data = {
                "url": url,
                "request_data": request_data,
                "refresh_token": refresh_token,
                "is_retry": is_retry,
            }
            cache_key = hashlib.sha256(str(cache_data).encode()).hexdigest()

            try:
                # Run cache get operation in thread to avoid blocking
                cached_result = await asyncio.to_thread(self._cache.get, cache_key)
                if cached_result is not None and isinstance(
                    cached_result, (list, dict)
                ):
                    _LOGGER.info(
                        "Returning cached response for '%s'", url + anonym_params
                    )
                    return cached_result
            except Exception as e:
                _LOGGER.warning("Error reading cache: %s", e)

        # refresh token if needed (recursive approach)
        is_valid_token = False
        response = []
        if refresh_token:
            is_valid_token = await self._get_token()
        if is_valid_token or not refresh_token:

            # run the query
            timeout = aiohttp.ClientTimeout(total=REQUESTS_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    _LOGGER.info("GET %s", url + anonym_params)
                    headers = {"Accept-Encoding": "identity"}

                    # Ensure we have a token
                    if not self._token.get("encoded"):
                        await self._get_token()

                    headers["Authorization"] = f"Bearer {self._token['encoded']}"

                    async with session.get(url + params, headers=headers) as reply:
                        # eval response
                        if reply.status == 200:
                            # we're here if reply seems valid
                            _LOGGER.info("Got 200 OK")
                            try:
                                response_json = await reply.json(content_type=None)
                                if response_json:
                                    response = response_json
                                    # Store in diskcache with 24h TTL
                                    if not ignore_recent_queries and isinstance(
                                        response, (list, dict)
                                    ):
                                        try:
                                            cache_data = {
                                                "url": url,
                                                "request_data": request_data,
                                                "refresh_token": refresh_token,
                                                "is_retry": is_retry,
                                            }
                                            cache_key = hashlib.sha256(
                                                str(cache_data).encode()
                                            ).hexdigest()
                                            ttl_seconds = int(
                                                QUERY_LIMIT.total_seconds()
                                            )

                                            # Run cache set operation in thread to avoid blocking
                                            await asyncio.to_thread(
                                                self._cache.set,
                                                cache_key,
                                                response,
                                                expire=ttl_seconds,
                                            )
                                            _LOGGER.info(
                                                "Cached response for %s with TTL %d seconds",
                                                url,
                                                ttl_seconds,
                                            )
                                        except Exception as e:
                                            _LOGGER.warning(
                                                "Error storing in cache: %s", e
                                            )
                                else:
                                    # this mostly happens when datadis provides an empty response
                                    _LOGGER.info("Got an empty response")
                            except Exception as e:
                                # Handle non-JSON responses
                                _LOGGER.info("Got an empty or non-JSON response")
                                _LOGGER.exception(e)
                        elif reply.status == 401 and not refresh_token:
                            # we're here if we were unauthorized so we will refresh the token
                            response = await self._get(
                                url,
                                request_data=data,
                                refresh_token=True,
                                ignore_recent_queries=ignore_recent_queries,
                            )
                        elif reply.status == 429:
                            # we're here if we exceeded datadis API rates (24h)
                            _LOGGER.warning(
                                "Got status code '%s' with message '%s'",
                                reply.status,
                                await reply.text(),
                            )
                        elif is_retry:
                            # otherwise, if this was a retried request... warn the user
                            if (url + params) not in self._warned_queries:
                                _LOGGER.warning(
                                    "Got status code '%s' with message '%s'. %s. %s",
                                    reply.status,
                                    await reply.text(),
                                    "Query temporary disabled",
                                    "Future 500 code errors for this query will be silenced until restart",
                                )
                            self._warned_queries.append(url + params)
                        else:
                            # finally, retry since an unexpected error took place (mostly 500 errors - server fault)
                            response = await self._get(
                                url,
                                request_data,
                                is_retry=True,
                                ignore_recent_queries=ignore_recent_queries,
                            )
                except asyncio.TimeoutError:
                    _LOGGER.warning("Timeout at %s", url + anonym_params)
                    return []
                except Exception as e:
                    _LOGGER.error(
                        "Error during async request to %s: %s", url + anonym_params, e
                    )
                    return []

        return response

    async def get_contract_detail(
        self, cups: str, distributor_code: str, authorized_nif: str | None = None
    ) -> list[Contract]:
        """Datadis get_contract_detail query (async version)."""
        data = {"cups": cups, "distributorCode": distributor_code}
        if authorized_nif is not None:
            data["authorizedNif"] = authorized_nif
        response = await self._get(
            URL_GET_CONTRACT_DETAIL, request_data=data, ignore_recent_queries=True
        )
        contracts = []
        tomorrow_str = (datetime.today() + timedelta(days=1)).strftime("%Y/%m/%d")
        for i in response:
            if all(k in i for k in GET_CONTRACT_DETAIL_MANDATORY_FIELDS):
                contracts.append(
                    Contract(
                        date_start=datetime.strptime(
                            i["startDate"] if i["startDate"] != "" else "1970/01/01",
                            "%Y/%m/%d",
                        ),
                        date_end=datetime.strptime(
                            i["endDate"] if i["endDate"] != "" else tomorrow_str,
                            "%Y/%m/%d",
                        ),
                        marketer=i["marketer"],
                        distributor_code=distributor_code,
                        power_p1=(
                            i["contractedPowerkW"][0]
                            if isinstance(i["contractedPowerkW"], list)
                            else None
                        ),
                        power_p2=(
                            i["contractedPowerkW"][1]
                            if (len(i["contractedPowerkW"]) > 1)
                            else None
                        ),
                    )
                )
            else:
                _LOGGER.warning(
                    "Weird data structure while fetching contracts data, got %s",
                    response,
                )
        return contracts

    async def get_consumption_data(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        measurement_type: str,
        point_type: int,
        authorized_nif: str | None = None,
        is_smart_fetch: bool = False,
    ) -> list[Consumption]:
        """Datadis get_consumption_data query (async version)."""

        if self._smart_fetch and not is_smart_fetch:
            _start = start_date
            consumptions_dicts = []
            while _start < end_date:
                _end = min(
                    _start + relativedelta(months=MAX_CONSUMPTIONS_MONTHS), end_date
                )
                batch_consumptions = await self.get_consumption_data(
                    cups,
                    distributor_code,
                    _start,
                    _end,
                    measurement_type,
                    point_type,
                    authorized_nif,
                    is_smart_fetch=True,
                )
                # Convert to dicts for extend_by_key function
                batch_dicts = [c.model_dump() for c in batch_consumptions]
                consumptions_dicts = utils.extend_by_key(
                    consumptions_dicts,
                    batch_dicts,
                    "datetime",
                )
                _start = _end
            # Convert back to Pydantic models
            return [Consumption(**c) for c in consumptions_dicts]

        data = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": datetime.strftime(start_date, "%Y/%m"),
            "endDate": datetime.strftime(end_date, "%Y/%m"),
            "measurementType": measurement_type,
            "pointType": point_type,
        }
        if authorized_nif is not None:
            data["authorizedNif"] = authorized_nif

        response = await self._get(URL_GET_CONSUMPTION_DATA, request_data=data)

        consumptions = []
        for i in response:
            if "consumptionKWh" in i:
                if all(k in i for k in GET_CONSUMPTION_DATA_MANDATORY_FIELDS):
                    hour = str(int(i["time"].split(":")[0]) - 1)
                    date_as_dt = datetime.strptime(
                        f"{i['date']} {hour.zfill(2)}:00", "%Y/%m/%d %H:%M"
                    )
                    if not (start_date <= date_as_dt <= end_date):
                        continue  # skip element if dt is out of range
                    _surplus = i.get("surplusEnergyKWh", 0)
                    if _surplus is None:
                        _surplus = 0
                    consumptions.append(
                        Consumption(
                            datetime=date_as_dt,
                            delta_h=1,
                            value_kwh=i["consumptionKWh"],
                            surplus_kwh=_surplus,
                            real=i["obtainMethod"] == "Real",
                        )
                    )
                else:
                    _LOGGER.warning(
                        "Weird data structure while fetching consumption data, got %s",
                        response,
                    )
        return consumptions

    async def get_max_power(
        self,
        cups: str,
        distributor_code: str,
        start_date: datetime,
        end_date: datetime,
        authorized_nif: str | None = None,
    ) -> list[MaxPower]:
        """Datadis get_max_power query (async version)."""

        data = {
            "cups": cups,
            "distributorCode": distributor_code,
            "startDate": datetime.strftime(start_date, "%Y/%m"),
            "endDate": datetime.strftime(end_date, "%Y/%m"),
        }
        if authorized_nif is not None:
            data["authorizedNif"] = authorized_nif
        response = await self._get(URL_GET_MAX_POWER, request_data=data)
        maxpower_values = []
        for i in response:
            if all(k in i for k in GET_MAX_POWER_MANDATORY_FIELDS):
                maxpower_values.append(
                    MaxPower(
                        datetime=datetime.strptime(
                            f"{i['date']} {i['time']}", "%Y/%m/%d %H:%M"
                        ),
                        value_kw=i["maxPower"],
                    )
                )
            else:
                _LOGGER.warning(
                    "Weird data structure while fetching maximeter data, got %s",
                    response,
                )
        return maxpower_values

    async def _get_token(self):
        """Private method that fetches a new token if needed (async version)."""

        _LOGGER.info("Fetching token for async requests")
        is_valid_token = False

        timeout = aiohttp.ClientTimeout(total=REQUESTS_TIMEOUT)

        # Prepare data as URL-encoded string, same as sync version
        form_data = {
            TOKEN_USERNAME: self._usr,
            TOKEN_PASSWD: self._pwd,
        }

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.post(
                    URL_TOKEN,
                    data=form_data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ) as response:
                    if response.status == 200:
                        # store token encoded
                        self._token["encoded"] = await response.text()
                        is_valid_token = True
                    else:
                        _LOGGER.error(
                            "Unknown error while retrieving async token, got %s",
                            await response.text(),
                        )
            except Exception as e:
                _LOGGER.error("Error during async token fetch: %s", e)

        return is_valid_token
