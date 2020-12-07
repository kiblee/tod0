from todocli.error import error
from todocli import auth

from .sysargs import SysargParser
from .datetime_parser import parseDateTime

sysarg_parser = SysargParser()

def parseTaskPath(task_path):
    if '/' in task_path:
        elems = task_path.split('/')
        if len(elems) > 2:
            error("Invalid path, path can only contain one '/'")
        return elems[0], elems[1]
    else:
        return None, task_path


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
