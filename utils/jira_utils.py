from models.ticket import *
from utils import utils
import constants


def build_jira_ticket(issue_obj, team_name, jira_client):
    try:
        ticket_id = issue_obj['id']
        ticket_key = issue_obj['key']
        ticket_type = issue_obj['fields']['issuetype']['name']
        if issue_obj['fields']['epic'] is not None:
            ticket_epic = issue_obj['fields']['epic']['name']
        else:
            ticket_epic = None

        if issue_obj['fields']['assignee'] is not None:
            assignee = issue_obj['fields']['assignee']['displayName']
            assignee_email = issue_obj['fields']['assignee']['emailAddress']
        else:
            assignee = None
            assignee_email = None

        ticket_status = issue_obj['fields']['status']['name']
        ticket_summary = issue_obj['fields']['summary']
        ticket_estimation_time = get_estimation_time(issue_obj)
        ticket_last_updated = utils.get_timestamp(issue_obj['fields']['updated'])
        if 'parent' in issue_obj['fields']:
            ticket_parent = issue_obj['fields']['parent']['fields']['summary']
            ticket_parent_id = issue_obj['fields']['parent']['id']
        else:
            ticket_parent = None
            ticket_parent_id = None

        sub_tasks = None
        if 'subtasks' in issue_obj['fields']:
            sub_tasks = []
            for sub_issue_obj in issue_obj['fields']['subtasks']:
                sub_id = sub_issue_obj['id']
                sub_issue_obj = jira_client.get_subtask_details(sub_id)

                sub_key = sub_issue_obj['key']
                sub_name = sub_issue_obj['fields']['summary']
                sub_status = sub_issue_obj['fields']['status']['name']
                sub_type = sub_issue_obj['fields']['issuetype']['name']
                sub_estimation_time = get_estimation_time(sub_issue_obj)
                if sub_issue_obj['fields']['assignee'] is not None:
                    sub_assignee = sub_issue_obj['fields']['assignee']['displayName']
                    sub_assignee_email = sub_issue_obj['fields']['assignee']['emailAddress']
                else:
                    sub_assignee = None
                    sub_assignee_email = None

                if sub_estimation_time is None:
                    sub_estimation_time = 1

                sub_last_update = utils.get_timestamp(sub_issue_obj['fields']['updated'])

                sub_ticket = Ticket(sub_id, sub_key, sub_type, None, sub_assignee, sub_assignee_email, sub_status,
                                    sub_name, sub_estimation_time, sub_last_update, None, None, None, team_name)
                sub_tasks.append(sub_ticket)

        ticket = Ticket(ticket_id, ticket_key, ticket_type, ticket_epic, assignee, assignee_email, ticket_status,
                        ticket_summary,
                        ticket_estimation_time, ticket_last_updated, ticket_parent, ticket_parent_id,
                        sub_tasks, team_name)
    except Exception as exc:
        print(exc)
        return None

    return ticket


def get_estimation_time(json_obj):
    # first check if we story points estimation, if not check if we have timeestimate
    if json_obj['fields'][constants.story_points] is not None:
        return json_obj['fields'][constants.story_points]
    elif json_obj['fields']['timeestimate'] is not None:
        time_estimate = json_obj['fields']['timeestimate']
        return utils.convert_seconds_to_days(time_estimate)

    return 1
