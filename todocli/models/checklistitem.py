from datetime import datetime, timezone


def _parse_datetime(dt_str):
    """Parse datetime string from checklist items API.

    The checklistItems endpoint returns datetimes without fractional seconds
    (e.g. "2026-02-04T19:08:45Z"), unlike tasks which include 7 digits
    (e.g. "2024-01-25T10:00:00.0000000Z").
    """
    if dt_str is None:
        return None

    if isinstance(dt_str, dict):
        dt_str = dt_str["dateTime"]

    # Strip trailing Z
    dt_str = dt_str.rstrip("Z")

    # Truncate fractional seconds to 6 digits (Python's %f limit)
    if "." in dt_str:
        base, frac = dt_str.rsplit(".", 1)
        dt_str = f"{base}.{frac[:6]}"

    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
        except ValueError:
            continue

    return None


class ChecklistItem:
    def __init__(self, query_result):
        self.id: str = query_result["id"]
        self.display_name: str = query_result["displayName"]
        self.is_checked: bool = bool(query_result["isChecked"])
        self.created_datetime = _parse_datetime(query_result["createdDateTime"])

        if "checkedDateTime" in query_result and query_result["checkedDateTime"]:
            self.checked_datetime = _parse_datetime(query_result["checkedDateTime"])
        else:
            self.checked_datetime = None
