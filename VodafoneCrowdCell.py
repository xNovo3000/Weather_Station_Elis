# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import os

import simplejson
import simplejson as json
import requests

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor

# GET ROOT PATH
root_path = os.path.join(os.path.dirname(__file__), "Files", "FakeData")


# VODAFONE CROWD CELL SENSOR
class VodafoneCrowdCell(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "VodafoneCrowdCell")

    def read(self):
        # FASE 1: LOGIN
        try:  # prova a fare la richiesta di login
            response = requests.post(
                url="https://api.analytics.vodafone.it/api",
                json={
                    "accessKey": self.configurations["access_key"],
                    "secretKey": self.configurations["secret_key"]
                }
            )
        except requests.RequestException as e:  # qualcosa è andato storto
            self.logger.err(self.sensor_name, e)
            return
        # verifica se la risposta e' 200 ok
        if response.status_code != 200:
            self.logger.err(self.sensor_name, "Login request status code {}".format(response.status_code))
            return
        # estrai il json
        try:
            response_json = response.json()
        except simplejson.JSONDecodeError as e:  # la risposta non ha un json
            self.logger.err(self.sensor_name, e)
            return
        # verifica che la risposta sia ok
        if not response_json["status"] or response_json["responseStatus"] != 200:  # non ok
            # TODO: FARE LA PROSSIMA RICHESTA MOLTO PRIMA DEL SOLITO
            self.logger.err(self.sensor_name, "Response status: {}".format(response_json["responseStatus"]))
            self.logger.err(self.sensor_name, "Message: {}".format(response_json["message"]))
            return
        # estrai il token verificando che ci sia
        if "token" not in response_json:
            self.logger.err(self.sensor_name, "Login response doesn't contain the token")
            return
        token = response_json["token"]
        # fai la seconda richiesta 'cicciona'


# stub main
if __name__ == "__main__":
    VodafoneCrowdCell().start()
