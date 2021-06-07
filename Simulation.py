# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# AMBIENT IMPORT
from Utils.AbstractClient import AbstractClient


class SimulationClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "Simulation")
        self.x = 0

    def publish(self):
        if self.client.is_connected():
            self.logger.info(self.client_name, "Send data")
            self.x += 1
        if self.x > 5:
            raise Exception("Test")


if __name__ == "__main__":
    client = SimulationClient()
    client.start()
    client.join()
