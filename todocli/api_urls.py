from enum import Enum

base_api_url = "https://graph.microsoft.com/v1.0/me/todo"


class ODataSystemQuery:
    class Format(Enum):
        json = "json"
        atom = "atom"
        xml = "xml"

    class SortOrder(Enum):
        Ascending = "asc"
        Descending = "desc"

    def __init__(self):
        self.query_expr = "?"

    def count(self):
        self.query_expr += "$count=true"
        return self

    def expand(self, expr):
        self.query_expr += "$expand={}".format(expr)
        return self

    def filter_startsWith(self, propertyName, expr):
        self.filter("startsWith({},'{}')".format(propertyName, expr))
        return self

    def filter_endsWith(self, propertyName, expr):
        self.filter("endsWith({},'{}')".format(propertyName, expr))
        return self

    def _filter_compare(self, propertyName, comparison, expr):
        self.filter("{} {} '{}'".format(propertyName, comparison, expr))
        return self

    def filter_eq(self, propertyName, expr):
        self._filter_compare(propertyName,"eq",expr)
        return self

    def filter_ne(self, propertyName, expr):
        self._filter_compare(propertyName, "ne", expr)
        return self

    def filter_gt(self, propertyName, expr):
        self._filter_compare(propertyName, "gt", expr)
        return self

    def filter_ge(self, propertyName, expr):
        self._filter_compare(propertyName, "ge", expr)
        return self

    def filter_lt(self, propertyName, expr):
        self._filter_compare(propertyName, "lt", expr)
        return self

    def filter_le(self, propertyName, expr):
        self._filter_compare(propertyName, "le", expr)
        return self

    def filter(self, expr):
        self.query_expr += "$filter={}".format(expr)
        return self

    def format(self, expr, ftmat: Format):
        self.query_expr += "$format={}".format(ftmat.value)
        return self

    def orderBy(self, expr, sort_order : SortOrder = SortOrder.Ascending):
        self.query_expr += "$orderby={} {}".format(expr, sort_order.value)
        return self

    def search(self, expr):
        raise Exception("Not implemented")

    def select(self, expr):
        raise Exception("Not implemented")

    def skip(self, expr):
        raise Exception("Not implemented")

    def top(self, num_elements):
        self.query_expr += "$top={}".format(num_elements)
        return self

    def get(self):
        if self.query_expr == "?":
            return ""
        return self.query_expr


def newTask(todoTaskListId):
    return "{}/lists/{}/tasks".format(base_api_url, todoTaskListId)


def newList():
    return "{}/lists".format(base_api_url)


def queryLists():
    return newList()


def modifyList(todoTaskListId):
    return "{}/lists/{}".format(base_api_url, todoTaskListId)


def modifyTask(todoTaskListId, taskId):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todoTaskListId, taskId)


def queryTasksFromList(todoTaskListId, num_tasks: int):
    return newTask(todoTaskListId) + ODataSystemQuery().filter_ne("status", "completed").top(num_tasks).get()


def queryTaskByName(todoTaskListId, task_name: str):
    return newTask(todoTaskListId) + ODataSystemQuery().filter_eq("title", task_name).get()


def modifyTask(todoTaskListId, taskId):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todoTaskListId, taskId)


def deleteTask(todoTaskListId, taskId):
    return modifyTask(todoTaskListId, taskId)
