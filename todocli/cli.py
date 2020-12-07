from error import error
from todocli import auth

from sysargs import SysargParser

sysarg_parser = SysargParser()

def parseTaskPath(task_path):
    if '/' in task_path:
        elems = task_path.split('/')
        if len(elems) > 2:
            error("Invalid path, path can only contain one '/'")
        return elems[0], elems[1]
    else:
        return None, task_path

from datetime import datetime, timedelta

import re

def parseDateTime(input_str : str):
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

    if re.match(r"([0-9]{1,2}h)", input_str):
        """ e.g. 1h / 12h """
        return datetime.now() + timedelta(hours=int(input_str[:-1]))
    if input_str == "morgen":
        return datetime.now().replace(hour=7) + timedelta(days=1)
    if input_str == "abend":
        dt = datetime.now()
        if dt.hour > 18:
            dt = dt + timedelta(days=1)
        return dt.replace(hour=18)
    if re.match(r"([0-9]{2}:[0-9]{2})", input_str):
        """ e.g. 17:00 """
        hour, minute = parseHourMinute(input_str)
        return datetime.now().replace(hour=hour, minute=minute)
    if re.match(r"([0-9]{2}:[0-9]{2})", input_str):
        """ e.g. 17.01. 17:00 """
        split_str = input_str.split(' ')
        day, month = parseDayMonth(split_str[0])
        hour, minute = parseHourMinute(split_str[1])
        return datetime.now().replace(day= day, month=month, hour=hour, minute=minute)



def createNewTask(new_task_path : str):
    auth.list_and_update_folders_new()
    folder, name = parseTaskPath(new_task_path)

    reminder_date_time_str = sysarg_parser.get("reminder_date_time")

    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parseDateTime(reminder_date_time_str)

    auth.create_task_new(name, folder, reminder_datetime)
    pass





def main():

    sysarg_parser.addOptionValue("new_task_path", None, str, "-n")
    sysarg_parser.addOptionValue("reminder_date_time", None, str, "-r")
    sysarg_parser.parseArgs()

    new_task_path = sysarg_parser.get("new_task_path")
    if new_task_path is not None:
        createNewTask(new_task_path)

    pass

if __name__ == "__main__":
    auth.list_and_update_folders_new()
    exit(main())
