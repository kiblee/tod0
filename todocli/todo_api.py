"""
For implementation details, refer to this source:
https://docs.microsoft.com/de-de/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime
from typing import Union

from todocli import api_urls
from todocli.rest_request import RestRequestGet, RestRequestPost, RestRequestPatch, RestRequestDelete
from todocli.todo_api_util import datetime_to_api_timestamp

list_ids_cached = {}


def query_list_id_by_name(list_name):
    url = api_urls.query_lists() + "?$filter=startswith(displayName,'{}')".format(list_name)
    res = RestRequestGet(url).execute()

    return res[0]['id']


def query_tasks(list_name: str, num_tasks: int = 100):
    query_url = api_urls.query_tasks_from_list(get_list_id_by_name(list_name), num_tasks)
    return RestRequestGet(query_url).execute()


def query_task(list_name: str, task_name: str):
    query_url = api_urls.query_task_by_name(get_list_id_by_name(list_name), task_name)
    return RestRequestGet(query_url).execute()


def get_list_id_by_name(list_name: str):
    if list_name not in list_ids_cached:
        list_id = query_list_id_by_name(list_name)
        list_ids_cached[list_name] = list_id
        return list_id
    else:
        return list_ids_cached[list_name]


def create_list(title: str):
    request = RestRequestPost(api_urls.new_list())
    request["title"] = title
    return request.execute()


def rename_list(old_list_title: str, new_list_title: str):
    request = RestRequestPatch(api_urls.modify_list(get_list_id_by_name(old_list_title)))
    request["title"] = new_list_title
    return request.execute()


def create_task(text: str, folder: str, reminder_datetime: datetime = None):
    todoTaskListId = get_list_id_by_name(folder)

    request = RestRequestPost(api_urls.new_task(todoTaskListId))
    request["title"] = text

    if reminder_datetime is not None:
        request["isReminderOn"] = True
        request["reminderDateTime"] = datetime_to_api_timestamp(reminder_datetime)

    return request.execute()


def query_lists():
    lists = RestRequestGet(api_urls.query_lists()).execute()
    return lists


def get_task_id_by_name(list_name: str, task_name: str):
    try:
        return query_task(list_name, task_name)[0]["id"]
    except IndexError:
        raise Exception(f"Task not found. List: {list_name}, task: {task_name}")


def get_task_id(list_name: str, task_name_or_listpos: Union[str, int]):
    if isinstance(task_name_or_listpos, str):
        return get_task_id_by_name(list_name, task_name_or_listpos)
    elif isinstance(task_name_or_listpos, int):
        tasks = query_tasks(list_name, task_name_or_listpos + 1)
        return tasks[task_name_or_listpos]['id']
    else:
        raise


def complete_task(list_name: str, task_name: Union[str, int]):
    task_id = get_task_id(list_name, task_name)

    url = api_urls.modify_task(get_list_id_by_name(list_name), task_id)

    request = RestRequestPatch(url)
    request["completedDateTime"] = datetime_to_api_timestamp(datetime.now())
    request["status"] = 'completed'
    request.execute()


def remove_task(task_list, param):
    task_id = get_task_id(task_list, param)
    url = api_urls.delete_task(task_list, task_id)
    request = RestRequestDelete(url)
    request.execute()
