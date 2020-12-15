from datetime import datetime
from typing import Union

import pytz
from tzlocal import get_localzone


def datetime_to_api_timestamp(dt: datetime):
    tz = get_localzone()
    local_dt = tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    timestamp_str = utc_dt.strftime("%Y-%m-%dT%H:%M:%S")

    api_dt = {"dateTime": timestamp_str, "timeZone": "UTC"}

    return api_dt


def api_timestamp_to_datetime(api_dt: Union[str, dict]):
    """Convertes the datetime string returned by the API to python datetime object"""

    """
    Somehow this string is formatted with 7 digits for 'microsecond' resolution, so crop the last digit (and trailing Z)
    The cropped string will be written into api_dt_str_mod 
    """
    api_dt_str_mod = None

    if isinstance(api_dt, str):
        api_dt_str_mod = api_dt[:-2]
    elif isinstance(api_dt, dict):
        api_dt_str_mod = api_dt["dateTime"][:-2]
    else:
        raise

    dt = datetime.strptime(api_dt_str_mod, "%Y-%m-%dT%H:%M:%S.%f")
    dt = pytz.utc.localize(dt)

    return dt
