# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# AMBIENT IMPORT
from Utils.AbstractClient import AbstractClient
from BME280 import SensorBME280
from DS18B20 import DS18B20
from WSA80422 import WSA80422


class WeatherStationClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "WeatherStation")
        # declare sensors
        self.bme280 = SensorBME280()
        self.ds18b20 = DS18B20()
        self.wsa80422 = WSA80422()

    # PUBLISH
    def publish(self):
        if self.client.is_connected():
            measuraments = {}
            measuraments.update(self.ds18b20.get_measurements())
            measuraments.update(self.bme280.get_measurements())
            measuraments.update(self.wsa80422.get_measurements())
            # self.client.publish(self.configurations["topic"], json.dumps(measurements), self.configurations["qos"])

    # RUN SENSORS WHEN CONNECTED
    def run(self):
        self.bme280.start()
        self.ds18b20.start()
        self.wsa80422.start()
        if self.bme280 and self.ds18b20 and self.wsa80422:
            AbstractClient.run(self)
        else:
            self.logger.err(self.client_name, "At least one sensor doesn't work correctly")
