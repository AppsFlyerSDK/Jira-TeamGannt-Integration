import auth
import requests
import json
import utils.utils as utils

BASE_URL = "https://api.teamgantt.com/v1"


class TeamGanttClient:
    def __init__(self):
        self.headers = set_auth_header()
        self.project_id = utils.get_teamgantt_project_id()
        self.resources = self.get_resources()
        self.groups = self.get_groups()

    def create_task(self, ticket):
        url = BASE_URL + "/tasks"

        task_payload = {"project_id": self.project_id,
                        "name": ticket.task,
                        "type": "task"}
        # Get group id
        if ticket.team_name in self.groups:
            group_id = self.groups[ticket.team_name]['team_id']
            # task_payload["parent_group_id"] = group_id

            # Look for epic
            if ticket.ticket_epic in self.groups[ticket.team_name]['epics']:
                # Get epic group id
                epic_group_id = self.groups[ticket.team_name]['epics'][ticket.ticket_epic]['epic_id']
            else:
                # Create a new group for the epic
                epic_group_id = self.create_group(ticket, group_id)
                pass
        else:
            # Create a new group
            group_id = self.create_group(ticket)
            epic_group_id = self.create_group(ticket, group_id)

        task_payload['parent_group_id'] = epic_group_id
        resp = requests.post(url, data=json.dumps(task_payload), headers=self.headers)
        return resp

    def get_resources(self):
        # API requests
        url = BASE_URL + "/companies/" + str(utils.get_company_id()) + "/resources"
        resp = requests.get(url, headers=self.headers)
        json_obj = utils.get_json(resp)

        resources_dict = {}
        # Iterate on all the resources and add them to the map
        for resource_json in json_obj:
            name = resource_json['name'].lower().strip()
            id = resource_json['id']
            resources_dict[name] = id
        return resources_dict

    def get_groups(self):
        url = BASE_URL + "/groups?project_ids=" + str(self.project_id)
        resp = requests.get(url, headers=self.headers)
        json_obj = utils.get_json(resp)

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

    def add_resource(self, task):
        url = BASE_URL + "/tasks/" + str(task.task_id) + "/resources"
        resource_payload = {'type': 'company'}

        if task.assignee.lower().strip() in self.resources:
            resource_id = self.resources[task.assignee.lower().strip()]
            resource_payload['type_id'] = resource_id

        resp = requests.post(url, data=json.dumps(resource_payload), headers=self.headers)

    def create_group(self, ticket, epic_parent_id=None):
        url = BASE_URL + "/groups"
        group_payload = {'project_id': self.project_id,
                         'name': ticket.team_name}

        if epic_parent_id is not None:
            # Add parent group id
            group_payload['parent_group_id'] = epic_parent_id

        resp = requests.post(url, data=json.dumps(group_payload), headers=self.headers)
        json_obj = utils.get_json(resp)
        group_id = json_obj['id']
        self.groups[ticket.team_name] = {'team_id': group_id,
                                         'epics': {}}

        return group_id


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
