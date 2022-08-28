from enum import Enum
from todocli.utils.datetime_util import api_timestamp_to_datetime


class TaskStatus(str, Enum):
    COMPLETED = "completed"
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    WAITING_ON_OTHERS = "waitingOnOthers"
    DEFERRED = "deferred"


class TaskImportance(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Task:
    def __init__(self, query_result):
        self.title = query_result["title"]
        self.id = query_result["id"]
        self.importance = TaskImportance(query_result["importance"])
        self.status = TaskStatus(query_result["status"])
        self.created_datetime = api_timestamp_to_datetime(
            query_result["createdDateTime"]
        )

        if "completedDateTime" in query_result:
            self.completed_datetime = api_timestamp_to_datetime(
                query_result["completedDateTime"]
            )
        else:
            self.completed_datetime = None

        self.is_reminder_on: bool = bool(query_result["isReminderOn"])

        if "reminderDateTime" in query_result:
            self.reminder_datetime = api_timestamp_to_datetime(
                query_result["reminderDateTime"]
            )
        else:
            self.reminder_datetime = None

        self.last_modified_datetime = api_timestamp_to_datetime(
            query_result["lastModifiedDateTime"]
        )

        if "bodyLastModifiedDateTime" in query_result:
            self.body_last_modified_datetime = api_timestamp_to_datetime(
                query_result["bodyLastModifiedDateTime"]
            )
        else:
            self.body_last_modified_datetime = None
