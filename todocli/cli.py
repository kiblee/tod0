import sys

from todocli.error import error
from todocli import auth
from todocli.todo_api import list_and_cache_folders, create_task, Folders, query_tasks


from todocli.datetime_parser import parseDateTime

import argparse

def parseTaskPath(task_path):
    if '/' in task_path:
        elems = task_path.split('/')
        if len(elems) > 2:
            error("Invalid path, path can only contain one '/'")
        return elems[0], elems[1]
    else:
        return None, task_path


def createNewTask(new_task_path : str):
    list_and_cache_folders()
    folder, name = parseTaskPath(new_task_path)

    reminder_date_time_str = sysarg_parser.get("reminder_date_time")
    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parseDateTime(reminder_date_time_str)

    if folder is None:
        folder = "Tasks"

    create_task(name, folder, reminder_datetime)
    pass

def ls(args):
    for folder in Folders.folders_raw:
        print(folder["displayName"])

    return 0

def lst(args):
    tasks = query_tasks(args.list_name)
    for task in tasks:
        print(task)

def new(args):
    pass

def newl(args):
    pass

def setupParser():
    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.set_defaults(func=None)
    # arg = parser.add_argument('command', choices=['ls', 'lst', 'new', 'newl'])
    subparsers = parser.add_subparsers(help='Command to execute')

    parser_ls = subparsers.add_parser('ls', help='Display all lists.')
    parser_ls.set_defaults(func=ls)

    parser_lst = subparsers.add_parser('lst', help='Display tasks from a list.')
    parser_lst.add_argument("list_name", nargs='?', default="Tasks",
                            help="This optional argument specifies the list from which the tasks are displayed.")
    parser_lst.set_defaults(func=lst)

    parser_new = subparsers.add_parser('new', help='a help')
    parser_new.set_defaults(func=new)

    parser_newl = subparsers.add_parser('newl', help='a help')
    parser_newl.set_defaults(func=newl)
    return parser



def main():
    list_and_cache_folders()
    parser = setupParser()

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    list_and_cache_folders()
    parser = setupParser()
    parser.print_help()

    arg = input("Input command:\n")
    args = arg.split()
    for arg in args:
        sys.argv.append(arg)
    print("Invoking: {}".format(" ".join(sys.argv)))
    args = parser.parse_args()
    args.func(args)
    exit()
