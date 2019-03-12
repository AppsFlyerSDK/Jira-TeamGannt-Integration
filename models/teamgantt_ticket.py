class TeamganttTicket:
    def __init__(self, team_name, epic, task, subtask, assignee, story_points, status):
        self.team_name = team_name  # The group name in teamgantt
        self.epic = epic
        self.task = task
        self.subtask = subtask
        self.assignee = assignee
        self.story_points = story_points
        self.status = status
        self.task_id = None

    def add_teamgantt_id(self, task_id):
        self.task_id = task_id
