class Board:
    def __init__(self, board_id, board_name, project_name):
        self.board_id = board_id
        self.board_name = board_name
        self.project_name = project_name
        self.sprints = {}  # Initialize with empty dictionary

    def __repr__(self):
        return "Board id: {}\tBoard name: {}".format(self.board_id, self.board_name)
