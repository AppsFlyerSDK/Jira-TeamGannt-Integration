import yaml
import base64


# return the base64 encoded string (email:token)
def get_jira_auth_token():
    with open("config/config.yaml", 'r') as stream:
        try:
            # Load the config yaml file
            yaml_dict = yaml.load(stream)

            token = yaml_dict['Auth']['Jira']['Token']
            email = yaml_dict['Auth']['Jira']['EMail']

            auth_str = email + ":" + token
            return str(base64.encodebytes(str.encode(auth_str)), "utf-8")
        except yaml.YAMLError as exc:
            print(exc)


def get_teamgantt_auth_token():
    with open("config/config.yaml", 'r') as stream:
        try:
            # Load the config yaml file
            yaml_dict = yaml.load(stream)

            token = yaml_dict['Auth']['TeamGantt']['App-Token']
            email = yaml_dict['Auth']['TeamGantt']['EMail']
            password = yaml_dict['Auth']['TeamGantt']['pass']

            return token, email, password
        except yaml.YAMLError as exc:
            print(exc)
