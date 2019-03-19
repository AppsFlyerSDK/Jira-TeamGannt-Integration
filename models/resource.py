from utils import utils
from datetime import datetime


class Resource:
    def __init__(self, id, name, sprint_start_date=None):
        self.id = id
        self.name = name
        if type(sprint_start_date) is datetime:
            self.start_date = utils.convert_to_teamgantt_date_format(sprint_start_date)
            self.cur_date = utils.convert_to_teamgantt_date_format(sprint_start_date)  # in format of YYYY-MM-DD
        else:
            self.start_date = sprint_start_date
            self.cur_date = sprint_start_date

    def set_sprint_start_date(self, start_date):
        self.cur_date = self.start_date = utils.convert_to_teamgantt_date_format(start_date)

    def __repr__(self):
        return "<{}> - {} - {}".format(self.name, self.start_date, self.cur_date)
