from datetime import datetime


class Sprint:
    def __init__(self, sprint_id, sprint_start_date, sprint_end_date):
        self.sprint_id = sprint_id
        self.sprint_start_date = sprint_start_date
        self.sprint_end_date = sprint_end_date
        self.tickets = {}  # Initalize an empty tickets dictionary

    def is_sprint_active(self):
        return self.sprint_end_date > datetime.now() > self.sprint_start_date

    def __repr__(self):
        return "[{}] - {} - {}".format(self.sprint_id, self.sprint_start_date, self.sprint_end_date)
