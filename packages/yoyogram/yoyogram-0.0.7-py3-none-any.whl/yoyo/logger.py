import sys
import os
import logging

from datetime import datetime


class Logger(object):
    log_file = bytes
    EXCEPTION = 100
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self):
        today = datetime.strftime(datetime.now(), "%d-%m-%y-%H_%M_%S")

        if not os.path.exists("logs"):
            os.mkdir("logs")

        LOGS_FOLDER = f"logs/log-{today}.log"
        LOGGER_NAME = "YoYoLogger"

        logging.basicConfig(
            filename=LOGS_FOLDER,
            filemode="w",
            format="[%(asctime)s] [%(levelname)s] -- %(message)s",
            datefmt="%d/%b/%y %H:%M:%S",
            encoding="utf-8"
        )


        self.__log = logging.getLogger(LOGGER_NAME)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] -- %(message)s", datefmt="%d/%b/%y %H:%M:%S"
        )
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(formatter)

        self.__log.setLevel(self.INFO)
        self.__methods_map = {
            self.DEBUG: self.__log.debug,
            self.INFO: self.__log.info,
            self.WARNING: self.__log.warning,
            self.ERROR: self.__log.error,
            self.CRITICAL: self.__log.critical,
            self.EXCEPTION: self.__log.exception,
        }


    def __call__(self, lvl, msg, *args, **kwargs):
        if lvl in self.__methods_map:
            self.__methods_map[lvl](msg, *args, **kwargs)
        else:
            self.__log.log(lvl, msg, *args, **kwargs)


    def set_level(self, level=None):
        if level is None:
            level = self.INFO
        self.__log.setLevel(level)
