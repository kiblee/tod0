"""
For implementation details, refer to this source:
https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-1.0
"""
from datetime import datetime


from todocli.rest_request import (
    RestRequestWithBody,
    RestRequestPatch,
    RestRequestPost,
    RestRequestDelete,
)
from todocli.todo_api import api_urls
from todocli.todo_api.exceptions import TaskNotFoundByName
from todocli.todo_api.queries import (
    get_list_id_by_name,
    get_task_id,
    query_tasks,
    query_task,
    query_list,
    query_lists,
)
from todocli.task import Task
from todocli.todo_api.todo_api_util import datetime_to_api_timestamp


class _RestRequestTask:
    def __init__(self, request: RestRequestWithBody):
        self.request = request

    def set_completed(self):
        self.request["completedDateTime"] = datetime_to_api_timestamp(datetime.now())
        self.set_status(Task.Status.Completed)
        return self

    def set_status(self, status: Task.Status):
        self.request["status"] = status.value
        return self

    def set_importance(self, importance: Task.Importance):
        self.request["importance"] = importance.value
        return self

    def set_title(self, title: str):
        self.request["title"] = title
        return self

    def set_reminder(self, reminder_datetime):
        self.request["isReminderOn"] = True
        self.request["reminderDateTime"] = datetime_to_api_timestamp(reminder_datetime)
        return self

    def execute(self):
        return self.request.execute()


class GetTask:
    def __init__(self, list_name, task_name):
        self.list_name = list_name
        self.task_name = task_name

    def execute(self):
        try:
            result = query_task(self.list_name, self.task_name)
            return Task(result)
        except IndexError:
            raise TaskNotFoundByName(self.task_name, self.list_name)


class GetTasks:
    def __init__(self, list_name, include_completed=False, num_tasks=100):
        self.list_name = list_name
        self.include_completed = include_completed
        self.num_tasks = num_tasks

    def execute(self):
        result = query_tasks(self.list_name, self.include_completed, self.num_tasks)
        return [Task(x) for x in result]


class ModifyTask(_RestRequestTask):
    def __init__(self, list_name, task_name):
        url = api_urls.modify_task(
            get_list_id_by_name(list_name), get_task_id(list_name, task_name)
        )
        super().__init__(RestRequestPatch(url))


class CreateTask(_RestRequestTask):
    def __init__(self, list_name, task_name):
        url = api_urls.new_task(get_list_id_by_name(list_name))
        super().__init__(RestRequestPost(url))
        self.set_title(task_name)


class DeleteTask(RestRequestDelete):
    def __init__(self, list_name, task_name):
        url = api_urls.delete_task(
            get_list_id_by_name(list_name), get_task_id(list_name, task_name)
        )
        super().__init__(url)


class _RestRequestList:
    def __init__(self, request: RestRequestWithBody):
        self.request = request

    def set_display_name(self, list_name):
        self.request["displayName"] = list_name
        return self

    def execute(self):
        self.request.execute()


class GetList:
    def __init__(self, list_name):
        self.list_name = list_name

    def execute(self):
        result = query_list(self.list_name)
        return result


class GetLists:
    def execute(self):
        result = query_lists()
        return result


class CreateList(_RestRequestList):
    def __init__(self, list_name):
        url = api_urls.new_list()
        super().__init__(RestRequestPost(url))
        self.set_display_name(list_name)


class ModifyList(_RestRequestList):
    def __init__(self, list_name):
        url = api_urls.modify_list(get_list_id_by_name(list_name))
        super().__init__(RestRequestPatch(url))


class DeleteList(RestRequestDelete):
    def __init__(self, list_name):
        url = api_urls.delete_list(get_list_id_by_name(list_name))
        super().__init__(url)
