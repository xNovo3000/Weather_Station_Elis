# encoding: UTF-8

"""
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
from gpiozero import CPUTemperature

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


class InternalSensors(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "InternalSensors")
        self.measurements["cpu_temperature"] = 0.0
        try:
            self.cpu_temperature_reader = CPUTemperature()
        except Exception as e:
            self.cpu_temperature_reader = None
            self.logger.err(self.sensor_name, e)

    def read(self):
        temp = self.cpu_temperature_reader.temperature
        self.logger.debug(self.sensor_name, "CPU Temperature: {}".format(temp))
        self.measurements_mutex.acquire()
        self.measurements["cpu_temperature"] = temp
        self.measurements_mutex.release()

    def __bool__(self):
        return AbstractSensor.__bool__(self) and self.cpu_temperature_reader is not None
