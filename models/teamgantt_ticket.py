class TeamganttTicket:
    def __init__(self, team_name, epic, task, subtask, assignee, assignee_email, story_points, status, ticket_jira_id,
                 ticket_jira_last_update):
        self.team_name = team_name  # The group name in teamgantt
        self.epic = epic
        self.task = task
        self.subtask = subtask
        self.assignee = assignee
        self.assignee_email = assignee_email
        self.story_points = story_points
        self.status = status
        self.ticket_jira_id = ticket_jira_id
        self.ticket_jira_last_update = ticket_jira_last_update
        self.task_id = None

    def add_teamgantt_id(self, task_id):
        self.task_id = task_id

    def get_assignee(self):
        return "{} - {}".format(self.assignee, self.assignee_email)
