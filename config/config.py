import yaml
from pathlib import Path

# Config class. Gets all the required configuration parameters from our config.yaml file,
# and place them inside the corresponded variables


db_string = None
db_user = None
db_password = None
db_name = None
db_schema = None
db_table_name = None
teamgantt_project_id = None
teamgantt_company_id = None
teamgantt_token = None
teamgantt_email = None
teamgantt_password = None
jira_token = None
jira_email = None


def is_file_valid(config_file):
    return Path(config_file).is_file() and config_file.lower().endswith('.yaml')


def init_config_parameters(config_file):
    global db_string, db_user, db_password, db_name, db_schema, db_table_name, teamgantt_project_id, teamgantt_company_id, teamgantt_token, teamgantt_email, teamgantt_password, jira_token, jira_email
    if is_file_valid(config_file):
        with open(config_file, "r") as config_stream:
            try:
                # Load the config yaml file into a dictionary
                yaml_dict = yaml.load(config_stream)
                # DB config params
                db_string = yaml_dict['Db']['ConnectionString']
                db_user = yaml_dict['Db']['user']
                db_password = yaml_dict['Db']['password']
                db_name = yaml_dict['Db']['DbName']
                db_schema = yaml_dict['Db']['DbSchema']
                db_table_name = yaml_dict['Db']['DbTableName']
                # TeamGantt params
                teamgantt_project_id = yaml_dict['TeamGantt']['projectId']
                teamgantt_company_id = yaml_dict['TeamGantt']['companyId']
                # TeamGantt Auth params
                teamgantt_token = yaml_dict['Auth']['TeamGantt']['App-Token']
                teamgantt_email = yaml_dict['Auth']['TeamGantt']['EMail']
                teamgantt_password = yaml_dict['Auth']['TeamGantt']['pass']
                # Jira params
                jira_token = yaml_dict['Auth']['Jira']['Token']
                jira_email = yaml_dict['Auth']['Jira']['EMail']
            except yaml.YAMLError as exc:
                print(exc)
