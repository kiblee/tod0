from datetime import datetime
import pytz
from tzlocal import get_localzone


def datetime_to_api_timestamp(dt: datetime):
    tz = get_localzone()
    local_dt = tz.localize(dt, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    timestamp_str = utc_dt.strftime("%Y-%m-%dT%H:%M:%S")

    api_dt = {"dateTime": timestamp_str, "timeZone": "UTC"}

    return api_dt
