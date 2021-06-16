#!/usr/bin/env python3
# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import simplejson as json

# AMBIENT IMPORT
from Utils.AbstractClient import AbstractClient
from VodafoneCrowdCell import VodafoneCrowdCell


class VodafoneClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "VodafoneClient")
        self.crowd_cell = VodafoneCrowdCell()

    def publish(self):
        # ottieni le misurazioni e loggale per vedere se è tutto ok
        measurements = self.crowd_cell.get_measurements()
        self.logger.debug(self.client_name, measurements)
        # manda su thingsboard
        if self.client.is_connected() and len(measurements) > 0:
            # measurements è una lista non più un dizionario
            # quindi si deve fare questa operazione per ogni elemento
            for item in measurements:
                # crea il json con le misurazioni
                json_measurements = json.dumps(item)
                # verifica se l'array è pieno
                if len(json_measurements) > 0:
                    # send to thingsboard
                    self.client.publish(self.configurations["topic"], json_measurements, self.configurations["qos"])
                    # log
                    self.logger.info(self.client_name, "Sent data to Thingsboard")
        else:
            # non ci sono state misurazioni
            self.logger.info(self.client, "No measurements")

    def start(self):
        AbstractClient.start(self)
        self.crowd_cell.start()

    def join(self, timeout=...):
        AbstractClient.join(self)
        self.crowd_cell.join()

    def __bool__(self):
        return AbstractClient.__bool__(self) and bool(self.crowd_cell)


if __name__ == "__main__":
    x = VodafoneClient()
    x.start()
    x.join()
