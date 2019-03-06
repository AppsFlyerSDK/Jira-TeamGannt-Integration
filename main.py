import utils.time_logger as logger
import utils.utils as utils
from models.board import *
from models.sprint import *
from clients.jira_client import *
from clients.teamgantt_client import *

MAX_RESULTS = 50

jira_client = JiraClient()
TeamGanttClient = TeamGanttClient()


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
        json_obj = utils.get_json(resp)

        # extract board details from the json object
        extract_boards_from_json(json_obj, boards)

        is_last = json_obj['isLast']
        start_index = start_index + 50

    print(time_logger.elapsed_time())
    return boards


def get_active_sprints(boards_dict):
    # Iterate on boards dictionary and get board_id
    for board_id in boards_dict:
        start_index = 0
        # Get all the relevant sprints of the board
        resp = jira_client.get_sprints_from_jira(board_id, start_index)
        # If the board support sprints the status board will be 200
        if resp.status_code == 200:
            while True:
                # iterate on all the active sprints
                json_obj = utils.get_json(resp)
                is_last = json_obj['isLast']
                for sprint_json in json_obj['values']:
                    # get sprint details
                    try:
                        sprint_state = sprint_json['state']
                        if sprint_state == 'future':
                            continue
                        sprint_id = sprint_json['id']
                        start_date_str = sprint_json['startDate']
                        end_date_str = sprint_json['endDate']

                        start_date = utils.convert_to_datetime(start_date_str)
                        end_date = utils.convert_to_datetime(end_date_str)

                        sprint = Sprint(sprint_id, start_date, end_date)
                        is_active = sprint.is_sprint_active()
                        print("Board id: " + board_id + "\tsprint id: " + str(sprint_id) + " - " + str(is_active))
                        if is_active:
                            print('active')
                    except Exception as exc:
                        print(exc)

                if is_last:
                    break
                start_index = start_index + 50
                # Get the next 50 sprints
                resp = jira_client.get_sprints_from_jira(board_id, start_index)


def extract_boards_from_json(obj, boards_dict):
    boards_json = obj['values']
    for board_json in boards_json:
        board_id = board_json['id']
        board_name = board_json['name']
        location_dict = board_json.get('location', {})
        project_name = location_dict.get('projectName', '')
        board = Board(board_id, board_name, project_name)
        boards_dict[str(board_id)] = board


if __name__ == "__main__":
    get_jira_tickets()
