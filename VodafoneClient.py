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
        # ottieni le misurazioni
        measurements = self.crowd_cell.get_measurements()
        # manda su thingsboard
        if self.client.is_connected():
            # crea il json con le misurazioni
            json_measuremets = json.dumps(measurements)
            # send to thingsboard
            self.client.publish(self.configurations["topic"], json_measuremets, self.configurations["qos"])
            # log
            self.logger.info(self.client_name, json_measuremets)

    def start(self):
        if self.crowd_cell:
            self.crowd_cell.start()
            AbstractClient.start(self)
        else:
            self.logger.err(self.client_name, "The VodafoneCrowdCell doesn't work correctly")


if __name__ == "__main__":
    x = VodafoneClient()
    x.start()
