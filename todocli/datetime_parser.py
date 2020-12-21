import re
from datetime import datetime, timedelta


def parse_hour_minute(input_str):
    split_str = input_str.split(":")
    hour = int(split_str[0])
    minute = int(split_str[1])
    return hour, minute


def parse_day_month_DD_MM(input_str):
    split_str = input_str.split(".")
    day = int(split_str[0])
    month = int(split_str[1])
    return day, month


def parse_day_month_MM_DD(input_str):
    split_str = input_str.split("/")
    month = int(split_str[0])
    day = int(split_str[1])
    return day, month


def parse_day_month_DD_MM_YYorYYYY(input_str):
    split_str = input_str.split(".")
    day = int(split_str[0])
    month = int(split_str[1])
    year = split_str[2]
    if len(year) == 2:
        year = int("20" + year)
    else:
        year = int(year)
    return day, month, year


def add_day_if_past(dt: datetime) -> datetime:
    """This function will add a day to the datetime object 'dt' when 'dt' is in the past"""
    dt_now = datetime.now()
    if dt < dt_now:
        return dt + timedelta(days=1)
    else:
        return dt


class TimeExpressionNotRecognized(Exception):
    def __init__(self, time_str):
        self.message = f"Time expression could not be parsed: {time_str}"
        super(TimeExpressionNotRecognized, self).__init__(self.message)


class ErrorParsingTime(Exception):
    def __init__(self, message):
        self.message = message
        super(ErrorParsingTime, self).__init__(message)


def parse_datetime(datetime_str: str):
    try:
        if re.match(r"([0-9]{1,2}h)", datetime_str, re.IGNORECASE):
            """ e.g. 1h / 12h """
            return datetime.now() + timedelta(hours=int(datetime_str[:-1]))

        if datetime_str == "morning":
            dt = datetime.now()
            return add_day_if_past(
                dt.replace(hour=7, minute=0, second=0, microsecond=0)
            )

        if datetime_str == "tomorrow":
            dt = datetime.now()
            return dt.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(
                days=1
            )

        if datetime_str == "evening":
            dt = datetime.now()
            return add_day_if_past(
                dt.replace(hour=18, minute=0, second=0, microsecond=0)
            )

        if re.match(r"([0-9]{1,2}:[0-9]{2} (am|pm))", datetime_str, re.IGNORECASE):
            """ e.g. 5:30 pm """
            split_str = datetime_str.split(" ")
            hour, minute = parse_hour_minute(split_str[0])

            if split_str[1] == "am":
                if hour == 12:
                    hour = 0
            else:
                hour = hour + 12

            return add_day_if_past(
                datetime.now().replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
            )

        if re.match(r"([0-9]{1,2}:[0-9]{2})", datetime_str, re.IGNORECASE):
            """ e.g. 17:00 """
            hour, minute = parse_hour_minute(datetime_str)
            return add_day_if_past(
                datetime.now().replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
            )

        if re.match(
            r"([0-9]{1,2}\.[0-9]{1,2}\.(([0-9]{4})|([0-9]{2})))$",
            datetime_str,
            re.IGNORECASE,
        ):
            """ e.g. 17.01.20 or 22.12.2020 """
            day, month, year = parse_day_month_DD_MM_YYorYYYY(datetime_str)
            return datetime.now().replace(
                year=year,
                day=day,
                month=month,
                hour=7,
                minute=0,
                second=0,
                microsecond=0,
            )

        if re.match(
            r"([0-9]{1,2}\.[0-9]{1,2}\. [0-9]{1,2}:[0-9]{2})",
            datetime_str,
            re.IGNORECASE,
        ):
            """ e.g. 17.01. 17:00 """
            split_str = datetime_str.split(" ")
            day, month = parse_day_month_DD_MM(split_str[0])
            hour, minute = parse_hour_minute(split_str[1])
            return datetime.now().replace(
                day=day, month=month, hour=hour, minute=minute, second=0, microsecond=0
            )

        # if re.match(
        #     r"([0-9]{1,2}/[0-9]{1,2} [0-9]{1,2}:[0-9]{2} (am|pm))",
        #     datetime_str,
        #     re.IGNORECASE,
        # ):
        #     """ e.g. 01/17 5:00 pm """
        #     split_str = datetime_str.split(" ")
        #     day, month = parse_day_month_MM_DD(split_str[0])
        #     hour, minute = parse_hour_minute(split_str[1])
        #     return datetime.now().replace(
        #         day=day, month=month, hour=hour, minute=minute, second=0, microsecond=0
        #     )

    except ValueError as e:
        raise ErrorParsingTime(str(e))

    raise TimeExpressionNotRecognized(datetime_str)
