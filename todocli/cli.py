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

def print_list(list, print_line_nums):
    i = 0
    for x in list:
        if print_line_nums:
            print("[{}] ".format(i), end='')
        print(x)
        i+=1

def ls(args):
    lists = todo_api.query_lists()
    lists_names = [list["displayName"] for list in lists]
    print_list(lists_names, args.display_linenums)

def lst(args):
    tasks = todo_api.query_tasks(args.list_name)
    tasks_titles = [x["title"] for x in tasks]
    print_list(tasks_titles, args.display_linenums)

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

def tryParseAsInt(input_str: str):
    try:
        return int(input_str)
    except (ValueError):
        return input_str


def complete(args):
    list, name = parseTaskPath(args.task_name)

    if list is None:
        list = "Tasks"

    todo_api.complete_task(list, tryParseAsInt(name))
    pass

class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(message, file=sys.stderr)
        raise



def setupParser():
    parser = ArgumentParser(description='Command line interface for Microsoft ToDo')
    parser.add_argument("--display_linenums", '-n', action='store_true', default=False, help="Display line numbers for the results")
    parser.add_argument("--interactive", '-i', action='store_true', default=False, help="Interactive mode. Don't exit the application after invoking a command, ask for follow up commands instead.")

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
        subparser.add_argument("task_name", help="""
        Specify the task to complete. 
        Can be one of the following:
        task_name 
        list_name/task_name 
        task_number
        list_name/task_number
        
        'task_number' is the number displayed when providing the argument '-n'  
        """
                                                 )
        subparser.set_defaults(func=complete)

    parser_lst()
    parser_ls()
    parser_new()
    parser_newl()
    parser_complete()

    return parser

def main():
    try:
        parser = setupParser()

        isInteractive = False

        if '-i' in sys.argv or '--interactive' in sys.argv:
            isInteractive = True

        while (True):
            try:
                args = parser.parse_args()
                args.func(args)
            except TypeError as e:
                parser.print_help()
            except:
                pass
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
                pass

            if isInteractive:
                sys.argv = sys.argv[:1]
                arg = input("\nInput command: ")
                args = arg.split()
                sys.argv = sys.argv[:1]
                sys.argv += args
            else:
                exit()
    except KeyboardInterrupt:
        print('\n')
        exit(0)



if __name__ == "__main__":
    #sys.argv.append('-i')
    #sys.argv.append('bla')
    main()
    exit()