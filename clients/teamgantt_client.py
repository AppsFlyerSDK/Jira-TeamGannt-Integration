import auth
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
            if ticket.epic in self.groups[ticket.team_name]['epics']:
                # Get epic group id
                epic_group_id = self.groups[ticket.team_name]['epics'][ticket.epic]
            else:
                # Create a new group for the epic
                epic_group_id = self.create_group(ticket.epic, group_id, ticket.team_name)
                pass
        else:
            # Create a new group
            group_id = self.create_group(ticket.team_name)
            epic_group_id = self.create_group(ticket.epic, group_id, ticket.team_name)

        task_payload['parent_group_id'] = epic_group_id
        # resp = requests.post(url, data=json.dumps(task_payload), headers=self.headers)
        return utils.execute_url(url=url, method="post", headers=self.headers, body=task_payload)

    def get_resources(self):
        # API requests
        url = BASE_URL + "/projects/" + str(utils.get_teamgantt_project_id()) + "/resources"
        json_obj = utils.execute_url(url=url, method="get", headers=self.headers)

        resources_dict = {}
        # Iterate on all the resources and add them to the map
        for resource_json in json_obj:
            name = resource_json['name']
            id = resource_json['id']
            resources_dict[name] = id
        return resources_dict

    def get_groups(self):
        url = BASE_URL + "/groups?project_ids=" + str(self.project_id)
        json_obj = utils.execute_url(url=url, method="get", headers=self.headers)

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

    def add_resource_to_task(self, task):
        url = BASE_URL + "/tasks/" + str(task.task_id) + "/resources"
        resource_payload = {'type': 'project'}

        if task.get_assignee() in self.resources:
            resource_id = self.resources[task.get_assignee()]
        else:
            # Add resource to task
            resource_id = self.add_to_project_resource_list(task)

        resource_payload['type_id'] = resource_id
        utils.execute_url(url=url, method="post", headers=self.headers, body=resource_payload)

    def create_group(self, group_name, epic_parent_id=None, team_name=None):
        url = BASE_URL + "/groups"
        group_payload = {'project_id': self.project_id,
                         'name': group_name}

        if epic_parent_id is not None:
            # Add parent group id
            group_payload['parent_group_id'] = epic_parent_id
            # resp = requests.post(url, data=json.dumps(group_payload), headers=self.headers)
            json_obj = utils.execute_url(url=url, method="post", headers=self.headers, body=group_payload)
            group_id = json_obj['id']
            self.groups[team_name]['epics'][group_name] = group_id
        else:
            # resp = requests.post(url, data=json.dumps(group_payload), headers=self.headers)
            json_obj = utils.execute_url(url=url, method="post", headers=self.headers, body=group_payload)
            group_id = json_obj['id']
            self.groups[group_name] = {'team_id': group_id,
                                       'epics': {}}

        return group_id

    def add_to_project_resource_list(self, task):
        resource_payload = {"type": "company",
                            "name": task.get_assignee()}

        url = BASE_URL + "/projects/" + str(self.project_id) + "/resources"
        json_obj = utils.execute_url(url=url, method="post", headers=self.headers, body=resource_payload)
        self.resources[task.get_assignee()] = json_obj['id']
        return json_obj['id']


def set_auth_header():
    app_token, email, password = auth.get_teamgantt_auth_token()
    header = {'Content-Type': 'application/json',
              'TG-Authorization': 'Bearer ' + app_token}
    auth_payload = {'user': email, 'pass': str(password)}

    # send app_token to get api token and user token (create session)
    url = BASE_URL + "/authenticate"
    json_obj = utils.execute_url(url=url, method="post", headers=header, body=auth_payload)

    # extract session api and user token
    api_key = json_obj['api_key']
    user_token = json_obj['user_token']

    return {'TG-Authorization': 'Bearer ' + app_token,
            'TG-Api-Key': api_key,
            'TG-User-Token': user_token}
