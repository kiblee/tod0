from enum import Enum


class TodoList:
    class WellKnownListName(Enum):
        none = "none"
        DefaultList = "defaultList"
        FlaggedEmails = "flaggedEmails"

    def __init__(self, query_result_list):
        self.id: str = query_result_list["id"]
        self.display_name: str = query_result_list["displayName"]
        self.is_owner = bool(query_result_list["isOwner"])
        self.is_shared = bool(query_result_list["isShared"])
        self.well_known_list_name = TodoList.WellKnownListName(
            query_result_list["wellknownListName"]
        )
