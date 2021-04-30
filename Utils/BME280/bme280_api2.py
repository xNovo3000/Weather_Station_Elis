# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import bme280
import smbus2

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger import Logger


# LA CLASSE CHE GESTISCE UN SENORE BME280
class BME280:

    # INIT
    def __init__(self):
        self.configs = Configs.load("bme280.json")
        self.logger = Logger(file_name=self.configs["log_file"])
        try:
            self.bus = smbus2.SMBus(self.configs["port"])
            bme280.load_calibration_params(self.bus, self.configs["address"])
        except Exception as e:
            self.bus = None
            self.logger.err("BME280", "Init error: {}".format(e))

    # PROVA AD OTTENERE I DATI DAL SENSORE
    def get_measurements(self):
        if self:
            try:
                bme280_data = bme280.sample(self.bus, self.configs["address"])
                measurements = {
                    "humidity": bme280_data.humidity,
                    "pressure": bme280_data.pressure,
                    "ambient_temperature": bme280_data.temperature
                }
                self.logger.info("BME280", "{}".format(json.dumps(measurements)))
                return measurements
            except Exception as e:
                self.logger.err("BME280", "Measuraments read error {}".format(e))
                return {}
        else:
            self.logger.err("BME280", "Bus is None")

    # VERIFICA SE IL SENSORE E' STATO INIZIALIZZATO CORRETTAMENTE
    def __bool__(self):
        return self.bus is not None
