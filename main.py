import utils.time_logger as logger
import utils.utils as utils
from models.board import *
from models.ticket import *
from models.sprint import *
from models.teamgantt_ticket import *
from clients.jira_client import *
from clients.teamgantt_client import *
import constants
from db import postgreSql
import csv

MAX_RESULTS = 50

jira_client = JiraClient()
teamgantt_client = TeamGanttClient()


def add_new_tickets_to_teamgantt(new_tickets):
    for ticket in new_tickets:
        # insert to teamgantt each ticket
        json_obj = teamgantt_client.create_task(ticket)

        if 'error' in json_obj:
            continue

        # Add the task id to the teamgantt ticket
        teamgantt_task_id = json_obj['id']
        ticket.add_teamgantt_id(teamgantt_task_id)

        # Add resource to task (the assignee)
        teamgantt_client.add_resource_to_task(ticket)


# Connect to PostgreSql and compare the extracted tickets with our db
def compare_with_db(boards):
    teamgantt_tickets_to_add = []
    rows_to_add_to_db = []

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
                    else:
                        # Ticket is not written in our db. add to teamgantt dict
                        ticket_to_add = TeamganttTicket(board.board_name, ticket.ticket_epic, ticket.ticket_summary,
                                                        ticket.ticket_summary, ticket.assignee, ticket.assignee_email,
                                                        ticket.ticket_estimation_time, ticket.ticket_status, ticket_id,
                                                        ticket.ticket_last_update)
                        teamgantt_tickets_to_add.append(ticket_to_add)
                except Exception as exc:
                    print(exc)

    return teamgantt_tickets_to_add


def push_tickets_to_gantt(boards):
    for board_id in boards:
        board = boards[board_id]
        for sprint_id in board.sprints:
            sprint = board.sprints[sprint_id]
            for ticket_id in sprint.tickets:
                pass


def write_tickets_to_csv(teamgantt_tickets):
    with open('gantt_ticket.csv', mode='w') as gantt_csv:
        teamgantt_ticket_writer = csv.writer(gantt_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for teamgantt_ticket in teamgantt_tickets:
            teamgantt_ticket_writer.writerow(
                [teamgantt_ticket.ticket_jira_id, teamgantt_ticket.task_id, teamgantt_ticket.ticket_jira_last_update])


def get_jira_tickets():
    time_logger = logger.TimeLogger()  # log the time it takes to get all the boards
    # 1. get all boards
    # boards = get_boards()
    boards = {}
    boards['173'] = Board(173, "sdk", "sdk-scrum")
    # 2. for each board get all active sprints and their corresponded tickets
    get_active_sprints(boards)

    print(time_logger.elapsed_time())
    # 3. compare the tickets we got with our db
    new_tickets = compare_with_db(boards)
    # 4. add the new tickets to TeamGantt
    add_new_tickets_to_teamgantt(new_tickets)
    # 5. write all tickets to csv to csv
    write_tickets_to_csv(new_tickets)
    # 6. copy csv into our db
    postgreSql.copy_csv_into_db()


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


def get_tickets_from_sprint(sprint_id, board_id):
    json_obj = jira_client.get_tickets_from_sprint(sprint_id, board_id)
    tickets = {}
    for issue_obj in json_obj['issues']:
        try:
            ticket_id = issue_obj['id']
            ticket_key = issue_obj['key']
            ticket_type = issue_obj['fields']['issuetype']['name']
            if issue_obj['fields']['epic'] is not None:
                ticket_epic = issue_obj['fields']['epic']['name']
            else:
                # Get only tickets with epic!
                continue

            if issue_obj['fields']['assignee'] is not None:
                assignee = issue_obj['fields']['assignee']['displayName']
                assignee_email = issue_obj['fields']['assignee']['emailAddress']
            else:
                assignee = None
                assignee_email = None

            ticket_status = issue_obj['fields']['status']['name']
            ticket_summary = issue_obj['fields']['summary']
            ticket_estimation_time = issue_obj['fields'][constants.story_points]
            ticket_last_updated = utils.get_timestamp(issue_obj['fields']['updated'])
            if 'parent' in issue_obj['fields']:
                ticket_parent = issue_obj['fields']['parent']['fields']['summary']
                ticket_parent_id = issue_obj['fields']['parent']['id']
            else:
                ticket_parent = None
                ticket_parent_id = None

            ticket = Ticket(ticket_id, ticket_key, ticket_type, ticket_epic, assignee, assignee_email, ticket_status,
                            ticket_summary,
                            ticket_estimation_time, ticket_last_updated, ticket_parent, ticket_parent_id)
            tickets[ticket_id] = ticket
        except Exception as exc:
            print(exc)

    return tickets


def get_active_sprints(boards_dict):
    # Iterate on boards dictionary and get board_id
    for board_id in boards_dict:
        start_index = 0
        # Get all the relevant sprints of the board
        json_obj = jira_client.get_sprints_from_jira(board_id, start_index)
        # If the board support sprints the status board will be 200
        is_last = False
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
                    print("Board id: " + board_id + "\tsprint id: " + str(sprint_id) + " - " + str(is_active))
                    if is_active:
                        # Get all the tickets of the current sprint
                        sprint.tickets = get_tickets_from_sprint(sprint_id, board_id)
                        boards_dict[board_id].sprints[sprint_id] = sprint

                except Exception as exc:
                    print(exc)

            start_index = start_index + MAX_RESULTS
            # Get the next 50 sprints
            json_obj = jira_client.get_sprints_from_jira(board_id, start_index)


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
