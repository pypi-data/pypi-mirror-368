"""Utility functions for edata package."""

import contextlib
import json
import logging
import math
from copy import deepcopy
from datetime import date, datetime, timedelta
from json import JSONEncoder
from typing import Any, Dict, List, Optional

import holidays

_LOGGER = logging.getLogger(__name__)

# PVPC tariff constants
HOURS_P1 = [10, 11, 12, 13, 18, 19, 20, 21]
HOURS_P2 = [8, 9, 14, 15, 16, 17, 22, 23]
WEEKDAYS_P3 = [5, 6]


def get_pvpc_tariff(a_datetime: datetime) -> str:
    """Evaluate the PVPC tariff for a given datetime.

    Args:
        a_datetime: The datetime to evaluate

    Returns:
        The tariff period: "p1", "p2", or "p3"
    """
    hdays = holidays.country_holidays("ES")
    hour = a_datetime.hour
    weekday = a_datetime.weekday()

    if weekday in WEEKDAYS_P3 or a_datetime.date() in hdays:
        return "p3"
    elif hour in HOURS_P1:
        return "p1"
    elif hour in HOURS_P2:
        return "p2"
    else:
        return "p3"


def extend_by_key(
    old_lst: List[Dict[str, Any]], new_lst: List[Dict[str, Any]], key: str
) -> List[Dict[str, Any]]:
    """Extend a list of dicts by key."""
    lst = deepcopy(old_lst)
    temp_list = []
    for new_element in new_lst:
        for old_element in lst:
            if new_element[key] == old_element[key]:
                for i in old_element:
                    old_element[i] = new_element[i]
                break
        else:
            temp_list.append(new_element)
    lst.extend(temp_list)
    return lst


def extract_dt_ranges(
    lst: List[Dict[str, Any]],
    dt_from: datetime,
    dt_to: datetime,
    gap_interval: timedelta = timedelta(hours=1),
) -> tuple:
    """Filter a list of dicts between two datetimes."""
    new_lst = []
    missing = []
    oldest_dt = None
    newest_dt = None
    last_dt = None
    if len(lst) > 0:
        sorted_lst = sorted(lst, key=lambda i: i["datetime"])
        last_dt = dt_from
        for i in sorted_lst:
            if dt_from <= i["datetime"] <= dt_to:
                if (i["datetime"] - last_dt) > gap_interval:
                    missing.append({"from": last_dt, "to": i["datetime"]})
                if i.get("value_kWh", 1) > 0:
                    if oldest_dt is None or i["datetime"] < oldest_dt:
                        oldest_dt = i["datetime"]
                    if newest_dt is None or i["datetime"] > newest_dt:
                        newest_dt = i["datetime"]
                if i["datetime"] != last_dt:  # remove duplicates
                    new_lst.append(i)
                    last_dt = i["datetime"]
        if dt_to > last_dt:
            missing.append({"from": last_dt, "to": dt_to})
        _LOGGER.debug("found data from %s to %s", oldest_dt, newest_dt)
    else:
        missing.append({"from": dt_from, "to": dt_to})
    return new_lst, missing


def get_by_key(
    lst: List[Dict[str, Any]], key: str, value: Any
) -> Optional[Dict[str, Any]]:
    """Obtain an element of a list of dicts by key=value."""
    for i in lst:
        if i[key] == value:
            return i
    return None


def serialize_dict(data: dict) -> dict:
    """Serialize dicts as json."""

    class DateTimeEncoder(JSONEncoder):
        """Replace datetime objects with ISO strings."""

        def default(self, o):
            if isinstance(o, (date, datetime)):
                return o.isoformat()

    return json.loads(json.dumps(data, cls=DateTimeEncoder))


def deserialize_dict(serialized_dict: dict) -> dict:
    """Deserializes a json replacing ISOTIME strings into datetime."""

    def datetime_parser(json_dict):
        """Parse JSON while converting ISO strings into datetime objects."""
        for key, value in json_dict.items():
            if "date" in key:
                with contextlib.suppress(Exception):
                    json_dict[key] = datetime.fromisoformat(value)
        return json_dict

    return json.loads(json.dumps(serialized_dict), object_hook=datetime_parser)


def percentile(N: List, percent: float, key=lambda x: x):
    """Find the percentile of a list of values."""
    if not N:
        return None
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c - k)
    d1 = key(N[int(c)]) * (k - f)
    return d0 + d1


def extend_and_filter(
    old_lst: List[Dict[str, Any]],
    new_lst: List[Dict[str, Any]],
    key: str,
    dt_from: datetime,
    dt_to: datetime,
) -> List[Dict[str, Any]]:
    """Extend and filter data by datetime range."""
    data = extend_by_key(old_lst, new_lst, key)
    data, _ = extract_dt_ranges(
        data,
        dt_from,
        dt_to,
        gap_interval=timedelta(days=365),  # trick
    )
    return data
