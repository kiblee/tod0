from datetime import datetime


def datetimeToApiTimestamp(dt: datetime):
    timestamp_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
    api_dt = {
        "dateTime": timestamp_str,
        "timeZone": "W. Europe Standard Time"
    }
    return api_dt