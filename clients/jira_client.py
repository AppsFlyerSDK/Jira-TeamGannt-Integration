import auth
import requests

BASE_URL = "https://appsflyer.atlassian.net"


class JiraClient:

    def __init__(self):
        # get encrypted token
        enc_token = auth.getJiraAuthToken().rstrip()
        self.headers = {
            'Authorization': 'Basic ' + enc_token}

    def get_boards_from_jira(self, start_index):
        url = BASE_URL + "/rest/agile/1.0/board?maxResults=50&startAt=" + str(start_index)
        resp = requests.get(url, headers=self.headers)
        print(resp.status_code)
        return resp
