import json


def parse_contents(response):
    return json.loads(response.content.decode())["value"]