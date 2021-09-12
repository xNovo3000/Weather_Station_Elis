# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
from datetime import datetime, timedelta

import pytz
import requests

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# CROWD CELL
class VodafoneSimplifiedCrowdCell(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "VodafoneEnhancedCrowdCell")
        self.date_format = "%Y%m%d"
        self.dimensions = ["age", "gender", "nationality", "homeDistance", "country",
                           "workDistance", "region", "municipality", "zip", "province"]
        self.measurements = []
        self.device_id = self.configurations["device_id"]

    def read(self):
        # FASE 1 -> effettua il login a Thingsboard
        thingsboard_token = self.phase_1()
        # FASE 2 -> ottieni il timestamp dagli ultimi dati di Thingsboard
        timestamp = self.phase_2(thingsboard_token)
        # FASE 3 -> effettua il login a Vodafone Analytics e ottieni il token
        vodafone_token = self.phase_3()
        # FASE 4 -> ottieni l'id del pdv dagli stores di Vodafone
        pdv_id = self.phase_4(vodafone_token)
        # FASE 5 -> usando il timestamp e il pdv chiedi dati fino ad oggi
        #        -> per ogni dato ricevuto, inseriscilo in self.measurements
        self.phase_5(vodafone_token, pdv_id, timestamp)
        self.logger.info(self.sensor_name, self.measurements)

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
            self.logger.debug(
                self.sensor_name, "Risposta ricevuta con successo".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch and get token
        json_response = response.json()
        if "token" in json_response:
            token = json_response["token"]
            self.logger.debug(self.sensor_name, "Token Thingsboard: {}".format(token))
            return token
        else:
            raise ValueError("Token non presente nella risposta")

    def phase_2(self, thingsboard_token):
        # phase 2 begin
        self.logger.debug(self.sensor_name, "Inizio fase 2")
        # generate url
        request_url = "https://{}/api/plugins/telemetry/DEVICE/{}/values/timeseries" \
            .format(self.configurations["host"], self.device_id)
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.get(
            url=request_url,
            headers={
                "X-Authorization": "Bearer {}".format(thingsboard_token)
            },
            params={
                "keys": "visitors"
            }
        )
        # check response
        if response.status_code == 200:
            self.logger.debug(
                self.sensor_name, "Risposta ricevuta con successo".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if json_response["visite"][0]["value"] is not None:
            self.logger.debug(self.sensor_name, "Ci sono dati. Inizio dal giorno successivo")
            return datetime.fromtimestamp(json_response["visite"][0]["ts"] / 1000) + timedelta(days=1)
        else:  # days_back giorni prima
            self.logger.debug(
                self.sensor_name,
                "Non ci sono dati. Inizierò da {} giorni prima".format(self.configurations["days_back"])
            )
            return datetime.now() - timedelta(days=self.configurations["days_back"])

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
            self.logger.debug(
                self.sensor_name,
                "Risposta ricevuta con successo".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if "token" in json_response:
            token = json_response["token"]
            self.logger.debug(self.sensor_name, "Token Vodafone: {}".format(token))
            return token
        else:
            raise ValueError("Token non presente nella risposta")

    def phase_4(self, vodafone_token):
        # phase 4 begin
        self.logger.debug(self.sensor_name, "Inizio fase 4")
        # generate url
        request_url = "{}/retail/stores".format(self.configurations["base_url"])
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.post(
            url=request_url,
            headers={
                "X-API-Key": vodafone_token
            }
        )
        # check response
        if response.status_code == 200:
            self.logger.debug(
                self.sensor_name, "Risposta ricevuta con successo".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if len(json_response["stores"]) > 0:
            pdv_id = json_response["stores"][0]["id"]
            self.logger.debug(self.sensor_name, "ID PDV: {}".format(pdv_id))
            return pdv_id
        else:
            raise ValueError("Nessun PDV registrato")

    def phase_5(self, vodafone_token, pdv_id, timestamp):
        # phase 5 begin
        self.logger.debug(self.sensor_name, "Inizio fase 5")
        # generate url
        request_url = "{}/retail/daily".format(self.configurations["base_url"])
        # for every day
        while True:
            # delta seconds
            number_of_cluster = 0
            # log INDOOR
            self.logger.debug(
                self.sensor_name, "Verifico la presenza di dati INDOOR per la data {}".format(timestamp)
            )
            # generate INDOOR request
            response = requests.post(
                url=request_url,
                headers={
                    "X-API-Key": vodafone_token
                },
                json={
                    "area": "INDOOR",
                    "pdvId": pdv_id,
                    "date": timestamp.strftime(self.date_format),
                    "dimensionsList": ["gender"],
                    "filtersList": [],
                    "page": 1
                }
            )
            # check response
            if response.status_code == 200:
                self.logger.debug(self.sensor_name, "Risposta ricevuta con successo")
            else:
                raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                    response.status_code, response.text
                ))
            # dispatch
            json_response = response.json()
            if json_response["pages"] == 0:
                self.logger.debug(self.sensor_name, "Non sembrano esserci dati")
                if timestamp < datetime.now():
                    timestamp += timedelta(days=1)
                    self.logger.debug(self.sensor_name, "Passo al giorno successivo")
                    continue
                else:
                    break
            # get data
            for data in json_response["data"]:
                # ensure there are all dimensions
                for dimension in self.dimensions:
                    if dimension not in data or data[dimension] is None:
                        data[dimension] = "null"
                # "*" avoider
                if data["visits"] == "*":
                    data["visits"] = 1
                if data["visitors"] == "*":
                    data["visitors"] = data["visits"]
                # remove useless data
                data.pop("date")
                data.pop("pdvId")
                data.pop("pdvName")
                # generate ts
                ts = timestamp.astimezone(pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
                ts += timedelta(seconds=number_of_cluster)
                # add to the measurements
                self.measurements_mutex.acquire()
                self.measurements.append({
                    "ts": ts.timestamp() * 1000,
                    "values": data
                })
                self.measurements_mutex.release()
                # increase seconds
                number_of_cluster += 1
            # log OUTDOOR
            self.logger.debug(
                self.sensor_name, "Verifico la presenza di dati INDOOR per la data {}".format(timestamp)
            )
            # generate OUTDOOR request
            response = requests.post(
                url=request_url,
                headers={
                    "X-API-Key": vodafone_token
                },
                json={
                    "area": "OUTDOOR",
                    "pdvId": pdv_id,
                    "date": timestamp.strftime(self.date_format),
                    "dimensionsList": ["gender"],
                    "filtersList": [],
                    "page": 1
                }
            )
            # check response
            if response.status_code == 200:
                self.logger.debug(self.sensor_name, "Risposta ricevuta con successo")
            else:
                raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                    response.status_code, response.text
                ))
            # dispatch
            json_response = response.json()
            if json_response["pages"] == 0:
                self.logger.debug(self.sensor_name, "Non sembrano esserci dati")
                if timestamp < datetime.now():
                    timestamp += timedelta(days=1)
                    self.logger.debug(self.sensor_name, "Passo al giorno successivo")
                    continue
                else:
                    break
            # get data
            for data in json_response["data"]:
                # ensure there are all dimensions
                for dimension in self.dimensions:
                    if dimension not in data or data[dimension] is None:
                        data[dimension] = "null"
                # "*" avoider
                if data["visits"] == "*":
                    data["visits"] = 1
                if data["visitors"] == "*":
                    data["visitors"] = data["visits"]
                # remove useless data
                data.pop("date")
                data.pop("pdvId")
                data.pop("pdvName")
                # generate ts
                ts = timestamp.astimezone(pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
                ts += timedelta(seconds=number_of_cluster)
                # add to the measurements
                self.measurements_mutex.acquire()
                self.measurements.append({
                    "ts": ts.timestamp() * 1000,
                    "values": data
                })
                self.measurements_mutex.release()
                # increase seconds
                number_of_cluster += 1
            # add one day to timestamp
            timestamp += timedelta(days=1)

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
