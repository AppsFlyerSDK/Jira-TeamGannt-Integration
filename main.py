import requests
import auth
import utils.time_logger as logger
import json
from models.board import *
from clients.jira_client import *

MAX_RESULTS = 50

jira_client = JiraClient()


def get_jira_tickets():
    # 1. get all boards
    boards = get_boards()
    # 2. for each board get all active sprints
    get_active_sprints(boards)


def get_boards():
    time_logger = logger.TimeLogger()  # log the time it takes to get all the boards
    boards = {}
    start_index = 0

    is_last = False

    # run on all the boards each time increase the starting index until is last is true
    while not is_last:
        resp = jira_client.get_boards_from_jira(start_index)
        json_obj = get_json(resp)

        # extract board details from the json object
        extract_boards_from_json(json_obj, boards)

        is_last = json_obj['isLast']
        start_index = start_index + 50

    print(time_logger.elapsed_time())
    return boards


def get_active_sprints(boards_dict):
    # Iterate on boards dictionary and get board_id
    for board_id in boards_dict:
        # Call JIRA API Endpoint to obtain all the sprints in the board
        url = BASE_URL + "/rest/agile/1.0/board/" + board_id + "/sprint"
        pass


def extract_boards_from_json(obj, boards_dict):
    boards_json = obj['values']
    for board_json in boards_json:
        board_id = board_json['id']
        board_name = board_json['name']
        location_dict = board_json.get('location', {})
        project_name = location_dict.get('projectName', '')
        board = Board(board_id, board_name, project_name)
        boards_dict[str(board_id)] = board


def get_json(resp):
    content = str(resp.content, "utf-8")
    return json.loads(content)


if __name__ == "__main__":
    get_jira_tickets()
