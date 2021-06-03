# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json

# AMBIENT IMPORT
from BME280 import BME280
from DS18B20 import DS18B20
from WSA80422 import WSA80422
from Utils.AbstractClient import AbstractClient


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
        # verifica se il client è connesso
        if self.client.is_connected():
            # send to thingsboard
            self.client.publish(self.configurations["topic"], json.dumps(measuraments), self.configurations["qos"])
            # avvisa che sono stati inviati dati a TB
            self.logger.info(self.client_name, "Data sent to Thingsboard")

    def start(self):
        AbstractClient.start(self)
        self.bme280.start()
        self.ds18b20.start()
        self.wsa80422.start()

    def join(self, timeout=...):
        AbstractClient.join(self, timeout)
        self.bme280.join()
        self.ds18b20.join()
        self.wsa80422.join()

    def __bool__(self):
        s1 = bool(self.bme280)
        s2 = bool(self.ds18b20)
        s3 = bool(self.wsa80422)
        return AbstractClient.__bool__(self) and s1 and s2 and s3


if __name__ == "__main__":
    client = WeatherStationClient()
    client.start()
    client.join()
