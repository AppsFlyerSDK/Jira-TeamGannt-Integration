from datetime import datetime


def print_log(sentence_to_print):
    print("[{}] - {}".format(get_time_str(), sentence_to_print))


def get_time_str():
    return datetime.now().strftime('%H:%M:%S')

# Todo - save all logs and write them to a file
# Todo - Make a report
