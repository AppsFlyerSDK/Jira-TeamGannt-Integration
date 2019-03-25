import requests
import json
from utils import utils


class Report:
    def __init__(self):
        self.new_tickets = None
        self.update_tickets = None
        self.rest_api_calls = {}
        self.time_elapsed = None
        self.new_tickets = []
        self.update_tickets = []

    def add_api_call(self, method):
        if method in self.rest_api_calls:
            self.rest_api_calls[method] += 1
        else:
            self.rest_api_calls[method] = 1

    def build_new_tickets_str(self):
        if len(self.new_tickets) == 0:
            return "there aren't any new tickets"

        new_tickets_str = "\n" + " " * 10 + "_tasks by category_\n```"
        count = 0
        tickets_by_type = {}
        tickets_by_team = {}

        for ticket in self.new_tickets:
            if ticket.ticket_type in tickets_by_type:
                tickets_by_type[ticket.ticket_type] += 1
            else:
                tickets_by_type[ticket.ticket_type] = 1

            if ticket.team_name in tickets_by_team:
                tickets_by_team[ticket.team_name] += 1
            else:
                tickets_by_team[ticket.team_name] = 1

            count += 1

        for ticket_type in tickets_by_type:
            new_tickets_str += "{}".format(ticket_type).ljust(25) + "{}\n".format(tickets_by_type[ticket_type]).rjust(
                5)

        new_tickets_str += "```\n" + " " * 10 + "_tasks by team_\n```"
        for team in tickets_by_team:
            new_tickets_str += "{}".format(team).ljust(25) + "{}\n".format(tickets_by_team[team]).rjust(5)

        new_tickets_str += "```\n*{}* tasks were added to TeamGantt".format(count)

        return new_tickets_str

    def build_update_tickets_str(self):
        for ticket in self.update_tickets:
            pass
        return ""

    def write_report(self):
        rest_api_str = self.build_rest_api_calls_str()
        new_ticket_str = self.build_new_tickets_str()
        update_ticket_str = self.build_update_tickets_str()
        report_str = "*{}* :jira-tg: \n" \
                     "{}\n" \
                     "--------------------------------------------\n" \
                     "*Tasks summary*\n" \
                     "*New tasks:*\n" \
                     "{}\n" \
                     "--------------------------------------------\n" \
                     "*Updated tasks:*\n" \
                     "{}\n" \
                     "--------------------------------------------\n" \
                     "Total time taken *{}* minutes\n".format(utils.create_doc_title(), rest_api_str,
                                                              new_ticket_str, update_ticket_str,
                                                              utils.format_milli(self.time_elapsed))

        write_to_slack(report_str)

    def build_rest_api_calls_str(self):
        my_str = "*Api calls*:\n"
        total = 0
        for method in self.rest_api_calls:
            total += self.rest_api_calls[method]
            my_str += "*{}*".format(method).ljust(25) + "{}\n".format(self.rest_api_calls[method]).rjust(5)

        my_str += "*Total:*".ljust(25) + "*{}*".format(total).rjust(5)
        return my_str


def write_to_slack(report_str):
    url = 'https://hooks.slack.com/services/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'
    slack_payload = {
        'text': report_str
    }
    requests.post(url, data=json.dumps(slack_payload), headers={'Content-Type': 'application/json'})
