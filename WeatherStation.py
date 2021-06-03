# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# AMBIENT IMPORT
import json

from Utils.AbstractClient import AbstractClient
from BME280 import BME280
from DS18B20 import DS18B20
from WSA80422 import WSA80422


class WeatherStationClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "WeatherStation")
        # carica i sensori
        self.bme280 = BME280()
        self.ds18b20 = DS18B20()
        self.wsa80422 = WSA80422()

    # PUBLISH
    def publish(self):
        # ottieni le misurazioni
        measuraments = {}
        measuraments.update(self.ds18b20.get_measurements())
        measuraments.update(self.bme280.get_measurements())
        measuraments.update(self.wsa80422.get_measurements())
        if self.client.is_connected():
            # crea una variabile c
            json_measuremets = json.dumps(measuraments)
            # send to thingsboard
            self.client.publish(self.configurations["topic"], json_measuremets, self.configurations["qos"])
            # log
            self.logger.info(self.client_name, json_measuremets)

    def run(self):
        # se i sensori sono ok allora il client può partire
        if self.bme280 and self.ds18b20 and self.wsa80422:
            self.bme280.start()
            self.ds18b20.start()
            self.wsa80422.start()
            AbstractClient.run(self)
        else:
            self.logger.err(self.client_name, "At least one sensor doesn't work correctly")


if __name__ == "__main__":
    client = WeatherStationClient()
    client.start()
