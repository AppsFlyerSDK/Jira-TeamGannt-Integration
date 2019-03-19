import utils.time_logger as logger
from config import config
from utils import utils, jira_utils
from models.board import *
from models.sprint import *
from clients.jira_client import *
from clients.teamgantt_client import *
from db import postgreSql
import csv
import sys

MAX_RESULTS = 50
jira_client, teamgantt_client = None, None


def copy_jira_tickets_to_teamgantt():
    time_logger = logger.TimeLogger()  # log the time it takes to get all the boards
    # 1. get all boards
    boards = get_boards()
    # boards = {'181': Board(181, 'UX/UI', 'UX/UI')}

    # 2. for each board get all active sprints and their corresponded tickets
    for board_id in boards:
        get_active_sprints(boards[board_id])

    # 3. compare the tickets we got with our db
    new_tickets, need_to_update_tickets = compare_with_db(boards)

    # 4.1 add the new tickets to TeamGantt
    add_new_tickets_to_teamgantt(new_tickets)
    # 4.2 update the tickets that were changed since last time
    update_tickets_in_teamgantt(need_to_update_tickets)

    # 5. write all tickets to csv to csv
    write_tickets_to_csv(new_tickets)
    # 6. copy csv into our db
    postgreSql.copy_csv_into_db()

    print(time_logger.elapsed_time())


def update_tickets_in_teamgantt(need_to_update_tickets):
    for ticket in need_to_update_tickets:
        teamgantt_client.update_task(ticket)
        postgreSql.update_ticket_timestamp(str(ticket.ticket_jira_id), str(ticket.ticket_jira_last_update))


def add_new_tickets_to_teamgantt(new_tickets):
    teamgantt_client.update_resources()

    for ticket in new_tickets:
        # insert to teamgantt each ticket
        teamgantt_client.create_task(ticket)


# Connect to PostgreSql and compare the extracted tickets with our db
def compare_with_db(boards):
    teamgantt_tickets_to_add = []
    teamgantt_tickets_to_update = []

    tickets = dict(postgreSql.get_tickets_from_db())

    # iterate on all the jira tickets from the active sprints
    for board_id in boards:
        board = boards[board_id]
        for sprint_id in board.sprints:
            sprint = board.sprints[sprint_id]
            for ticket_id in sprint.tickets:
                ticket = sprint.tickets[ticket_id]
                # Check if the ticket is in our db
                try:
                    if ticket_id in tickets:
                        print(ticket_id)
                        # Check if the ticket was changed since last time
                        if ticket.ticket_jira_last_update > float(tickets[ticket_id]['jira_last_update']):
                            ticket.teamgantt_id = tickets[ticket_id]['teamgantt_id']
                            teamgantt_tickets_to_update.append(ticket)
                    else:
                        # Ticket is not written in our db. add to teamgantt list
                        teamgantt_tickets_to_add.append(ticket)
                except Exception as exc:
                    print(exc)

    return teamgantt_tickets_to_add, teamgantt_tickets_to_update


def write_tickets_to_csv(teamgantt_tickets):
    with open('gantt_ticket.csv', mode='w') as gantt_csv:
        teamgantt_ticket_writer = csv.writer(gantt_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for teamgantt_ticket in teamgantt_tickets:
            teamgantt_ticket_writer.writerow(
                [teamgantt_ticket.ticket_jira_id, teamgantt_ticket.teamgantt_id,
                 teamgantt_ticket.ticket_jira_last_update])


def get_boards():
    boards = {}
    start_index = 0

    is_last = False

    # run on all the boards each time increase the starting index until is last is true
    while not is_last:
        json_obj = jira_client.get_boards_from_jira(start_index)

        # extract board details from the json object
        extract_boards_from_json(json_obj, boards)

        is_last = json_obj['isLast']
        start_index = start_index + 50

    return boards


def get_tickets_from_sprint(sprint, board_id, team_name):
    json_obj = jira_client.get_tickets_from_sprint(sprint.sprint_id, board_id)
    tickets = {}
    for issue_obj in json_obj['issues']:
        ticket = jira_utils.build_jira_ticket(issue_obj, team_name, jira_client)
        if ticket is not None:
            tickets[ticket.ticket_jira_id] = ticket

    return tickets


def get_active_sprints(board):
    start_index = 0
    # Get all the relevant sprints of the board
    json_obj, status_code = jira_client.get_sprints_from_jira(board.board_id, start_index)
    # If the board support sprints the status board will be 200
    is_last = False
    if status_code != 200:
        return
    while not is_last:
        # iterate on all the active sprints
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
                is_active = sprint.is_sprint_active() and sprint_state == 'active'
                print("Board id: " + str(board.board_id) + "\tsprint id: " + str(sprint_id) + " - " + str(is_active))
                if is_active:
                    teamgantt_client.set_sprint_start_date(sprint.sprint_start_date)
                    # Get all the tickets of the current sprint
                    sprint.tickets = get_tickets_from_sprint(sprint, board.board_id, board.board_name)
                    board.sprints[sprint_id] = sprint

            except Exception as exc:
                print(exc)

        start_index = start_index + MAX_RESULTS
        # Get the next 50 sprints
        json_obj, _ = jira_client.get_sprints_from_jira(board.board_id, start_index)


def extract_boards_from_json(obj, boards_dict):
    boards_json = obj['values']
    for board_json in boards_json:
        board_id = board_json['id']
        if board_id == 168:
            continue  # Ignore this specific board

        board_name = board_json['name']
        location_dict = board_json.get('location', {})
        project_name = location_dict.get('projectName', '')
        board = Board(board_id, board_name, project_name)
        boards_dict[str(board_id)] = board


def init():
    global jira_client, teamgantt_client

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config.init_config_parameters(config_file)
    else:
        print("no config file was set - exiting program...")
        sys.exit()

    jira_client = JiraClient()
    teamgantt_client = TeamGanttClient()


if __name__ == "__main__":
    init()
    copy_jira_tickets_to_teamgantt()
