import json
import time
import requests
import math
from utils.logger import *


def get_json(resp):
    content = str(resp.content, "utf-8")
    return json.loads(content)


def convert_to_teamgantt_date_format(date):
    return date.strftime('%Y-%m-%d')


def convert_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def convert_seconds_to_days(seconds):
    return math.ceil(seconds / 60 / 60 / 8)


def get_timestamp(date):
    return time.mktime(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())


def execute_url(url, method, headers, body=None):
    if method == "get":
        resp = requests.get(url, headers=headers)
    elif method == "post":
        resp = requests.post(url, data=json.dumps(body), headers=headers)
    elif method == "patch":
        resp = requests.patch(url, data=json.dumps(body), headers=headers)
    else:
        raise Exception("Wrong method")

    json_obj = get_json(resp)

    print_log("{}\t{}\t{}".format(method.upper(), url, body))

    return json_obj, resp.status_code
