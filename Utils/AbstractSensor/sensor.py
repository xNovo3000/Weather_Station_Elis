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

    # INIZIALIZZA LE VARIABILI DEL SENSORE
    def __init__(self, sensor_name):
        Thread.__init__(self)
        self.can_run = True
        self.measurements = {}
        self.sensor_name = sensor_name
        self.measurements_mutex = Lock()
        self.configurations = Configs.load(sensor_name)
        self.logger = get_logger(self.configurations["logger"])

    # METODO CHIAMATO OGNI [pooling_rate], DA IMPLEMENTARE OBBLIGATORIAMENTE
    def on_read(self):
        self.logger.warn(self.sensor_name, "AbstractSensor.on_read(self) not implemented!")

    # METODO CHIAMATO QUANDO IL SENSORE VIENE STOPPATO
    def on_stop(self):
        self.logger.info(self.sensor_name, "AbstractSensor.on_stop(self) not implemented!")

    # CHIAMATO DA Thread.start(self)
    def run(self):
        # avvisa che il sensore è partito
        self.logger.info(self.sensor_name, "Started sensor")
        # finché lo stato del sensore è ok (True)
        while self:
            begin = time.time()
            try:
                self.on_read()
            except Exception as e:
                self.logger.err(self.sensor_name, "A {} error occured: {}".format(type(e), e))
                self.can_run = False
                begin = time.time()  # forza l'uscita dalla funzione
            end = time.time()
            if (end - begin) < self.configurations["pooling_rate"]:
                time.sleep(self.configurations["pooling_rate"] - (end - begin))
            else:
                self.logger.warn(self.sensor_name, "Pooling rate is lower of {} seconds".format(end - begin))
        # il sensore è stato fermato (tramite errore o tramite utente), avvisare
        self.logger.info(self.sensor_name, "Stopped sensor")
        self.on_stop()

    # PRIMA DI CHIAMARE IL VERO JOIN INVALIDA IL SENSORE
    def join(self, timeout=...):
        self.can_run = False
        AbstractSensor.join(self)

    # OTTIENE LE ULTIME MISURAZIONI
    def get_measurements(self):
        self.measurements_mutex.acquire()  # blocca la guardia
        measurements = self.measurements.copy()  # copia le misurazioni
        self.measurements_mutex.release()  # sblocca la guardia
        return measurements

    # VERIFICA SE IL SENSORE SI TROVA IN UNO STATO ACCETTABILE PER L'ESECUZIONE
    def __bool__(self):
        return self.can_run
