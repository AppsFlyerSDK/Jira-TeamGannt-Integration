# Jira ticket
class Ticket:
    def __init__(self, ticket_id, ticket_key, ticket_type, ticket_epic, assignee, assignee_email, ticket_status,
                 ticket_summary,
                 ticket_estimation_time, ticket_last_update, ticket_parent, ticket_parent_id, ticket_subtasks,
                 team_name):
        self.ticket_jira_id = ticket_id
        self.ticket_key = ticket_key
        self.ticket_type = str(ticket_type).replace("'", "")
        self.epic = str(ticket_epic).replace("'", "")
        self.assignee = str(assignee).replace("'", "")
        self.assignee_email = str(assignee_email).replace("'", "")
        self.ticket_status = str(ticket_status).replace("'", "")
        self.ticket_summary = str(ticket_summary).replace("'", "")
        self.ticket_estimation_time = str(ticket_estimation_time).replace("'", "")
        self.ticket_jira_last_update = str(ticket_last_update).replace("'", "")
        self.ticket_parent = ticket_parent
        self.ticket_parent_id = ticket_parent_id
        self.ticket_subtasks = ticket_subtasks
        self.team_name = str(team_name).replace("'", "")
        self.teamgantt_id = None
        self.resource = None

    def add_teamgantt_id(self, task_id):
        self.teamgantt_id = task_id

    def get_assignee(self):
        return "{} - {}".format(self.assignee, self.assignee_email)

    def set_resource(self, resource):
        self.resource = resource

    def __repr__(self):
        return "[{} | {}] - {} <{}>".format(self.ticket_jira_id, self.ticket_type, self.ticket_summary,
                                            self.assignee_email)
