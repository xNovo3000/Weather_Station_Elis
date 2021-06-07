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
import logging.handlers
from threading import Thread, Lock

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger.colored_formatter import ColoredFormatter


# Nuova classe Logger
class Logger(Thread):

    __LOGGER_FMT = "%(asctime)s - [%(levelname)s] %(message)s"
    __LOGGER_DATEFMT = "%Y/%m/%d %H:%M:%S"

    def __init__(self, name):
        Thread.__init__(self)
        self.strings = []
        self.valid = False
        self.strings_mutex = Lock()
        self.configurations = Configs.load(name)
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
        # crea il logger di logging
        self.inner = logging.getLogger(name=name)
        self.inner.setLevel(logging.DEBUG)
        # se la stampa su terminale è attiva inizializzala
        if self.configurations["terminal"]["enabled"]:
            # genera l'handler per il terminale e imposta livello e formatter colorato
            thandler = logging.StreamHandler()
            thandler.setFormatter(ColoredFormatter(fmt=Logger.__LOGGER_FMT, datefmt=Logger.__LOGGER_DATEFMT))
            thandler.setLevel(self.configurations["terminal"]["level"])
            self.inner.addHandler(thandler)
        # se la stampa su file è attiva inizializzala
        if self.configurations["file"]["enabled"]:
            # genera la path del file se non esiste
            path = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Logs")
            if not os.path.exists(path):
                os.makedirs(path)
            # genera l'handler per i file e imposta livello, formatter e file rotation
            rfandler = logging.handlers.RotatingFileHandler(
                filename=os.path.join(path, "{}.log".format(self.configurations["file"]["name"])),
                mode="a",
                maxBytes=self.configurations["file"]["max_bytes"],
                backupCount=self.configurations["file"]["backup_count"]
            )
            rfandler.setFormatter(logging.Formatter(fmt=Logger.__LOGGER_FMT, datefmt=Logger.__LOGGER_DATEFMT))
            rfandler.setLevel(self.configurations["file"]["level"])
            self.inner.addHandler(rfandler)

    # CHIAMATO DA Thread.start(self)
    def run(self):
        begin = time.time()
        end = time.time()
        while self:  # adesso il wait si trova all'inizio
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))
            begin = time.time()
            try:
                # ottieni le stringhe
                self.strings_mutex.acquire()
                now_strings = self.strings.copy()
                self.strings.clear()
                self.strings_mutex.release()
                # passa al logger ogni stringa
                for (string, level) in now_strings:
                    self.inner.log(level, string)
            except Exception as e:
                self.inner.log(logging.ERROR, e)  # logga l'errore
                self.valid = False  # invalida il logger
            end = time.time()

    # ERRORE CRITICO
    def err(self, name, value):
        self.__generate_string(logging.ERROR, name, value)

    # ERRORE NON CRITICO
    def warn(self, name, value):
        self.__generate_string(logging.WARNING, name, value)

    # INFORMAZIONE UTILE
    def info(self, name, value):
        self.__generate_string(logging.INFO, name, value)

    # INFORMAZIONE UTILE SOLO PER IL DEBUGGING
    def debug(self, name, value):
        self.__generate_string(logging.DEBUG, name, value)

    # FUNZIONE NASCOSTA CHE GENERA UNA STRINGA PER IL LOGGER
    def __generate_string(self, level, name, value):
        self.strings_mutex.acquire()
        self.strings.append(("{}: {}".format(name, value), level))
        self.strings_mutex.release()

    # VALIDA LA SESSIONE
    def start(self):
        self.valid = True
        Thread.start(self)

    # INVALIDA LA SESSIONE
    def join(self, timeout=...):
        self.valid = False
        Thread.join(self)

    # VERIFICA SE IL LOGGER E' ANCORA VALIDO O MENO
    def __bool__(self):
        return self.valid
