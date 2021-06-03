# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import os
import time
from datetime import datetime
from threading import Thread, Lock

# AMBIENT IMPORT
import Utils.Configs as Configs


# Nuova classe Logger
class Logger(Thread):

    __LOG_LEVEL = {
        0: {
            "label": "ERR",
            "color": "\033[91m"
        },
        1: {
            "label": "WARN",
            "color": "\033[93m"
        },
        2: {
            "label": "INFO",
            "color": "\033[94m"
        },
        3: {
            "label": "DEBUG",
            "color": "\033[0m"
        },
        -1: {
            "color": "\033[0m"
        },
    }

    def __init__(self, name):
        Thread.__init__(self)
        self.configurations = Configs.load(name)
        self.strings = []
        self.strings_mutex = Lock()
        if self.configurations["file"]["enabled"]:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Logs")
            if not os.path.exists(path):
                os.makedirs(path)
            self.file = open(os.path.join(path, "{}.log".format(self.configurations["file"]["name"])), "a+")
        else:
            self.file = None

    # CHIAMATO DA Thread.start(self)
    def run(self):
        while True:
            begin = time.time()
            self.__log_all()
            end = time.time()
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))

    def __log_all(self):
        # get data
        self.strings_mutex.acquire()
        now_strings = self.strings.copy()
        self.strings.clear()
        self.strings_mutex.release()
        # check if log to terminal
        if self.configurations["terminal"]["enabled"]:
            for (string, code) in now_strings:
                if self.configurations["terminal"]["level"] >= code:
                    print("{}{}{}".format(Logger.__LOG_LEVEL[code]["color"], string, Logger.__LOG_LEVEL[-1]["color"]))
        # check if log to file
        if self.file is not None:
            for (string, code) in now_strings:
                if self.configurations["file"]["level"] >= code:
                    self.file.write("{}\n".format(string))
            self.file.flush()

    # ERRORE BLOCCANTE - IL PROGRAMMA TERMINA
    def err(self, name, value):
        self.__generate_string(0, name, value)

    # ERRORE NON BLOCCANTE - IL PROGRAMMA PROSEGUE L'ESECUZIONE
    def warn(self, name, value):
        self.__generate_string(1, name, value)

    # INFORMAZIONE - ES. CONNESSO ALLA WEATHER STATION, OTTENUTO LE MISURAZIONI, ECC...
    def info(self, name, value):
        self.__generate_string(2, name, value)

    # INFORMAZIONE DI DEBUG - UTILE SOLO PER IL DEBUGGING (VALORI, CHECKPOINT, ECC...)
    def debug(self, name, value):
        self.__generate_string(3, name, value)

    # GENERA LA STRINGA DA SCRIVERE EVENTUALMENTE SIA SUL TERMINALE CHE SU FILE
    def __generate_string(self, code, name, value):
        self.strings_mutex.acquire()
        self.strings.append(  # tuple (string, code)
            ("{} - [{}] {}: {}".format(
                datetime.now().strftime("%Y/%m/%d %H:%M:%S"), Logger.__LOG_LEVEL[code]["label"], name, value
            ), code)
        )
        self.strings_mutex.release()
