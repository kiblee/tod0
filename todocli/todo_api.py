"""
For implementation details, refer to this source:
https://docs.microsoft.com/de-de/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime

from todocli import api_urls
from todocli.rest_request import RestRequestGet, RestRequestPost, RestRequestPatch
from todocli.todo_api_util import datetimeToApiTimestamp

class Folders:
    # Cache folders
    folders_raw = {}
    name2id = {}
    id2name = {}


def query_tasks(list_name: str, num_tasks: int = 100):
    query_url = api_urls.queryTasksFromList(getListIdByName(list_name), num_tasks)
    return RestRequestGet(query_url).execute()


def getListIdByName(folder_name: str):
    return Folders.name2id[folder_name]


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


def list_and_cache_folders():
    folders = RestRequestGet(api_urls.queryLists()).execute()

    Folders.folders_raw = folders
    for f in folders:
        Folders.name2id[f["displayName"]] = f["id"]
        Folders.id2name[f["id"]] = f["displayName"]

    return True


def getTaskId(list_name: str, task_name: str):
    # todo this might fail when the task list contains of more than 100 tasks
    tasks = query_tasks(list_name, 100)
    task = next(x for x in tasks if x["title"] == task_name)
    return task["id"]

def complete_task(list_name: str, task_name: str):
    task_id = getTaskId(list_name, task_name)

    url = api_urls.modifyTask(getListIdByName(list_name), task_id)

    request = RestRequestPatch(url)
    request["completedDateTime"] = datetimeToApiTimestamp(datetime.now())
    request["status"] = 'completed'
    request.execute()