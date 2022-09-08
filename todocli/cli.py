import argparse
import shlex
import sys

import todocli.graphapi.wrapper as wrapper
from todocli.utils import update_checker
from todocli.utils.datetime_util import (
    parse_datetime,
    TimeExpressionNotRecognized,
    ErrorParsingTime,
)


class InvalidTaskPath(Exception):
    def __init__(self, path):
        self.message = (
            "Invalid path: '{}', path can only contain one '/'. "
            "Please specify the task in format: '<list>/<task>'".format(path)
        )
        super(InvalidTaskPath, self).__init__(self.message)


def parse_task_path(task_path):
    if "/" in task_path:
        elems = task_path.split("/")
        if len(elems) > 2:
            raise InvalidTaskPath(task_path)
        return elems[0], elems[1]
    else:
        return "Tasks", task_path


def print_list(item_list):
    for i, x in enumerate(item_list):
        print(f"[{i}]\t{x}")


def ls(args):
    lists = wrapper.get_lists()
    lists_names = [l.display_name for l in lists]
    print_list(lists_names)


def lst(args):
    tasks = wrapper.get_tasks(list_name=args.list_name)
    tasks_titles = [x.title for x in tasks]
    print_list(tasks_titles)


def new(args):
    task_list, name = parse_task_path(args.task_name)

    reminder_date_time_str = args.reminder
    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parse_datetime(reminder_date_time_str)

    wrapper.create_task(name, list_name=task_list, reminder_datetime=reminder_datetime)


def newl(args):
    wrapper.create_list(args.list_name)


def try_parse_as_int(input_str: str):
    try:
        return int(input_str)
    except ValueError:
        return input_str


def complete(args):
    task_list, name = parse_task_path(args.task_name)
    wrapper.complete_task(list_name=task_list, task_name=try_parse_as_int(name))


def rm(args):
    task_list, name = parse_task_path(args.task_name)
    wrapper.remove_task(task_list, try_parse_as_int(name))


helptext_task_name = """
        Specify the task to complete.
        Can be one of the following:
        task_name
        list_name/task_name
        task_number
        list_name/task_number
        """


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Command line interface for Microsoft ToDo"
    )
    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help="Command to execute")

    # create parser for 'ls' command
    subparser = subparsers.add_parser("ls", help="Display all lists")
    subparser.set_defaults(func=ls)

    # create parser for 'lst' command
    subparser = subparsers.add_parser("lst", help="Display tasks from a list")
    subparser.add_argument(
        "list_name",
        nargs="?",
        default="Tasks",
        help="This optional argument specifies the list from which the tasks are displayed."
        "If this parameter is omitted, \
                                all tasks from the default task list will be displayed",
    )
    subparser.set_defaults(func=lst)

    # create parser for 'new' command
    subparser = subparsers.add_parser("new", help="Add a new task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.add_argument("-r", "--reminder")
    subparser.set_defaults(func=new)

    # create parser for 'newl' command
    subparser = subparsers.add_parser("newl", help="Add a new list")
    subparser.add_argument("list_name", help="Name of the list to create")
    subparser.set_defaults(func=newl)

    # create parser for 'complete' command
    subparser = subparsers.add_parser("complete", help="Complete a Task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.set_defaults(func=complete)

    # create parser for 'rm' command
    subparser = subparsers.add_parser("rm", help="Remove a Task")
    subparser.add_argument("task_name", help=helptext_task_name)
    subparser.set_defaults(func=rm)

    return parser


def main():
    try:
        parser = setup_parser()

        while True:
            try:
                namespace, args = parser.parse_known_args()
                parser.parse_args(args, namespace)

                if namespace.func is not None:
                    namespace.func(namespace)
                else:
                    # No argument was provided
                    parser.print_usage()

            except argparse.ArgumentError:
                pass
            except wrapper.TaskNotFoundByName as e:
                print(e.message)
            except wrapper.ListNotFound as e:
                print(e.message)
            except wrapper.TaskNotFoundByIndex as e:
                print(e.message)
            except InvalidTaskPath as e:
                print(e.message)
            except TimeExpressionNotRecognized as e:
                print(e.message)
            except ErrorParsingTime as e:
                print(e.message)
            finally:
                sys.stdout.flush()
                sys.stderr.flush()

            arg = input("\nInput command: ")
            args = shlex.split(arg)
            sys.argv = sys.argv[:1]
            sys.argv += args

    except KeyboardInterrupt:
        print("\n")
        exit(0)


if __name__ == "__main__":
    update_checker()
    main()
