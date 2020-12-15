from typing import Union

from todocli import api_urls
from todocli.rest_request import RestRequestGet
from todocli.todo_api.exceptions import (
    TaskNotFoundByName,
    TaskNotFoundByIndex,
    ListNotFound,
)

list_ids_cached = {}


def query_tasks(list_name: str, completed=True, num_tasks: int = 100):
    if completed:
        query_url = api_urls.get_tasks_completed(
            get_list_id_by_name(list_name), num_tasks
        )
    else:
        query_url = api_urls.get_tasks(get_list_id_by_name(list_name), num_tasks)

    return RestRequestGet(query_url).execute()


def query_task(list_name: str, task_name: str):
    query_url = api_urls.get_task_by_name(get_list_id_by_name(list_name), task_name)
    try:
        return RestRequestGet(query_url).execute()[0]
    except IndexError:
        raise TaskNotFoundByName(task_name, list_name)


def query_lists():
    return RestRequestGet(api_urls.get_all_lists()).execute()


def get_task_id_by_name(list_name: str, task_name: str):
    result_task = query_task(list_name, task_name)
    return result_task["id"]


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


def query_list_id_by_name(list_name):
    result_list = query_list(list_name)
    return result_list["id"]


def get_list_id_by_name(list_name: str):
    if list_name not in list_ids_cached:
        list_id = query_list_id_by_name(list_name)
        list_ids_cached[list_name] = list_id
        return list_id
    else:
        return list_ids_cached[list_name]


def query_list(list_name):
    url = api_urls.get_list_by_name(list_name)
    try:
        return RestRequestGet(url).execute()[0]
    except IndexError:
        raise ListNotFound(list_name)
