import json
import time
import requests
import math
import main
import datetime
from logger import *

reporter = main.reporter


def get_json(resp):
    content = str(resp.content)
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
    elif method == "delete":
        resp = requests.delete(url, headers=headers)
    else:
        raise Exception("Wrong method")

    if resp.status_code == 204:
        print_log("{}\t{}".format(method.upper(), url))
        global reporter
        reporter.add_api_call(method)
        return {}, resp.status_code
    else:
        json_obj = get_json(resp)

    if body is not None:
        print_log("{}\t{}\t{}".format(method.upper(), url, body))
    else:
        print_log("{}\t{}".format(method.upper(), url))

    reporter.add_api_call(method)

    return json_obj, resp.status_code


def create_doc_title():
    now = datetime.now()
    return "Report " + now.strftime("%Y-%m-%d %H:%M")


def write_report():
    print_log_to_file()
    reporter.write_report()


def set_tickets_to_report(new_tickets, need_to_update_tickets):
    reporter.new_tickets = new_tickets
    reporter.update_tickets = need_to_update_tickets


def set_time_elapsed(time_elapsed):
    reporter.time_elapsed = time_elapsed


def format_milli(time_elapsed):
    seconds = (time_elapsed / 1000) % 60
    seconds = int(seconds)
    minutes = (time_elapsed / (1000 * 60)) % 60
    minutes = int(minutes)
    return "{:02d}:{:02d}".format(minutes, seconds)
