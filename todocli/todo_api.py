"""
For implementation details, refer to this source:
https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime
from typing import Union

from todocli import api_urls
from todocli.rest_request import (
    RestRequestGet,
    RestRequestPost,
    RestRequestPatch,
    RestRequestDelete,
    RestRequestWithBody,
)
from todocli.task import Task
from todocli.todo_api_util import datetime_to_api_timestamp

list_ids_cached = {}


class ListNotFound(Exception):
    def __init__(self, list_name):
        self.message = "List with name '{}' could not be found".format(list_name)
        super(ListNotFound, self).__init__(self.message)


class TaskNotFoundByName(Exception):
    def __init__(self, task_name, list_name):
        self.message = "Task with name '{}' could not be found in list '{}'".format(
            task_name, list_name
        )
        super(TaskNotFoundByName, self).__init__(self.message)


class TaskNotFoundByIndex(Exception):
    def __init__(self, task_index, list_name):
        self.message = "Task with index '{}' could not be found in list '{}'".format(
            task_index, list_name
        )
        super(TaskNotFoundByIndex, self).__init__(self.message)


class _RestRequestTask:
    def __init__(self):
        self.request = None

    def set_completed(self):
        self.request["completedDateTime"] = datetime_to_api_timestamp(datetime.now())
        self.set_status(Task.Status.Completed)

    def set_status(self, status: Task.Status):
        self.request["status"] = status.value

    def set_importance(self, importance: Task.Importance):
        self.request["importance"] = importance.value

    def set_title(self, title: str):
        self.request["title"] = title

    def set_reminder(self, reminder_datetime):
        self.request["isReminderOn"] = True
        self.request["reminderDateTime"] = datetime_to_api_timestamp(reminder_datetime)

    def execute(self):
        return self.request.execute()


class RestRequestTaskModify(_RestRequestTask):
    def __init__(self, list_name, task_name):
        super().__init__()

        url = api_urls.modify_task(
            get_list_id_by_name(list_name), get_task_id(list_name, task_name)
        )
        self.request = RestRequestPatch(url)


class RestRequestTaskNew(_RestRequestTask):
    def __init__(self, list_name, task_name):
        super().__init__()

        url = api_urls.new_task(get_list_id_by_name(list_name))
        self.request = RestRequestPost(url)
        self.set_title(task_name)

    def _get_request(self) -> RestRequestWithBody:
        return self.request


def query_list_id_by_name(list_name):
    url = api_urls.query_list_id_by_name(list_name)
    res = RestRequestGet(url).execute()

    try:
        return res[0]["id"]
    except IndexError:
        raise ListNotFound(list_name)


def get_list_id_by_name(list_name: str):
    if list_name not in list_ids_cached:
        list_id = query_list_id_by_name(list_name)
        list_ids_cached[list_name] = list_id
        return list_id
    else:
        return list_ids_cached[list_name]


def query_tasks(list_name: str, num_tasks: int = 100):
    query_url = api_urls.query_completed_tasks(
        get_list_id_by_name(list_name), num_tasks
    )
    return RestRequestGet(query_url).execute()


def query_task(list_name: str, task_name: str):
    query_url = api_urls.query_task_by_name(get_list_id_by_name(list_name), task_name)
    return RestRequestGet(query_url).execute()


def create_list(title: str):
    request = RestRequestPost(api_urls.new_list())
    request["title"] = title
    return request.execute()


def rename_list(old_list_title: str, new_list_title: str):
    request = RestRequestPatch(
        api_urls.modify_list(get_list_id_by_name(old_list_title))
    )
    request["title"] = new_list_title
    return request.execute()


def create_task(task_name: str, list_name: str, reminder_datetime: datetime = None):
    request = RestRequestTaskNew(list_name, task_name)

    if reminder_datetime is not None:
        request.set_reminder(reminder_datetime)

    return request.execute()


def query_lists():
    lists = RestRequestGet(api_urls.all_lists()).execute()
    return lists


def get_task_id_by_name(list_name: str, task_name: str):
    try:
        return query_task(list_name, task_name)[0]["id"]
    except IndexError:
        raise TaskNotFoundByName(task_name, list_name)


def get_task_id_by_list_position(list_name: str, task_list_position):
    tasks = query_tasks(list_name, task_list_position + 1)
    try:
        return tasks[task_list_position]["id"]
    except IndexError:
        raise TaskNotFoundByIndex(task_list_position, list_name)


def get_task_id(list_name: str, task_name_or_listpos: Union[str, int]):
    if isinstance(task_name_or_listpos, str):
        return get_task_id_by_name(list_name, task_name_or_listpos)
    elif isinstance(task_name_or_listpos, int):
        return get_task_id_by_list_position(list_name, task_name_or_listpos)
    else:
        raise


def complete_task(list_name: str, task_name: Union[str, int]):
    request = RestRequestTaskModify(list_name, task_name)
    request.set_completed()
    request.execute()


def remove_task(task_list, param):
    task_id = get_task_id(task_list, param)
    url = api_urls.delete_task(task_list, task_id)
    request = RestRequestDelete(url)
    request.execute()
