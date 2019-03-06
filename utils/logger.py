from datetime import datetime


class Logger:
    def __init__(self, class_name):
        self.class_name = class_name

    def print_log(self, str):
        print("[{}] - {} - {}".format(self.class_name, get_time_str(), str))


def get_time_str():
    return datetime.now().strftime('%H:%M:%S')
