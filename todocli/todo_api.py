"""
For implementation details, refer to this source:
https://docs.microsoft.com/de-de/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime
from typing import Union

from todocli import api_urls
from todocli.rest_request import RestRequestGet, RestRequestPost, RestRequestPatch
from todocli.todo_api_util import datetimeToApiTimestamp

list_ids_cached = {}

def queryListIdByName(list_name):
    url = api_urls.queryLists()+"?$filter=startswith(displayName,'{}')".format(list_name)
    res = RestRequestGet(url).execute()

    return res[0]['id']


def query_tasks(list_name: str, num_tasks: int = 100):
    query_url = api_urls.queryTasksFromList(getListIdByName(list_name), num_tasks)
    return RestRequestGet(query_url).execute()


def query_task(list_name: str, task_name: str):
    query_url = api_urls.queryTaskByName(getListIdByName(list_name), task_name)
    return RestRequestGet(query_url).execute()


def getListIdByName(list_name: str):
    if list_name not in list_ids_cached:
        id = queryListIdByName(list_name)
        list_ids_cached[list_name] = id
        return id
    else:
        return list_ids_cached[list_name]


def create_list(title: str):
    request = RestRequestPost(api_urls.newList())
    request["title"] = title
    return request.execute()


def rename_list(old_list_title: str, new_list_title: str):
    request = RestRequestPatch(api_urls.modifyList(getListIdByName(old_list_title)))
    request["title"] = new_list_title
    return request.execute()


def create_task(text: str, folder: str, reminder_datetime : datetime = None):
    todoTaskListId = getListIdByName(folder)

    request = RestRequestPost(api_urls.newTask(todoTaskListId))
    request["title"] = text

    if reminder_datetime is not None:
        request["isReminderOn"] = True
        request["reminderDateTime"] = datetimeToApiTimestamp(reminder_datetime)

    return request.execute()


def query_lists():
    lists = RestRequestGet(api_urls.queryLists()).execute()
    return lists


def getTaskIdByName(list_name: str, task_name: str):
    try:
        return query_task(list_name, task_name)[0]["id"]
    except IndexError:
        raise Exception(f"Task not found. List: {list_name}, task: {task_name}")


def getTaskId(list_name: str, task_name_or_listpos: Union[str, int]):
    if isinstance(task_name_or_listpos, str):
        return getTaskIdByName(list_name, task_name_or_listpos)
    elif isinstance(task_name_or_listpos, int):
        tasks = query_tasks(list_name, task_name_or_listpos+1)
        return tasks[task_name_or_listpos]['id']
    else:
        raise


def complete_task(list_name: str, task_name: Union[str,int]):
    task_id = getTaskId(list_name, task_name)

    url = api_urls.modifyTask(getListIdByName(list_name), task_id)

    request = RestRequestPatch(url)
    request["completedDateTime"] = datetimeToApiTimestamp(datetime.now())
    request["status"] = 'completed'
    request.execute()


def remove_task(task_list, param):
    task_id = getTaskId(task_list, param)
    api_urls.deleteTask(task_list, task_id)
    return None
