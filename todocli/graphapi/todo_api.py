"""
For implementation details, refer to this source:
https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
import json
from datetime import datetime
from typing import Union

from todocli.models.todolist import TodoList
from todocli.models.task import Task, TaskStatus
from todocli.graphapi.oauth import get_oauth_session

from todocli.graphapi import endpoints
from todocli.utils.datetime_util import datetime_to_api_timestamp

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


def parse_response(response):
    return json.loads(response.content.decode())["value"]


def get_lists():
    session = get_oauth_session()
    response = session.get(endpoints.all_lists())
    response_value = parse_response(response)
    return [TodoList(x) for x in response_value]


def create_list(title: str):
    request_body = {"displayName": title}
    session = get_oauth_session()
    response = session.post(endpoints.new_list(), json=request_body)
    return True if response.ok else response.raise_for_status()


# TODO No associated command
def rename_list(old_title: str, new_title: str):
    request_body = {"title": new_title}
    session = get_oauth_session()
    response = session.patch(
        endpoints.modify_list(get_list_id_by_name(old_title)), json=request_body
    )
    return True if response.ok else response.raise_for_status()


def get_tasks(list_name: str, num_tasks: int = 100):
    query_url = endpoints.query_completed_tasks(
        get_list_id_by_name(list_name), num_tasks
    )
    session = get_oauth_session()
    response = session.get(query_url)
    response_value = parse_response(response)
    return [Task(x) for x in response_value]


def create_task(task_name: str, list_name: str, reminder_datetime: datetime = None):
    url = endpoints.new_task(get_list_id_by_name(list_name))
    request_body = {
        "title": task_name,
        "reminderDateTime": datetime_to_api_timestamp(reminder_datetime),
    }
    session = get_oauth_session()
    response = session.post(url, json=request_body)
    return True if response.ok else response.raise_for_status()


def complete_task(list_name: str, task_name: Union[str, int]):
    url = endpoints.modify_task(
        get_list_id_by_name(list_name), get_task_id(list_name, task_name)
    )
    request_body = {
        "status": TaskStatus.COMPLETED,
        "completedDateTime": datetime_to_api_timestamp(datetime.now()),
    }
    session = get_oauth_session()
    response = session.patch(url, json=request_body)
    return True if response.ok else response.raise_for_status()


def remove_task(task_list: str, task_name: Union[str, int]):
    task_id = get_task_id(task_list, task_name)
    url = endpoints.delete_task(task_list, task_id)

    session = get_oauth_session()
    response = session.delete(url)
    return True if response.ok else response.raise_for_status()


def query_list_id_by_name(list_name):
    url = endpoints.query_list_id_by_name(list_name)

    session = get_oauth_session()
    response = session.get(url)
    response_value = parse_response(response)
    try:
        return response_value[0]["id"]
    except IndexError:
        raise ListNotFound(list_name)


def get_list_id_by_name(list_name: str):
    if list_name not in list_ids_cached:
        list_id = query_list_id_by_name(list_name)
        list_ids_cached[list_name] = list_id
        return list_id
    else:
        return list_ids_cached[list_name]


def query_task(list_name: str, task_name: str):
    query_url = endpoints.query_task_by_name(get_list_id_by_name(list_name), task_name)

    session = get_oauth_session()
    response = session.get(query_url)
    response_value = parse_response(response)
    return [Task(x) for x in response_value]


def get_task_id_by_name(list_name: str, task_name: str):
    try:
        return query_task(list_name, task_name)[0].id
    except IndexError:
        raise TaskNotFoundByName(task_name, list_name)


def get_task_id_by_list_position(list_name: str, task_list_position):
    tasks = get_tasks(list_name, task_list_position + 1)
    try:
        return tasks[task_list_position].id
    except IndexError:
        raise TaskNotFoundByIndex(task_list_position, list_name)


def get_task_id(list_name: str, task_name_or_listpos: Union[str, int]):
    if isinstance(task_name_or_listpos, str):
        return get_task_id_by_name(list_name, task_name_or_listpos)
    elif isinstance(task_name_or_listpos, int):
        return get_task_id_by_list_position(list_name, task_name_or_listpos)
    else:
        raise
