import argparse
import shlex
import sys

import todocli.todo_api as todo_api
from todocli.datetime_parser import parse_datetime
from todocli.error import error, eprint


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


def print_list(item_list, print_line_nums):
    for i, x in enumerate(item_list):
        if print_line_nums:
            print("[{}] ".format(i), end="")
        print(x)


def ls(args):
    lists = todo_api.query_lists()
    lists_names = [task_list["displayName"] for task_list in lists]
    print_list(lists_names, args.display_linenums)


def lst(args):
    tasks = todo_api.query_tasks(args.list_name)
    tasks_titles = [x["title"] for x in tasks]
    print_list(tasks_titles, args.display_linenums)


def new(args):
    task_list, name = parse_task_path(args.task_name)

    reminder_date_time_str = args.reminder
    reminder_datetime = None

    if reminder_date_time_str is not None:
        reminder_datetime = parse_datetime(reminder_date_time_str)

    todo_api.create_task(name, task_list, reminder_datetime)


def newl(args):
    todo_api.create_list(args.list_name)


def try_parse_as_int(input_str: str):
    try:
        return int(input_str)
    except ValueError:
        return input_str


def complete(args):
    task_list, name = parse_task_path(args.task_name)

    todo_api.complete_task(task_list, try_parse_as_int(name))


def rm(args):
    task_list, name = parse_task_path(args.task_name)
    todo_api.remove_task(task_list, try_parse_as_int(name))


class ArgumentParser(argparse.ArgumentParser):
    class OnExit(Exception):
        pass

    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        raise self.OnExit()


helptext_task_name = """
        Specify the task to complete. 
        Can be one of the following:
        task_name 
        list_name/task_name 
        task_number
        list_name/task_number

        'task_number' is the number displayed when providing the argument '-n'  
        """


def setup_parser():
    parser = ArgumentParser(description="Command line interface for Microsoft ToDo")

    parser.set_defaults(func=None)
    subparsers = parser.add_subparsers(help="Command to execute")

    def parser_ls():
        subparser = subparsers.add_parser("ls", help="Display all lists")
        subparser.set_defaults(func=ls)

    def parser_lst():
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

    def parser_new():
        subparser = subparsers.add_parser("new", help="Add a new task")
        subparser.add_argument("task_name", help=helptext_task_name)
        subparser.add_argument("-r", "--reminder")
        subparser.set_defaults(func=new)

    def parser_newl():
        subparser = subparsers.add_parser("newl", help="Add a new list")
        subparser.add_argument("list_name", help="Name of the list to create")
        subparser.set_defaults(func=newl)

    def parser_complete():
        subparser = subparsers.add_parser("complete", help="Complete a Task")
        subparser.add_argument("task_name", help=helptext_task_name)
        subparser.set_defaults(func=complete)

    def parser_rm():
        subparser = subparsers.add_parser("rm", help="Remove a Task")
        subparser.add_argument("task_name", help=helptext_task_name)
        subparser.set_defaults(func=rm)

    parser_lst()
    parser_ls()
    parser_new()
    parser_newl()
    parser_complete()
    parser_rm()

    parser.add_argument(
        "-n",
        "--display_linenums",
        action="store_true",
        default=False,
        help="Display line numbers for the results",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        default=False,
        help="Interactive mode. \
                            Don't exit the application after invoking a command, ask for follow up commands instead.",
    )

    return parser


def main():
    try:
        parser = setup_parser()

        isInteractive = False

        if "-i" in sys.argv or "--interactive" in sys.argv:
            isInteractive = True

        while True:
            try:
                namespace, args = parser.parse_known_args()
                parser.parse_args(args, namespace)

                namespace.func(namespace)

            except TypeError:
                parser.print_help()
            except argparse.ArgumentError:
                pass
            except ArgumentParser.OnExit:
                pass
            except todo_api.TaskNotFoundByName as e:
                eprint(e.message)
            except todo_api.ListNotFound as e:
                eprint(e.message)
            except todo_api.TaskNotFoundByIndex as e:
                eprint(e.message)
            except InvalidTaskPath as e:
                eprint(e.message)
            finally:
                sys.stdout.flush()
                sys.stderr.flush()
                pass

            if isInteractive:
                arg = input("\nInput command: ")
                args = shlex.split(arg)
                sys.argv = sys.argv[:1]
                sys.argv += args
            else:
                exit()
    except KeyboardInterrupt:
        print("\n")
        exit(0)


if __name__ == "__main__":
    sys.argv.append("-i")
    main()
