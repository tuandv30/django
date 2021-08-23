import json
from datetime import datetime


class Log:
    __log_type = None

    def __init__(self, log_type):
        self.__log_type = log_type

    def info(self, message, extra=None):
        self.print_log(message, "INFO", extra)

    def error(self, message, extra=None):
        self.print_log(message, "ERROR", extra)

    def warn(self, message, extra=None):
        self.print_log(message, "WARNING", extra)

    def print_log(self, message, log_level, extra):
        obj_log = {
            "log_type": self.__log_type,
            "log_level": log_level,
            "messages": message,
            "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        if extra is not None:
            for key, value in extra.items():
                obj_log[key] = value
        print(json.dumps(obj_log))
