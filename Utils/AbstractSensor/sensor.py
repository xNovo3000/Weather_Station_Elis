# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import time
from threading import Thread, Lock

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger import get_logger, destroy_logger


# LA CLASSE ESTESA DA TUTTI I SENSORI
class AbstractSensor(Thread):

    # INIZIALIZZA LE BASI DEL SENSORE
    def __init__(self, sensor_name):
        Thread.__init__(self)
        self.valid = False
        self.measurements = {}
        self.sensor_name = sensor_name
        self.measurements_mutex = Lock()
        self.configurations = Configs.load(sensor_name)
        self.logger = get_logger(self.configurations["logger"])
        # retrocompatibilità
        if "enabled" not in self.configurations:
            self.configurations["enabled"] = True

    # METODO CHIAMATO OGNI [pooling_rate]
    def read(self):
        self.logger.warn(self.sensor_name, "AbstractSensor.read(self) not implemented!")

    # CHIAMATO DA Thread.start(self)
    def run(self):
        self.logger.info(self.sensor_name, "Started sensor")
        while self:
            begin = time.time()
            try:
                self.read()
            except Exception as e:
                self.logger.err(self.sensor_name, e)  # stampa l'errore ricevuto
                self.valid = False  # invalida il sensore
                continue  # termina a priori l'esecuzione senza passare dal via
            end = time.time()
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))
            else:
                self.logger.warn(self.sensor_name, "Pooling rate is lower of {} seconds".format(end - begin))
        self.logger.info(self.sensor_name, "Stopped sensor")

    # RENDE ATTIVO IL SENSORE
    def start(self):
        self.valid = True
        if self.configurations["enabled"]:
            Thread.start(self)
        else:
            self.logger.info(self.sensor_name, "Il sensore è stato disabilitato dal file di configurazione")

    # DISATTIVA IL SENSORE
    def join(self, timeout=...):
        self.valid = False
        if self.configurations["enabled"]:
            Thread.join(self)
        destroy_logger(self.configurations["logger"])

    # OTTIENE LE ULTIME MISURAZIONI
    def get_measurements(self):
        self.measurements_mutex.acquire()
        if self.configurations["enabled"]:
            measurements = self.measurements.copy()
        else:
            measurements = {}
        self.measurements_mutex.release()
        return measurements

    # VERIFICA SE IL SENSORE E' VALIDO
    def __bool__(self):
        return self.valid
