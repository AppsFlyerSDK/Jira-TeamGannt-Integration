import json
from datetime import datetime


def get_json(resp):
    content = str(resp.content, "utf-8")
    return json.loads(content)


def convert_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
