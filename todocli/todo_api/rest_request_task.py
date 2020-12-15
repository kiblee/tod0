from datetime import datetime

from todocli import api_urls
from todocli.rest_request import (
    RestRequestWithBody,
    RestRequestPatch,
    RestRequestDelete,
    RestRequestPost,
)
from todocli.todo_api.querys import get_list_id_by_name, get_task_id
from todocli.todo_api.todo_api_util import datetime_to_api_timestamp
from todocli.task import Task


class _RestRequestTask:
    def __init__(self):
        self.request: RestRequestWithBody = None

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


class RestRequestTaskDelete(RestRequestDelete):
    def __init__(self, list_name, task_name):
        url = api_urls.delete_task(
            get_list_id_by_name(list_name), get_task_id(list_name, task_name)
        )
        super().__init__(url)
