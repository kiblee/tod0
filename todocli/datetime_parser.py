import re
from datetime import datetime, timedelta


def parseHourMinute(input_str):
    split_str = input_str.split(':')
    hour = int(split_str[0])
    minute = int(split_str[1])
    return hour, minute


def parseDayMonth(input_str):
    split_str = input_str.split('.')
    day = int(split_str[0])
    month = int(split_str[1])
    return day, month


def parseDateTime(datetime_str: str):
    if re.match(r"([0-9]{1,2}h)", datetime_str):
        """ e.g. 1h / 12h """
        return datetime.now() + timedelta(hours=int(datetime_str[:-1]))
    if datetime_str == "morgen":
        return datetime.now().replace(hour=7) + timedelta(days=1)
    if datetime_str == "abend":
        dt = datetime.now()
        if dt.hour > 18:
            dt = dt + timedelta(days=1)
        return dt.replace(hour=18)
    if re.match(r"([0-9]{2}:[0-9]{2})", datetime_str):
        """ e.g. 17:00 """
        hour, minute = parseHourMinute(datetime_str)
        return datetime.now().replace(hour=hour, minute=minute)
    if re.match(r"([0-9]{2}:[0-9]{2})", datetime_str):
        """ e.g. 17.01. 17:00 """
        split_str = datetime_str.split(' ')
        day, month = parseDayMonth(split_str[0])
        hour, minute = parseHourMinute(split_str[1])
        return datetime.now().replace(day=day, month=month, hour=hour, minute=minute)
