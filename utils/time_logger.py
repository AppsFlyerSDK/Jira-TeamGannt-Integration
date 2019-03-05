import time


class TimeLogger:
    def __init__(self):
        self.start = time.time()
        self.end = 0

    def elapsed_time(self):
        self.end = time.time()
        return int((self.end - self.start)*1000)
