import sys

from todocli.error import error
from todocli import auth
import todocli.todo_api as todo_api

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


def ls(args):
    for folder in todo_api.Folders.folders_raw:
        print(folder["displayName"])

def lst(args):
    tasks = todo_api.query_tasks(args.list_name)
    tasks_titles = [x["title"] for x in tasks]
    for task in tasks_titles:
        print(task)

def new(args):
    list, name = parseTaskPath(args.task_name)

    reminder_date_time_str = args.reminder
    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parseDateTime(reminder_date_time_str)

    if list is None:
        list = "Tasks"

    todo_api.create_task(name, list, reminder_datetime)
    pass

def newl(args):
    todo_api.create_list(args.list_name)
    pass

def complete(args):
    list, name = parseTaskPath(args.task_name)

    if list is None:
        list = "Tasks"

    todo_api.complete_task(list, name)
    pass

def setupParser():
    parser = argparse.ArgumentParser(description='Command line interface for Microsoft ToDo')

    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help='Command to execute')

    def parser_ls():
        subparser = subparsers.add_parser('ls', help='Display all lists')
        subparser.set_defaults(func=ls)

    def parser_lst():
        subparser = subparsers.add_parser('lst', help='Display tasks from a list')
        subparser.add_argument("list_name", nargs='?', default="Tasks",
                                help="This optional argument specifies the list from which the tasks are displayed.")
        subparser.set_defaults(func=lst)

    def parser_new():
        subparser = subparsers.add_parser('new', help='Add a new task')
        subparser.add_argument('task_name',
                                help="Specify the task name. It's also possible to specify a task in a specific list by writing: list_name/task_name")
        subparser.add_argument('-r', '--reminder')
        subparser.set_defaults(func=new)

    def parser_newl():
        subparser = subparsers.add_parser('newl', help='Add a new list')
        subparser.add_argument("list_name", help="Name of the list to create")
        subparser.set_defaults(func=newl)

    def parser_complete():
        subparser = subparsers.add_parser('complete', help='Complete a Task')
        subparser.add_argument("task_name", help="Specify the task name. It's also possible to specify a task in a specific list by writing: list_name/task_name")
        subparser.set_defaults(func=complete)

    parser_lst()
    parser_ls()
    parser_new()
    parser_newl()
    parser_complete()

    return parser

def main():
    todo_api.list_and_cache_folders()
    parser = setupParser()

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    todo_api.list_and_cache_folders()
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
