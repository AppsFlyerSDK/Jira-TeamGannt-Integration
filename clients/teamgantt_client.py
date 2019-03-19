import auth
import utils.utils as utils
import config.config as config
from models.resource import *
from utils import teamgantt_utils

BASE_URL = "https://api.teamgantt.com/v1"


class TeamGanttClient:
    def __init__(self):
        self.headers = set_auth_header()
        self.project_id = config.teamgantt_project_id
        self.resources = self.get_resources()
        self.groups = self.get_groups()
        self.sprint_start_date = None

    def create_task(self, ticket, group_id=-1):
        url = BASE_URL + "/tasks"

        if group_id != -1:
            # It's a subtask
            task_payload = teamgantt_utils.create_task_payload(ticket, parent_group_id=group_id,
                                                               project_id=self.project_id)
            self.add_task_and_resource_to_teamgantt(task_payload, ticket, url)
            return
        else:
            # Get group id
            if ticket.team_name in self.groups:
                # Group already created
                group_id = self.groups[ticket.team_name]['team_id']

                # Look for epic
                if ticket.epic in self.groups[ticket.team_name]['epics']:
                    # Get epic group id
                    epic_group_id = self.groups[ticket.team_name]['epics'][ticket.epic]['epic_id']
                else:
                    if ticket.epic is None:
                        # A ticket without epic
                        task_payload = teamgantt_utils.create_task_payload(ticket, parent_group_id=group_id,
                                                                           project_id=self.project_id)
                        self.add_task_and_resource_to_teamgantt(task_payload, ticket, url)
                        return
                    else:
                        # Create a new group for the epic
                        epic_group_id = self.create_group(ticket.epic, self.groups[ticket.team_name]['epics'], group_id,
                                                          is_epic=True)
            else:
                # Create a new group
                group_id = self.create_group(ticket.team_name, self.groups)

                if ticket.epic is None:
                    # In case that the ticket has no epic, add it to the team group
                    task_payload = teamgantt_utils.create_task_payload(ticket, parent_group_id=group_id,
                                                                       project_id=self.project_id)
                    self.add_task_and_resource_to_teamgantt(task_payload, ticket, url)
                    return

                epic_group_id = self.create_group(ticket.epic, self.groups[ticket.team_name]['epics'], group_id,
                                                  is_epic=True)

            # Check if the task have sub tasks, if it have any make it a group and call the method again for the subtasks
            if len(ticket.ticket_subtasks) > 0:
                parent_group_id = self.create_group(ticket.ticket_summary,
                                                    self.groups[ticket.team_name]['epics'][ticket.epic]['stories'],
                                                    epic_group_id)
                for sub_task in ticket.ticket_subtasks:
                    self.create_task(sub_task, parent_group_id)

                return

            task_payload = teamgantt_utils.create_task_payload(ticket, parent_group_id=epic_group_id,
                                                               project_id=self.project_id)
            self.add_task_and_resource_to_teamgantt(task_payload, ticket, url)

    def update_task(self, task):
        url = BASE_URL + "/tasks/" + str(task.teamgantt_id) + "?assigned_hours_set=total_hours_adjust"
        update_payload = teamgantt_utils.create_task_payload(task)
        json_obj, status_code = utils.execute_url(url=url, method="patch", headers=self.headers, body=update_payload)
        print(status_code)

    def add_task_and_resource_to_teamgantt(self, task_payload, ticket, url):
        resource_id, task_resource = self.get_resource_for_task(ticket)
        task_payload = teamgantt_utils.add_time_to_task(task_payload, ticket)
        json_obj, status_code = utils.execute_url(url=url, method="post", headers=self.headers, body=task_payload)

        if status_code != 200:
            return

        # Add the task id to the teamgantt ticket
        teamgantt_task_id = json_obj['id']
        ticket.add_teamgantt_id(teamgantt_task_id)
        # Add resource to task (the assignee)
        self.add_resource_to_task_in_teamgantt(ticket, resource_id)

    def get_resources(self):
        # API requests
        url = BASE_URL + "/projects/" + str(config.teamgantt_project_id) + "/resources"
        json_obj, _ = utils.execute_url(url=url, method="get", headers=self.headers)

        resources_dict = {}
        # Iterate on all the resources and add them to the map
        for resource_json in json_obj:
            name = resource_json['name']
            id = resource_json['id']
            resources_dict[name] = Resource(id, name)
        return resources_dict

    def update_resources(self):
        for resource_name in self.resources:
            resource = self.resources[resource_name]
            resource.set_sprint_start_date(self.sprint_start_date)

    def get_groups(self):
        url = BASE_URL + "/groups?project_ids=" + str(self.project_id)
        json_obj, _ = utils.execute_url(url=url, method="get", headers=self.headers)

        groups = {}
        for group_json in json_obj:
            team_name = group_json['name']
            team_id = group_json['id']
            groups[team_name] = {'team_id': team_id,
                                 'epics': {}}
            # Get epics for the team
            for epic_json in group_json['children']:
                epic_name = epic_json['name']
                epic_id = epic_json['id']
                groups[team_name]['epics'][epic_name] = {'epic_id': epic_id,
                                                         'stories': {}}

                # Get stories for the epic
                for story_json in epic_json['children']:
                    story_name = story_json['name']
                    story_id = story_json['id']
                    groups[team_name]['epics'][epic_name]['stories'][story_name] = story_id
        return groups

    def add_resource_to_task_in_teamgantt(self, task, resource_id):
        url = BASE_URL + "/tasks/" + str(task.teamgantt_id) + "/resources"
        resource_payload = {'type': 'project',
                            'type_id': resource_id}
        utils.execute_url(url=url, method="post", headers=self.headers, body=resource_payload)

    def create_group(self, group_name, group_dict, parent_group_id=None, is_epic=False):
        url = BASE_URL + "/groups"
        group_payload = {'project_id': self.project_id,
                         'name': group_name}

        if parent_group_id is not None:
            # Add parent group id
            group_payload['parent_group_id'] = parent_group_id
            json_obj, _ = utils.execute_url(url=url, method="post", headers=self.headers, body=group_payload)
            if 'id' in json_obj:
                group_id = json_obj['id']
            else:
                print('none')
            if is_epic:
                group_dict[group_name] = {'epic_id': group_id,
                                          'stories': {}}
            else:
                group_dict[group_name] = group_id
        else:
            json_obj, _ = utils.execute_url(url=url, method="post", headers=self.headers, body=group_payload)
            group_id = json_obj['id']
            group_dict[group_name] = {'team_id': group_id,
                                      'epics': {}}

        return group_id

    def add_to_project_resource_list(self, task):
        resource_payload = {"type": "company",
                            "name": task.get_assignee()}

        url = BASE_URL + "/projects/" + str(self.project_id) + "/resources"
        json_obj, _ = utils.execute_url(url=url, method="post", headers=self.headers, body=resource_payload)
        self.resources[task.get_assignee()] = Resource(json_obj['id'], task.get_assignee(), self.sprint_start_date)
        return json_obj['id']

    def set_sprint_start_date(self, start_date):
        if self.sprint_start_date is None:
            self.sprint_start_date = start_date

    def get_resource_for_task(self, task):
        if task.get_assignee() in self.resources:
            resource_id = self.resources[task.get_assignee()].id
        else:
            # Add resource to task
            resource_id = self.add_to_project_resource_list(task)

        task.resource = self.resources[task.get_assignee()]
        return resource_id, self.resources[task.get_assignee()]


def set_auth_header():
    app_token, email, password = auth.get_teamgantt_auth_token()
    header = {'Content-Type': 'application/json',
              'TG-Authorization': 'Bearer ' + app_token}
    auth_payload = {'user': email, 'pass': str(password)}

    # send app_token to get api token and user token (create session)
    url = BASE_URL + "/authenticate"
    json_obj, _ = utils.execute_url(url=url, method="post", headers=header, body=auth_payload)

    # extract session api and user token
    api_key = json_obj['api_key']
    user_token = json_obj['user_token']

    return {'TG-Authorization': 'Bearer ' + app_token,
            'TG-Api-Key': api_key,
            'TG-User-Token': user_token}
