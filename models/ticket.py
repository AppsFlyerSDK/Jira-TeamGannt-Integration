# Jira ticket
class Ticket:
    def __init__(self, ticket_id, ticket_key, ticket_type, ticket_epic, assignee, assignee_email, ticket_status,
                 ticket_summary,
                 ticket_estimation_time, ticket_last_update, ticket_parent, ticket_parent_id):
        self.ticket_id = ticket_id
        self.ticket_key = ticket_key
        self.ticket_type = ticket_type
        self.ticket_epic = ticket_epic
        self.assignee = assignee
        self.assignee_email = assignee_email
        self.ticket_status = ticket_status
        self.ticket_summary = ticket_summary
        self.ticket_estimation_time = ticket_estimation_time
        self.ticket_last_update = ticket_last_update
        self.ticket_parent = ticket_parent
        self.ticket_parent_id = ticket_parent_id
