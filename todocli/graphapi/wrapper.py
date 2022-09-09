"""
For implementation details, refer to this source:
https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
import json
from datetime import datetime
from typing import Union

from todocli.models.todolist import TodoList
from todocli.models.todotask import Task, TaskStatus
from todocli.graphapi.oauth import get_oauth_session

from todocli.utils.datetime_util import datetime_to_api_timestamp

BASE_URL = "https://graph.microsoft.com/v1.0/me/todo/lists"


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
    response = session.get(BASE_URL)
    response_value = parse_response(response)
    return [TodoList(x) for x in response_value]


def create_list(title: str):
    request_body = {"displayName": title}
    session = get_oauth_session()
    response = session.post(BASE_URL, json=request_body)
    return True if response.ok else response.raise_for_status()


# TODO No associated command
def rename_list(old_title: str, new_title: str):
    list_id = get_list_id_by_name(old_title)
    request_body = {"title": new_title}
    session = get_oauth_session()
    response = session.patch(f"{BASE_URL}/{list_id}", json=request_body)
    return True if response.ok else response.raise_for_status()


def get_tasks(list_name: str = None, list_id: str = None, num_tasks: int = 100):
    assert (list_name is not None) or (
        list_id is not None
    ), "You must provide list_name or list_id"

    # For compatibility with cli
    if list_id is None:
        list_id = get_list_id_by_name(list_name)

    endpoint = (
        f"{BASE_URL}/{list_id}/tasks?$filter=status ne 'completed'&$top={num_tasks}"
    )
    session = get_oauth_session()
    response = session.get(endpoint)
    response_value = parse_response(response)
    return [Task(x) for x in response_value]


def create_task(
    task_name: str,
    list_name: str = None,
    list_id: str = None,
    reminder_datetime: datetime = None,
):
    assert (list_name is not None) or (
        list_id is not None
    ), "You must provide list_name or list_id"

    # For compatibility with cli
    if list_id is None:
        list_id = get_list_id_by_name(list_name)

    endpoint = f"{BASE_URL}/{list_id}/tasks"
    request_body = {
        "title": task_name,
        "reminderDateTime": datetime_to_api_timestamp(reminder_datetime),
    }
    session = get_oauth_session()
    response = session.post(endpoint, json=request_body)
    return True if response.ok else response.raise_for_status()


def complete_task(
    list_name: str = None,
    task_name: Union[str, int] = None,
    list_id: str = None,
    task_id: str = None,
):
    assert (list_name is not None) or (
        list_id is not None
    ), "You must provide list_name or list_id"
    assert (task_name is not None) or (
        task_id is not None
    ), "You must provide task_name or task_id"

    # For compatibility with cli
    if list_id is None:
        list_id = get_list_id_by_name(list_name)
    if task_id is None:
        task_id = get_task_id_by_name(list_name, task_name)

    endpoint = f"{BASE_URL}/{list_id}/tasks/{task_id}"
    request_body = {
        "status": TaskStatus.COMPLETED,
        "completedDateTime": datetime_to_api_timestamp(datetime.now()),
    }
    session = get_oauth_session()
    response = session.patch(endpoint, json=request_body)
    return True if response.ok else response.raise_for_status()


def remove_task(list_name: str, task_name: Union[str, int]):
    list_id = get_list_id_by_name(list_name)
    task_id = get_task_id_by_name(list_name, task_name)
    endpoint = f"{BASE_URL}/{list_id}/tasks/{task_id}"
    session = get_oauth_session()
    response = session.delete(endpoint)
    return True if response.ok else response.raise_for_status()


def get_list_id_by_name(list_name):
    endpoint = f"{BASE_URL}?$filter=startswith(displayName,'{list_name}')"
    session = get_oauth_session()
    response = session.get(endpoint)
    response_value = parse_response(response)
    try:
        return response_value[0]["id"]
    except IndexError:
        raise ListNotFound(list_name)


def get_task_id_by_name(list_name: str, task_name: str):
    if isinstance(task_name, str):
        try:
            list_id = get_list_id_by_name(list_name)
            endpoint = f"{BASE_URL}/{list_id}/tasks?$filter=title eq '{task_name}'"
            session = get_oauth_session()
            response = session.get(endpoint)
            response_value = parse_response(response)
            return [Task(x) for x in response_value][0].id
        except IndexError:
            raise TaskNotFoundByName(task_name, list_name)
    # elif isinstance(task_name, int):
    #    tasks = get_tasks(list_name, task_list_position + 1)
    #    try:
    #        return tasks[task_list_position].id
    #    except IndexError:
    #        raise TaskNotFoundByIndex(task_list_position, list_name)
    else:
        raise
