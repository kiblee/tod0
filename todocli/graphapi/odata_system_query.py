from enum import Enum


class ODataSystemQuery:
    class Format(Enum):
        json = "json"
        atom = "atom"
        xml = "xml"

    class SortOrder(Enum):
        Ascending = "asc"
        Descending = "desc"

    def add_to_query(self, expr):
        if len(self.query_expr) == 1:
            self.query_expr += expr
        else:
            self.query_expr += "&" + expr

    def __init__(self):
        self.query_expr = "?"

    def count(self):
        self.add_to_query("$count=true")
        return self

    def expand(self, expr):
        self.add_to_query("$expand={}".format(expr))
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
        self.add_to_query("$filter={}".format(expr))
        return self

    def format(self, ftmat: Format):
        self.add_to_query("$format={}".format(ftmat.value))
        return self

    def orderBy(self, expr, sort_order: SortOrder = SortOrder.Ascending):
        self.add_to_query("$orderby={} {}".format(expr, sort_order.value))
        return self

    def search(self, expr):
        raise Exception("Not implemented")

    def select(self, expr):
        raise Exception("Not implemented")

    def skip(self, expr):
        raise Exception("Not implemented")

    def top(self, num_elements):
        self.add_to_query("$top={}".format(num_elements))
        return self

    def get(self):
        if self.query_expr == "?":
            return ""
        return self.query_expr
