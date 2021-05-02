# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import time
import BME280
import smbus2

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


class SensorBME280(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "BME280")
        self.measurements["humidity"] = 0.0
        self.measurements["pressure"] = 0.0
        self.measurements["ambient_temperature"] = 0.0
        try:
            self.bus = smbus2.SMBus(self.configurations["port"])
            BME280.load_calibration_params(self.bus, self.configurations["address"])
        except Exception as e:
            self.bus = None
            self.logger.err(self.sensor_name, "Init error: {}".format(e))

    def read(self):
        if self:  # verifica se il senore è ok
            # ottieni le misurazioni
            bme280_data = BME280.sample(self.bus, self.configurations["address"])
            # salva bloccando le operazioni concorrenti
            self.measurements_mutex.acquire()
            self.measurements["humidity"] = bme280_data.humidity
            self.measurements["pressure"] = bme280_data.pressure
            self.measurements["ambient_temperature"] = bme280_data.temperature
            self.measurements_mutex.release()
            # logga le misurazioni appena ottenute
            self.logger.info(self.sensor_name, json.dumps(self.measurements))

    def __bool__(self):
        return AbstractSensor.__bool__(self) and self.bus is not None