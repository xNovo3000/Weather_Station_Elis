# encoding: UTF-8

"""
Version: 0.3
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import time
import json
import random

# AMBIENT IMPORT
from Utils.Client import Client


# LA NUOVA SOTTOCLASSE PER IL CLIENT
class SimulationClient(Client):

    def __init__(self):
        Client.__init__(self, "thingsboard.json")

    def transmit_data(self):
        while self.client.is_connected():
            # genera dati fasulli
            wind_direction_average = float(random.randint(0, 30))
            ground_temp = float(random.randint(20, 25))
            wind_gust = float(random.randint(7, 9))
            wind_speed_mean = float(random.randint(0, 10))
            rainfall = float(random.randint(0, 5))
            humidity = float(random.randint(49, 52))
            pressure = float(random.randint(1011, 1015))
            ambient_temperature = float(random.randint(20, 25))
            # crea il json con i dati
            measuraments = json.dumps({
                "wind_direction_average": wind_direction_average,
                "wind_gust": wind_gust,
                "wind_speed_mean": wind_speed_mean,
                "rainfall": rainfall,
                "ground_temp": ground_temp,
                "humidity": humidity,
                "pressure": pressure,
                "ambient_temperature": ambient_temperature
            })
            # scrivili nel log e pubblicali
            self.logger.info("Data", measuraments)
            # TODO: client.publish('v1/devices/me/telemetry', measuraments, self.configs["qos"])
            # attendi la prossima pubblicazione
            time.sleep(self.configs["publish_time"])


if __name__ == "__main__":
    client = SimulationClient()
    client.connect()
