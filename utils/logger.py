from datetime import datetime
import utils

logger_list = []


def print_log(sentence_to_print):
    sentence_to_print = "[{}] - {}".format(get_time_str(), sentence_to_print)
    logger_list.append(sentence_to_print)
    print(sentence_to_print)


def get_time_str():
    return datetime.now().strftime('%H:%M:%S')


def print_log_to_file():
    with open(utils.create_doc_title(), 'w') as file:
        for log in logger_list:
            file.write(log + "\n")
