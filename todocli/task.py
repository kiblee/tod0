from datetime import datetime
from enum import Enum

from todocli.todo_api_util import api_timestamp_to_datetime


class Task:
    class Status(Enum):
        Completed = "completed"
        NotStarted = "notStarted"
        InProgress = "inProgress"
        WaitingOnOthers = "waitingOnOthers"
        Deferred = "deferred"

    class Importance(Enum):
        Low = "low"
        Normal = "normal"
        High = "high"

    def __init__(self, query_result_task):
        self.title: str = query_result_task["title"]
        self.id: str = query_result_task["id"]
        self.importance: Task.Importance = Task.Importance(
            query_result_task["importance"]
        )
        self.status: Task.Status = Task.Status(query_result_task["status"])
        self.created_datetime: datetime = api_timestamp_to_datetime(
            query_result_task["createdDateTime"]
        )

        if "completedDateTime" in query_result_task:
            self.completed_datetime: datetime = api_timestamp_to_datetime(
                query_result_task["completedDateTime"]
            )
        else:
            self.completed_datetime = None

        self.is_reminder_on: bool = bool(query_result_task["isReminderOn"])

        if "reminderDateTime" in query_result_task:
            self.reminder_datetime: datetime = api_timestamp_to_datetime(
                query_result_task["reminderDateTime"]
            )
        else:
            self.reminder_datetime = None

        self.last_modified_datetime: datetime = api_timestamp_to_datetime(
            query_result_task["lastModifiedDateTime"]
        )

        if "bodyLastModifiedDateTime" in query_result_task:
            self.body_last_modified_datetime: datetime = api_timestamp_to_datetime(
                query_result_task["bodyLastModifiedDateTime"]
            )
        else:
            self.body_last_modified_datetime = None
