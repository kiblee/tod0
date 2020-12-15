from todocli import api_urls
from todocli.rest_request import RestRequestPatch, RestRequestPost, RestRequestWithBody
from todocli.todo_api.querys import get_list_id_by_name


class _RestRequestList:
    def __init__(self):
        self.request: RestRequestWithBody = None

    def set_display_name(self, list_name):
        self.request["displayName"] = list_name

    def execute(self):
        self.request.execute()


class RestRequestListModify(_RestRequestList):
    def __init__(self, list_name):
        super().__init__()

        url = api_urls.modify_list(get_list_id_by_name(list_name))
        self.request = RestRequestPatch(url)


class RestRequestListNew(_RestRequestList):
    def __init__(self, list_name):
        super().__init__()

        url = api_urls.new_list()
        self.request = RestRequestPost(url)
        self.set_display_name(list_name)
