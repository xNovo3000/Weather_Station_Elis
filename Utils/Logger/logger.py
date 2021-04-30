# encoding: UTF-8

"""
Version: 0.2
Updated: 20/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import os
from datetime import datetime


# LA NUOVA CLASSE Logger
class Logger:

    # I COLORI IN OUTPUT DA TERMINALE
    __LOG_COLOR = {
        "INFO": "\033[94m",
        "WARN": "\033[93m",
        "ERR": "\033[91m",
        "NONE": "\033[0m",
    }

    # INIZIALIZZAZIONE
    def __init__(self, file_name=None, terminal=True):
        self.terminal = terminal
        if file_name:
            path = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Logs")
            if not os.path.exists(path):
                os.makedirs(path)
            self.file = open(os.path.join(path, "{}.log".format(file_name)), "a+")
        else:
            self.file = None

    # STAMPA UN MESSAGGIO DI ERRORE
    def err(self, name, value):
        self.__print("ERR", name, value)

    # STAMPA UN AVVERTIMENTO
    def warn(self, name, value):
        self.__print("WARN", name, value)

    # STAMPA UN'INFORMAZIONE
    def info(self, name, value):
        self.__print("INFO", name, value)

    # FUNZIONE NASCOSTA CHE STAMPA SIA SU CONSOLE CHE SU FILE
    def __print(self, code, name, value):
        result = "{} - [{}] {}: {}".format(datetime.now().strftime("%Y/%m/%d %H:%M:%S"), code, name, value)
        if self.file:
            self.file.write("{}\n".format(result))
            self.file.flush()
        if self.terminal:
            print("{}{}{}".format(Logger.__LOG_COLOR[code], result, Logger.__LOG_COLOR["NONE"]))
