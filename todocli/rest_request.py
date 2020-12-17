import json

from todocli.oauth import get_oauth_session


class RestRequest:
    def __init__(self, url):
        self.url = url

    @staticmethod
    def evaluateResult(o):
        if o.ok:
            return True
        else:
            o.raise_for_status()

    @staticmethod
    def parse_contents(response):
        return json.loads(response.content.decode())["value"]

    def parseResult(self, o):
        self.evaluateResult(o)
        return self.parse_contents(o)

    def execute(self):
        pass


class RestRequestWithBody(RestRequest):
    def __init__(self, url):
        super().__init__(url)
        self.body = {}

    def __setitem__(self, key, value):
        self.body[key] = value

    def addToRequestBody(self, tag, value):
        self.body[tag] = value


class RestRequestGet(RestRequest):
    def execute(self):
        outlook = get_oauth_session()
        o = outlook.get(self.url)
        return self.parseResult(o)


class RestRequestPost(RestRequestWithBody):
    def execute(self):
        outlook = get_oauth_session()
        o = outlook.post(self.url, json=self.body)
        return self.evaluateResult(o)


class RestRequestPatch(RestRequestWithBody):
    def execute(self):
        outlook = get_oauth_session()
        o = outlook.patch(self.url, json=self.body)
        return self.evaluateResult(o)


class RestRequestDelete(RestRequest):
    def execute(self):
        outlook = get_oauth_session()
        o = outlook.delete(self.url)
        return self.evaluateResult(o)
