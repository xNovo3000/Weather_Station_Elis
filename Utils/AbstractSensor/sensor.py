# encoding: UTF-8

"""
Version: 0.3
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import time
from threading import Thread, Lock

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger import get_logger


# DEVE ESSERE ESTESA DA UN SENSORE
class AbstractSensor(Thread):

    def __init__(self, sensor_name):
        Thread.__init__(self)
        self.is_active = False
        self.measurements = {}
        self.sensor_name = sensor_name
        self.measurements_mutex = Lock()
        self.configurations = Configs.load(sensor_name)
        self.logger = get_logger(self.configurations["logger"])

    # METODO DA SOVRASCRIVERE
    def read(self):
        self.logger.warn(self.sensor_name, "AbstractSensor.read(self) not implemented!")

    # METODO ESEGUITO QUANDO IL THREAD VIENE AVVIATO
    def run(self):
        self.logger.warn(self.sensor_name, "Started sensor")
        while self.is_active:
            begin = time.time()
            self.read()
            end = time.time()
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))
            else:
                self.logger.warn(self.sensor_name, "Pooling rate is lower of {} seconds".format(end - begin))
        self.logger.warn(self.sensor_name, "Stopped sensor")

    # RENDE ATTIVO IL SENSORE
    def start(self):
        self.is_active = True
        Thread.start(self)

    # DISATTIVA IL SENSORE E FA IL JOIN DEL THREAD
    def join(self, timeout=...):
        self.is_active = False
        Thread.join(self)

    # OTTIENE LE ULTIME MISURAZIONI
    def get_measurements(self):
        self.measurements_mutex.acquire()
        measurements = self.measurements.copy()
        self.measurements_mutex.release()
        return measurements

    # VERIFICA SE IL SENSORE E' OK O NO
    def __bool__(self):
        return self.is_active
