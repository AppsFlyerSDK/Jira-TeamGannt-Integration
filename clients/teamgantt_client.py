import auth
import requests
import json
import utils.utils as utils

BASE_URL = "https://api.teamgantt.com/v1"


class TeamGanttClient:
    def __init__(self):
        self.headers = set_auth_header()


def set_auth_header():
    app_token, email, password = auth.get_teamgantt_auth_token()
    header = {'Content-Type': 'application/json',
              'TG-Authorization': 'Bearer ' + app_token}
    auth_payload = {'user': email, 'pass': str(password)}

    # send app_token to get api token and user token (create session)
    url = BASE_URL + "/authenticate"
    resp = requests.post(url, data=json.dumps(auth_payload), headers=header)

    # extract session api and user token
    json_obj = utils.get_json(resp)
    api_key = json_obj['api_key']
    user_token = json_obj['user_token']

    return {'TG-Authorization': 'Bearer ' + app_token,
            'TG-Api-Key': api_key,
            'TG-User-Token': user_token}
