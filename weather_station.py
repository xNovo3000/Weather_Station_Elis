# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import json
import time

# AMBIENT IMPORT
from Utils.Client import Client
from Utils.BME280 import BME280
from Utils.DS18B20 import DS18B20
from Utils.WSA80422 import WSA80422


# LA CLASSE CHE FA ESEGUIRE LA FUNZIONE
class WeatherStationClient(Client):

    # INIZIALIZZATORE
    def __init__(self):
        Client.__init__(self, "thingsboard.json")

    # FUNZIONE CHE TRASMETTE DATI
    def transmit_data(self):
        # init BME280 -> (humidity, pressure, ambient_temperature)
        bme280 = BME280()
        # init DS18B20 -> (ground_temperature)
        ds18b20 = DS18B20()
        # init WSA80422 -> (wind_direction_average, wind_gust, wind_speed_mean, rainfall)
        wsa80422 = WSA80422()
        # sensor checks
        if not bme280:
            self.logger.err("Weather Station", "Error loading BME280")
        if not ds18b20:
            self.logger.err("Weather Station", "Error loading DS18B20")
        if not wsa80422:
            self.logger.err("Weather Station", "Error loading WSA80422")
        # read the data
        while self.client.is_connected():
            # ottieni le misurazioni
            measuraments = {}
            if ds18b20:
                measuraments.update(ds18b20.get_measurements())
            if bme280:
                measuraments.update(bme280.get_measurements())
            if wsa80422:
                measuraments.update(wsa80422.get_measurements())
            # crea il json con i dati
            json_measuraments = json.dumps(measuraments)
            # log and send data
            self.logger.info("Data", json_measuraments)
            # TODO: self.client.publish('v1/devices/me/telemetry', json_measuraments, self.configs["qos"])
            time.sleep(self.configs["publish_time"])
        self.logger.warn("Weather Station", "Stopping publishing data")


if __name__ == "__main__":
    client = WeatherStationClient()
    client.connect()
