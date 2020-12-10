from todocli.oauth import getOAuthSession
from todocli.parse_contents import parse_contents


class RestRequest:
    def __init__(self, url):
        self.url = url


class RestRequestGet(RestRequest):
    def execute(self):
        outlook = getOAuthSession()
        o = outlook.get(self.url)
        if o.ok:
            result = parse_contents(o)
            return result
        else:
            o.raise_for_status()


class RestRequestWithBody(RestRequest):
    def __init__(self, url):
        super().__init__(url)
        self.body = {}

    def __setitem__(self, key, value):
        self.body[key] = value

    def addToRequestBody(self, tag, value):
        self.body[tag] = value
        

class RestRequestPost(RestRequestWithBody):
    def execute(self):
        outlook = getOAuthSession()
        o = outlook.post(self.url, json=self.body)
        if o.ok:
            return True
        else:
            o.raise_for_status()


class RestRequestPatch(RestRequestWithBody):
    def execute(self):
        outlook = getOAuthSession()
        o = outlook.patch(self.url, json=self.body)
        if o.ok:
            return True
        else:
            o.raise_for_status()