import re
from datetime import date

from todocli.models.todotask import RecurrencePatternType, DayOfWeek


class InvalidRecurrenceExpression(Exception):
    def __init__(self, expr):
        self.message = f"Invalid recurrence expression: '{expr}'"
        super().__init__(self.message)


DAY_MAP = {
    "mon": DayOfWeek.MONDAY,
    "tue": DayOfWeek.TUESDAY,
    "wed": DayOfWeek.WEDNESDAY,
    "thu": DayOfWeek.THURSDAY,
    "fri": DayOfWeek.FRIDAY,
    "sat": DayOfWeek.SATURDAY,
    "sun": DayOfWeek.SUNDAY,
}

UNIT_MAP = {
    "day": RecurrencePatternType.DAILY,
    "days": RecurrencePatternType.DAILY,
    "week": RecurrencePatternType.WEEKLY,
    "weeks": RecurrencePatternType.WEEKLY,
    "month": RecurrencePatternType.ABSOLUTE_MONTHLY,
    "months": RecurrencePatternType.ABSOLUTE_MONTHLY,
    "year": RecurrencePatternType.ABSOLUTE_YEARLY,
    "years": RecurrencePatternType.ABSOLUTE_YEARLY,
}

PRESET_MAP = {
    "daily": (RecurrencePatternType.DAILY, 1),
    "weekly": (RecurrencePatternType.WEEKLY, 1),
    "monthly": (RecurrencePatternType.ABSOLUTE_MONTHLY, 1),
    "yearly": (RecurrencePatternType.ABSOLUTE_YEARLY, 1),
}

WEEKDAYS = [
    DayOfWeek.MONDAY,
    DayOfWeek.TUESDAY,
    DayOfWeek.WEDNESDAY,
    DayOfWeek.THURSDAY,
    DayOfWeek.FRIDAY,
]


def _parse_days(days_str):
    days = []
    for d in days_str.split(","):
        d = d.strip().lower()
        if d not in DAY_MAP:
            raise ValueError(d)
        days.append(DAY_MAP[d])
    return days


def parse_recurrence(expr):
    if expr is None:
        return None

    expr = expr.strip()
    if not expr:
        return None

    # Split on ":" to separate base from day specifiers
    parts = expr.split(":", 1)
    base_part = parts[0].strip().lower()
    days_part = parts[1].strip() if len(parts) > 1 else None

    pattern_type = None
    interval = 1

    # Check for "weekdays" preset
    if base_part == "weekdays":
        pattern_type = RecurrencePatternType.WEEKLY
        interval = 1
        days_part = days_part or "mon,tue,wed,thu,fri"

    # Check for simple presets
    elif base_part in PRESET_MAP:
        pattern_type, interval = PRESET_MAP[base_part]

    # Check for "every N unit" format
    else:
        match = re.match(r"^every\s+(\d+)\s+(days?|weeks?|months?|years?)$", base_part)
        if match:
            interval = int(match.group(1))
            unit = match.group(2)
            pattern_type = UNIT_MAP[unit]
        else:
            raise InvalidRecurrenceExpression(expr)

    # Build pattern
    today = date.today()
    pattern = {
        "type": pattern_type.value,
        "interval": interval,
    }

    if days_part:
        try:
            pattern["daysOfWeek"] = [d.value for d in _parse_days(days_part)]
        except ValueError:
            raise InvalidRecurrenceExpression(expr)

    if pattern_type == RecurrencePatternType.ABSOLUTE_MONTHLY:
        pattern["dayOfMonth"] = today.day

    if pattern_type == RecurrencePatternType.ABSOLUTE_YEARLY:
        pattern["dayOfMonth"] = today.day
        pattern["month"] = today.month

    return {
        "pattern": pattern,
        "range": {
            "type": "noEnd",
            "startDate": today.isoformat(),
        },
    }
