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

    def addToQuery(self, expr):
        if len(self.query_expr) == 1:
            self.query_expr += expr
        else:
            self.query_expr += "&" + expr

    def __init__(self):
        self.query_expr = "?"

    def count(self):
        self.addToQuery("$count=true")
        return self

    def expand(self, expr):
        self.addToQuery("$expand={}".format(expr))
        return self

    def filter_startsWith(self, property_name, expr):
        self.filter("startsWith({},'{}')".format(property_name, expr))
        return self

    def filter_endsWith(self, property_name, expr):
        self.filter("endsWith({},'{}')".format(property_name, expr))
        return self

    def _filter_compare(self, property_name, comparison, expr):
        self.filter("{} {} '{}'".format(property_name, comparison, expr))
        return self

    def filter_eq(self, property_name, expr):
        self._filter_compare(property_name, "eq", expr)
        return self

    def filter_ne(self, property_name, expr):
        self._filter_compare(property_name, "ne", expr)
        return self

    def filter_gt(self, property_name, expr):
        self._filter_compare(property_name, "gt", expr)
        return self

    def filter_ge(self, property_name, expr):
        self._filter_compare(property_name, "ge", expr)
        return self

    def filter_lt(self, property_name, expr):
        self._filter_compare(property_name, "lt", expr)
        return self

    def filter_le(self, property_name, expr):
        self._filter_compare(property_name, "le", expr)
        return self

    def filter(self, expr):
        self.addToQuery("$filter={}".format(expr))
        return self

    def format(self, ftmat: Format):
        self.addToQuery("$format={}".format(ftmat.value))
        return self

    def orderBy(self, expr, sort_order: SortOrder = SortOrder.Ascending):
        self.addToQuery("$orderby={} {}".format(expr, sort_order.value))
        return self

    def search(self, expr):
        raise Exception("Not implemented")

    def select(self, expr):
        raise Exception("Not implemented")

    def skip(self, expr):
        raise Exception("Not implemented")

    def top(self, num_elements):
        self.addToQuery("$top={}".format(num_elements))
        return self

    def get(self):
        if self.query_expr == "?":
            return ""
        return self.query_expr


def newTask(todo_task_list_id):
    return "{}/lists/{}/tasks".format(base_api_url, todo_task_list_id)


def newList():
    return "{}/lists".format(base_api_url)


def queryLists():
    return newList()


def modifyList(todo_task_list_id):
    return "{}/lists/{}".format(base_api_url, todo_task_list_id)


def modifyTask(todo_task_list_id, task_id):
    return "{}/lists/{}/tasks/{}".format(base_api_url, todo_task_list_id, task_id)


def queryTasksFromList(todo_task_list_id, num_tasks: int):
    return newTask(todo_task_list_id) + ODataSystemQuery().filter_ne("status", "completed").top(num_tasks).get()


def queryTaskByName(todo_task_list_id, task_name: str):
    return newTask(todo_task_list_id) + ODataSystemQuery().filter_eq("title", task_name).get()


def deleteTask(todo_task_list_id, task_id):
    return modifyTask(todo_task_list_id, task_id)
