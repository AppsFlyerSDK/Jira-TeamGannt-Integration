import base64
import config


# return the base64 encoded string (email:token)
def get_jira_auth_token():
    token = config.jira_token
    email = config.jira_email

    auth_str = email + ":" + token
    return str(base64.b64encode(str.encode(auth_str)))


def get_teamgantt_auth_token():
    token = config.teamgantt_token
    email = config.teamgantt_email
    password = config.teamgantt_password

    return token, email, password
