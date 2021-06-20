#!/usr/bin/env python3
# encoding: UTF-8

"""
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import simplejson as json

# AMBIENT IMPORT
from Utils.AbstractClient import AbstractClient
from InternalSensors import InternalSensors


class InternalClient(AbstractClient):

    def __init__(self):
        AbstractClient.__init__(self, "InternalClient")
        self.internal_sensors = InternalSensors()

    def publish(self):
        measurements = self.internal_sensors.get_measurements()
        if self.client.is_connected():
            self.client.publish(self.configurations["topic"], json.dumps(measurements), self.configurations["qos"])
            self.logger.info(self.client_name, "Data sent to thingsboard")

    def start(self):
        AbstractClient.start(self)
        self.internal_sensors.start()

    def join(self, timeout=...):
        AbstractClient.join(self)
        self.internal_sensors.join()

    def __bool__(self):
        return AbstractClient.__bool__(self) and bool(self.internal_sensors)


if __name__ == "__main__":
    x = InternalClient()
    x.start()
    x.join()
