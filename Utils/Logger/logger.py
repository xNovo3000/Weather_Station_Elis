# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import os
import time
import logging
from threading import Thread, Lock
from logging.handlers import RotatingFileHandler

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger.custom_formatter import CustomFormatter


# Nuova classe Logger
class Logger(Thread):

    def __init__(self, name):
        Thread.__init__(self)
        self.configurations = Configs.load(name)
        self.strings = []
        self.strings_mutex = Lock()
        # gestisce la retrocompatibilità con le vecchie versioni del logger
        if "write_to_terminal" in self.configurations:
            self.configurations["file"] = {
                "enabled": self.configurations["write_to_file"] is not None,
                "level": 10,
                "name": self.configurations["write_to_file"],
                "max_bytes": 16777216,
                "backup_count": 3
            }
            self.configurations["terminal"] = {
                "enabled": self.configurations["write_to_terminal"],
                "level": 10
            }
        # adesso inizializzo il logger di logging
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(10)
        # verifica se si vuole stampare su terminale
        if self.configurations["terminal"]["enabled"]:
            terminal_stream_handler = logging.StreamHandler()
            terminal_stream_handler.setFormatter(CustomFormatter(
                fmt="%(asctime)s - [%(levelname)s] %(message)s",
                datefmt="%Y/%m/%d %H:%M:%S",
                is_terminal=True
            ))
            terminal_stream_handler.setLevel(self.configurations["terminal"]["level"])
            self.logger.addHandler(terminal_stream_handler)
        if self.configurations["file"]["enabled"]:
            # genera la path del file
            path = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Logs")
            if not os.path.exists(path):
                os.makedirs(path)
            # genera l'handler
            rotating_file_handler = RotatingFileHandler(
                filename=os.path.join(path, "{}.log".format(self.configurations["file"]["name"])),
                mode="a",
                maxBytes=self.configurations["file"]["max_bytes"],
                backupCount=self.configurations["file"]["backup_count"]
            )
            # inietta il formatter
            rotating_file_handler.setFormatter(CustomFormatter(
                fmt="%(asctime)s - [%(levelname)s] %(message)s",
                datefmt="%Y/%m/%d %H:%M:%S",
                is_terminal=False
            ))
            # imposta il livello di log
            rotating_file_handler.setLevel(self.configurations["file"]["level"])
            # registra nel logger
            self.logger.addHandler(rotating_file_handler)

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
        # log using logging
        for (string, level) in now_strings:
            self.logger.log(level=level, msg=string)

    # ERRORE BLOCCANTE - IL PROGRAMMA TERMINA
    def err(self, name, value):
        self.__generate_string(logging.ERROR, name, value)

    # ERRORE NON BLOCCANTE - IL PROGRAMMA PROSEGUE L'ESECUZIONE
    def warn(self, name, value):
        self.__generate_string(logging.WARNING, name, value)

    # INFORMAZIONE - ES. CONNESSO ALLA WEATHER STATION, OTTENUTO LE MISURAZIONI, ECC...
    def info(self, name, value):
        self.__generate_string(logging.INFO, name, value)

    # INFORMAZIONE DI DEBUG - UTILE SOLO PER IL DEBUGGING (VALORI, CHECKPOINT, ECC...)
    def debug(self, name, value):
        self.__generate_string(logging.DEBUG, name, value)

    # GENERA LA STRINGA DA SCRIVERE EVENTUALMENTE SIA SUL TERMINALE CHE SU FILE
    def __generate_string(self, code, name, value):
        self.strings_mutex.acquire()
        self.strings.append(("{}: {}".format(name, value), code))
        self.strings_mutex.release()
