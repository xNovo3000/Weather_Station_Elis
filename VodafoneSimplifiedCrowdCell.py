# encoding: UTF-8

"""
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

    def __init__(self, area):
        AbstractSensor.__init__(self, "VodafoneSimplifiedCrowdCell")
        self.date_format = "%Y%m%d"
        self.dimensions = ["age", "gender", "nationality", "homeDistance", "country",
                           "workDistance", "region", "municipality", "province"]
        self.measurements = []
        self.area = area
        if area == "INDOOR":
            self.device_id = self.configurations["indoor_device_id"]
        elif area == "OUTDOOR":
            self.device_id = self.configurations["outdoor_device_id"]
        else:
            self.device_id = None

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
        self.logger.info(self.sensor_name + "-" + self.area, "Misurazioni misurate con successo")

    def phase_1(self):
        # phase 1 begin
        self.logger.info(self.sensor_name + "-" + self.area, "Inizio fase 1")
        # generate url
        request_url = "https://{}/api/auth/login".format(self.configurations["host"])
        self.logger.info(self.sensor_name + "-" + self.area, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.post(url=request_url, json={
            "username": self.configurations["username"],
            "password": self.configurations["password"]
        })
        # check response
        if response.status_code == 200:
            self.logger.info(
                self.sensor_name + "-" + self.area, "Risposta ricevuta con successo: {}".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch and get token
        json_response = response.json()
        if "token" in json_response:
            token = json_response["token"]
            self.logger.debug(self.sensor_name + "-" + self.area, "Token Thingsboard: {}".format(token))
            return token
        else:
            raise ValueError("Token non presente nella risposta")

    def phase_2(self, thingsboard_token):
        # phase 2 begin
        self.logger.info(self.sensor_name + "-" + self.area, "Inizio fase 2")
        # generate url
        request_url = "https://{}/api/plugins/telemetry/DEVICE/{}/values/timeseries" \
            .format(self.configurations["host"], self.device_id)
        self.logger.info(self.sensor_name + "-" + self.area, "Invio richiesta a: {}".format(request_url))
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
            self.logger.info(
                self.sensor_name + "-" + self.area, "Risposta ricevuta con successo {}".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if "visitors" in json_response and json_response["visitors"][0]["value"] is not None:
            self.logger.info(self.sensor_name + "-" + self.area, "Ci sono dati. Inizio dal giorno successivo")
            return datetime.fromtimestamp(json_response["visitors"][0]["ts"] / 1000) + timedelta(days=1)
        else:  # days_back giorni prima
            self.logger.info(
                self.sensor_name + "-" + self.area,
                "Non ci sono dati. Inizier?? da {} giorni prima".format(self.configurations["days_back"])
            )
            return datetime.now() - timedelta(days=self.configurations["days_back"])

    def phase_3(self):
        # phase 3 begin
        self.logger.info(self.sensor_name + "-" + self.area, "Inizio fase 3")
        # generate url
        request_url = "{}/userbackend/login".format(self.configurations["base_url"])
        self.logger.info(self.sensor_name + "-" + self.area, "Invio richiesta a: {}".format(request_url))
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
            self.logger.info(
                self.sensor_name + "-" + self.area,
                "Risposta ricevuta con successo {}".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if "token" in json_response:
            token = json_response["token"]
            self.logger.debug(self.sensor_name + "-" + self.area, "Token Vodafone: {}".format(token))
            return token
        else:
            raise ValueError("Token non presente nella risposta")

    def phase_4(self, vodafone_token):
        # phase 4 begin
        self.logger.info(self.sensor_name + "-" + self.area, "Inizio fase 4")
        # generate url
        request_url = "{}/retail/stores".format(self.configurations["base_url"])
        self.logger.info(self.sensor_name + "-" + self.area, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.post(
            url=request_url,
            headers={
                "X-API-Key": vodafone_token
            }
        )
        # check response
        if response.status_code == 200:
            self.logger.info(
                self.sensor_name + "-" + self.area, "Risposta ricevuta con successo".format(response.status_code)
            )
        else:
            raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                response.status_code, response.text
            ))
        # dispatch
        json_response = response.json()
        if len(json_response["stores"]) > 0:
            pdv_id = json_response["stores"][0]["id"]
            self.logger.debug(self.sensor_name + "-" + self.area, "ID PDV: {}".format(pdv_id))
            return pdv_id
        else:
            raise ValueError("Nessun PDV registrato")

    def phase_5(self, vodafone_token, pdv_id, timestamp):
        # phase 5 begin
        self.logger.info(self.sensor_name + "-" + self.area, "Inizio fase 5")
        # generate url
        request_url = "{}/retail/daily".format(self.configurations["base_url"])
        # for every day
        while True:
            # log
            self.logger.info(
                self.sensor_name + "-" + self.area, "Verifico la presenza di dati {} per la data {}".format(self.area, timestamp)
            )
            # delta seconds
            delta_seconds = 0
            # generate INDOOR request
            response = requests.post(
                url=request_url,
                headers={
                    "X-API-Key": vodafone_token
                },
                json={
                    "area": self.area,
                    "pdvId": pdv_id,
                    "date": timestamp.strftime(self.date_format),
                    "dimensionsList": self.dimensions,
                    "filtersList": [],
                    "page": 1
                }
            )
            # check response
            if response.status_code == 200:
                self.logger.info(self.sensor_name + "-" + self.area, "Risposta ricevuta con successo")
            else:
                raise ConnectionError("Risposta ricevuta con errore. Codice: {}. Messaggio: {}".format(
                    response.status_code, response.text
                ))
            # dispatch
            json_response = response.json()
            if json_response["pages"] == 0:
                self.logger.info(self.sensor_name + "-" + self.area, "Non sembrano esserci dati")
                if timestamp < datetime.now():
                    timestamp += timedelta(days=1)
                    self.logger.info(self.sensor_name + "-" + self.area, "Passo al giorno successivo")
                    continue
                else:
                    break
            else:
                self.logger.info(self.sensor_name + "-" + self.area, "Ci sono dati, ?? il momento di spacchettarli")
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
                if data["totalDwellTime"] == "*":
                    data["totalDwellTime"] = 6000 if self.area == "INDOOR" else 600
                # remove useless data
                data.pop("area")
                data.pop("date")
                data.pop("pdvId")
                data.pop("pdvName")
                # generate ts
                ts = timestamp.astimezone(pytz.utc).replace(hour=12, minute=0, second=0, microsecond=0)
                ts += timedelta(seconds=delta_seconds)
                # add to the measurements
                self.measurements_mutex.acquire()
                self.measurements.append({
                    "ts": ts.timestamp() * 1000,
                    "values": data
                })
                self.measurements_mutex.release()
                # increase
                delta_seconds += 1
            # add one day to timestamp
            timestamp += timedelta(days=1)

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
