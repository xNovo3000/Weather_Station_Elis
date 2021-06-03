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

    # I COLORI IN OUTPUT DA TERMINALE
    __LOG_COLOR = {
        "INFO": "\033[94m",
        "WARN": "\033[93m",
        "ERR": "\033[91m",
        "NONE": "\033[0m",
    }

    def __init__(self, name):
        Thread.__init__(self)
        self.configurations = Configs.load(name)
        self.strings = []
        self.strings_mutex = Lock()
        if self.configurations["write_to_file"] is not None:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Logs")
            if not os.path.exists(path):
                os.makedirs(path)
            self.file = open(os.path.join(path, "{}.log".format(self.configurations["write_to_file"])), "a+")
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
        if self.configurations["write_to_terminal"]:
            for (string, code) in now_strings:
                print("{}{}{}".format(Logger.__LOG_COLOR[code], string, Logger.__LOG_COLOR["NONE"]))
        # check if log to file
        if self.file is not None:
            for (string, _) in now_strings:
                self.file.write("{}\n".format(string))
            self.file.flush()

    # STAMPA UN MESSAGGIO DI ERRORE
    def err(self, name, value):
        self.__generate_string("ERR", name, value)

    # STAMPA UN AVVERTIMENTO
    def warn(self, name, value):
        self.__generate_string("WARN", name, value)

    # STAMPA UN'INFORMAZIONE
    def info(self, name, value):
        self.__generate_string("INFO", name, value)

    # FUNZIONE NASCOSTA CHE STAMPA SIA SU CONSOLE CHE SU FILE
    def __generate_string(self, code, name, value):
        self.strings_mutex.acquire()
        self.strings.append(  # tuple (string, code)
            ("{} - [{}] {}: {}".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), code, name, value), code)
        )
        self.strings_mutex.release()
