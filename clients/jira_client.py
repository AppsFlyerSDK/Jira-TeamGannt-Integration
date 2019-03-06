import auth
import requests
from utils.logger import *

BASE_URL = "https://appsflyer.atlassian.net"


class JiraClient:

    def __init__(self):
        # get encrypted token
        self.header = set_auth_header()
        self.logger = Logger('JiraClient')

    def get_boards_from_jira(self, start_index):
        url = BASE_URL + "/rest/agile/1.0/board?maxResults=50&startAt=" + str(start_index)
        self.logger.print_log(url);
        resp = requests.get(url, headers=self.header)
        print(resp.status_code)
        return resp

    def get_sprints_from_jira(self, board_id, start_index):
        # Call JIRA API Endpoint to obtain all the sprints in the board
        url = BASE_URL + "/rest/agile/1.0/board/" + board_id + "/sprint?maxResults=50&startAt=" + str(start_index)
        self.logger.print_log(url);
        resp = requests.get(url, headers=self.header)
        return resp


def set_auth_header():
    enc_token = auth.get_jira_auth_token().rstrip()
    return {
        'Authorization': 'Basic ' + enc_token}
