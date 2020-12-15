"""
For implementation details, refer to this source:
https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime
from typing import Union, List

from todocli.task import Task
from todocli.todo_api import querys
from todocli.todo_api.rest_request_list import RestRequestListModify, RestRequestListNew
from todocli.todo_api.rest_request_task import (
    RestRequestTaskModify,
    RestRequestTaskNew,
    RestRequestTaskDelete,
)


def get_lists():
    return querys.query_lists()


def get_list(list_name):
    return querys.query_list(list_name)


def create_list(title: str):
    return RestRequestListNew(title).execute()


def rename_list(old_list_title: str, new_list_title: str):
    return (
        RestRequestListModify(old_list_title).set_display_name(new_list_title).execute()
    )


def get_tasks(list_name) -> List[Task]:
    query_result = querys.query_tasks(list_name)

    return [Task(x) for x in query_result]


def get_task(list_name, task_name):
    return Task(querys.query_task(list_name, task_name))


def create_task(task_name: str, list_name: str, reminder_datetime: datetime = None):
    request = RestRequestTaskNew(list_name, task_name)

    if reminder_datetime is not None:
        request.set_reminder(reminder_datetime)

    return request.execute()


def complete_task(list_name: str, task_name: Union[str, int]):
    return RestRequestTaskModify(list_name, task_name).set_completed().execute()


def remove_task(task_list, task_name_or_listpos):
    return RestRequestTaskDelete(task_list, task_name_or_listpos).execute()
