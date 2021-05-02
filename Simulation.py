# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# AMBIENT IMPORT
from Utils.AbstractClient import AbstractClient


class SimulationClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "Simulation")

    def publish(self):
        if self.client.is_connected():
            self.logger.info(self.client_name, "Send data")


if __name__ == "__main__":
    client = SimulationClient()
    client.start()
