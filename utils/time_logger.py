import time


class TimeLogger:
    def __init__(self):
        self.start = time.time()
        self.end = 0

    def elapsed_time(self):
        self.end = time.time()
        milliseconds = int((self.end - self.start)*1000)

        # pretty print the time elapsed
        print("Elapsed time: {} Seconds".format(milliseconds/1000.0))

        return milliseconds
