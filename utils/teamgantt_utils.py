from datetime import datetime, timedelta
from utils import utils


def create_task_payload(ticket, parent_group_id=-1, project_id=-1):
    name = ticket.ticket_summary
    percent_complete = determine_percent_complete(ticket.ticket_status)
    color = determine_task_color(ticket.ticket_type)
    type = 'task'
    start_date = ''
    end_date = ''

    task_payload = {'name': name,
                    'percent_complete': percent_complete,
                    'color': color,
                    'type': type}

    if parent_group_id != -1:
        task_payload['parent_group_id'] = parent_group_id

    if project_id != -1:
        task_payload['project_id'] = project_id

    return task_payload


def calculate_end_date(start_date_str, ticket_estimation_time):
    if ticket_estimation_time is None:
        ticket_estimation_time = 1

    if type(start_date_str) is datetime:
        start_date_str = utils.convert_to_teamgantt_date_format(start_date_str)

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=ticket_estimation_time - 1)
    cur_date = end_date + timedelta(days=1)
    end_date_str = utils.convert_to_teamgantt_date_format(end_date)
    cur_date_str = utils.convert_to_teamgantt_date_format(cur_date)
    return end_date_str, cur_date_str


def add_time_to_task(task_payload, task):
    start_date = task.resource.cur_date
    end_date, cur_date = calculate_end_date(start_date, task.ticket_estimation_time)
    task.resource.cur_date = cur_date

    task_payload['start_date'] = start_date
    task_payload['end_date'] = end_date

    return task_payload


def determine_percent_complete(ticket_status):
    if ticket_status.lower() == 'review':
        return 100
    if ticket_status.lower() == 'closed':
        return 100
    if ticket_status.lower() == 'done':
        return 100
    if ticket_status.lower() == 'test':
        return 70
    if ticket_status.lower() == 'in progress':
        return 30
    if ticket_status.lower() == 'backlog':
        return 0
    if ticket_status.lower() == 'on hold':
        return 0
    else:
        return 0


def determine_task_color(ticket_type):
    if ticket_type.lower() == 'bug':  # Bug (INT R&D)
        return 'yellow1'
    if ticket_type.lower() == 'technical story':
        return 'purple1'
    if ticket_type.lower() == 'bug (int r&d)':
        return 'green1'
    return 'blue1'
