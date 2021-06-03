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
from Utils.Logger import get_logger


# LA CLASSE ESTESA DA TUTTI I SENSORI
class AbstractSensor(Thread):

    # INIZIALIZZA LE BASI DEL SENSORE
    def __init__(self, sensor_name):
        Thread.__init__(self)
        self.is_active = False
        self.measurements = {}
        self.sensor_name = sensor_name
        self.measurements_mutex = Lock()
        self.configurations = Configs.load(sensor_name)
        self.logger = get_logger(self.configurations["logger"])

    # METODO CHIAMATO OGNI [pooling_rate]
    def read(self):
        self.logger.warn(self.sensor_name, "AbstractSensor.read(self) not implemented!")

    # CHIAMATO DA Thread.start(self)
    def run(self):
        self.logger.info(self.sensor_name, "Started sensor")
        while self.is_active:
            begin = time.time()
            self.read()
            end = time.time()
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))
            else:
                self.logger.warn(self.sensor_name, "Pooling rate is lower of {} seconds".format(end - begin))
        self.logger.info(self.sensor_name, "Stopped sensor")

    # RENDE ATTIVO IL SENSORE
    def start(self):
        self.is_active = True
        Thread.start(self)

    # DISATTIVA IL SENSORE E FA IL JOIN DEL THREAD DEL SENSORE
    def join(self, timeout=...):
        self.is_active = False
        Thread.join(self)

    # OTTIENE LE ULTIME MISURAZIONI
    def get_measurements(self):
        self.measurements_mutex.acquire()
        measurements = self.measurements.copy()
        self.measurements_mutex.release()
        return measurements

    # VEDE SE IL SENSORE E' ATTIVO
    def is_active(self):
        return self.is_active

    # SEMPRE FALSO, NECESSITA LA SOVRASCRITTURA
    def __bool__(self):
        return False
