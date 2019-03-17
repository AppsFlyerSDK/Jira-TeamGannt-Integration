import json
import time
import yaml
import requests
from utils.logger import *


def get_json(resp):
    content = str(resp.content, "utf-8")
    return json.loads(content)


def convert_to_datetime(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')


# Db utils
def get_db_config_params():
    with open("config/config.yaml", 'r') as stream:
        try:
            # Load the config yaml file
            yaml_dict = yaml.load(stream)
            db_string = yaml_dict['Db']['ConnectionString']
            db_user = yaml_dict['Db']['user']
            db_password = yaml_dict['Db']['password']
            db_name = yaml_dict['Db']['DbName']
            db_schema = yaml_dict['Db']['DbSchema']
            db_table_name = yaml_dict['Db']['DbTableName']
            return db_string, db_user, db_password, db_name, db_schema, db_table_name
        except yaml.YAMLError as exc:
            print(exc)


def get_timestamp(date):
    return time.mktime(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())


def get_teamgantt_project_id():
    with open("config/config.yaml", 'r') as stream:
        try:
            yaml_dict = yaml.load(stream)
            teamgantt_project_id = yaml_dict['TeamGantt']['projectId']
            return teamgantt_project_id
        except yaml.YAMLError as exc:
            print(exc)


def get_company_id():
    with open("config/config.yaml", 'r') as stream:
        try:
            yaml_dict = yaml.load(stream)
            teamgantt_company_id = yaml_dict['TeamGantt']['companyId']
            return teamgantt_company_id
        except yaml.YAMLError as exc:
            print(exc)


def execute_url(url, method, headers, body=None):
    if method == "get":
        resp = requests.get(url, headers=headers)
    elif method == "post":
        resp = requests.post(url, data=json.dumps(body), headers=headers)
    else:
        raise Exception("Wrong method")

    print_log("{}\t{}".format(method.upper(), url))
    return get_json(resp)
