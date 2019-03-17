import auth
from utils import utils

BASE_URL = "https://appsflyer.atlassian.net"


class JiraClient:

    def __init__(self):
        # get encrypted token
        self.header = set_auth_header()

    def get_boards_from_jira(self, start_index):
        url = BASE_URL + "/rest/agile/1.0/board?maxResults=50&startAt=" + str(start_index)
        return utils.execute_url(url=url, method="get", headers=self.header)

    def get_sprints_from_jira(self, board_id, start_index):
        # Call JIRA API Endpoint to obtain all the sprints in the board
        url = BASE_URL + "/rest/agile/1.0/board/" + board_id + "/sprint?maxResults=50&startAt=" + str(start_index)
        return utils.execute_url(url=url, method="get", headers=self.header)

    def get_tickets_from_sprint(self, sprint_id, board_id):
        url = BASE_URL + "/rest/agile/1.0/board/" + str(board_id) + "/issue?jql=sprint=" + str(sprint_id)
        return utils.execute_url(url=url, method="get", headers=self.header)


def set_auth_header():
    enc_token = auth.get_jira_auth_token().rstrip()
    return {
        'Authorization': 'Basic ' + enc_token}
