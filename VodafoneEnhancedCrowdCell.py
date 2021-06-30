# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
from datetime import datetime, timedelta
import requests

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# CROWD CELL
class VodafoneEnhancedCrowdCell(AbstractSensor):

    def __init__(self, data_type):
        AbstractSensor.__init__(self, "VodafoneEnhancedCrowdCell")
        self.data_type = data_type
        self.measurements = []

    def read(self):
        # FASE 1 -> effettua il login a Thingsboard
        thingsboard_token = self.phase_1()
        # FASE 2 -> ottieni il timestamp dagli ultimi dati di Thingsboard
        timestamp = self.phase_2(thingsboard_token)
        # FASE 3 -> effettua il login a Vodafone Analytics e ottieni il token
        vodafone_token = self.phase_3()
        # TODO: FASE 4 -> ottieni l'id del pdv dagli stores di Vodafone
        # TODO: FASE 5 -> usando il timestamp e il pdv chiedi dati fino ad oggi
        # TODO:        -> per ogni dato ricevuto, inseriscilo in self.measurements
        self.logger.debug(self.sensor_name, "Reading")

    def phase_1(self):
        # phase 1 begin
        self.logger.debug(self.sensor_name, "Inizio fase 1")
        # generate url
        request_url = "https://{}/api/auth/login".format(self.configurations["host"])
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.post(url=request_url, json={
            "username": self.configurations["username"],
            "password": self.configurations["password"]
        })
        # check response
        if response.status_code == 200:
            self.logger.debug(self.sensor_name, "Risposta ricevuta con successo".format(response.status_code))
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch and get token
        json_response = response.json()
        return json_response["token"]

    def phase_2(self, token):
        # phase 2 begin
        self.logger.debug(self.sensor_name, "Inizio fase 2")
        # generate url
        request_url = "https://{}/api/plugins/telemetry/DEVICE/{}/values/timeseries"\
            .format(self.configurations["host"], self.get_device_id())
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.get(
            url=request_url,
            headers={
                "X-Authorization": token
            },
            params={
                "keys": "visite"
            }
        )
        # check response
        if response.status_code == 200:
            self.logger.debug(self.sensor_name, "Risposta ricevuta con successo".format(response.status_code))
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if json_response["visite"][0]["value"] is not None:
            self.logger.debug(self.sensor_name, "Ci sono dati. Inizio dal giorno successivo")
            return datetime.fromtimestamp(json_response["visite"][0]["ts"]) + timedelta(days=1)
        else:  # 90 giorni prima
            self.logger.debug(self.sensor_name, "Non ci sono dati. Inizierò da 90 giorni prima")
            return datetime.now() - timedelta(days=90)

    def phase_3(self):
        # phase 3 begin
        self.logger.debug(self.sensor_name, "Inizio fase 3")
        # generate url
        request_url = "{}/userbackend/login".format(self.configurations["base_url"])
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.post(
            url=request_url,
            json={
                "accessKey": self.configurations["access_key"],
                "secretKey": self.configurations["secret_key"]
            },
        )
        # check response
        if response.status_code == 200:
            self.logger.debug(self.sensor_name, "Risposta ricevuta con successo".format(response.status_code))
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        return json_response["token"]

    def get_device_id(self):
        if self.data_type == "INDOOR":
            return self.configurations["indoor_device_id"]
        else:
            return self.configurations["outoor_device_id"]

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
