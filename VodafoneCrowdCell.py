# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import os
import simplejson as json
import requests
from datetime import datetime

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor

# GET ROOT PATH
root_path = os.path.join(os.path.dirname(__file__), "Files", "FakeData")


# VODAFONE CROWD CELL SENSOR
class VodafoneCrowdCell(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "VodafoneCrowdCell")
        self.__reset_data()

    def __reset_data(self):
        self.visitatori_italiani = 0
        self.visitatori_stranieri = 0
        self.transiti = 0
        self.maschi = 0
        self.femmine = 0
        self.eta_media = 0
        self.distanza_lavoro_media = 0
        self.distanza_casa_media = 0

    def read(self):
        # FASE 1: LOGIN
        try:  # prova a fare la richiesta di login
            response = requests.post(
                url="{}userbackend/login".format(self.configurations["base_url"]),
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
        # estrai il json
        try:
            response_json = response.json()
        except json.JSONDecodeError as e:  # la risposta non ha un json
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
        now_string = datetime.now().strftime('%Y%m%d')
        total_pages = 1
        actual_page = 1
        while actual_page <= total_pages:
            try:  # prova a fare la richiesta di dati
                response = requests.post(
                    url="{}retail/daily".format(self.configurations["base_url"]),
                    headers={
                        "X-API-Key": token
                    },
                    json={
                        "date": now_string,
                        "area": "INDOOR",
                        "pdvId": -1,
                        "page": actual_page,
                        "dimensionsList": [
                            "gender", "age", "nationality", "workDistance", "homeDistance", "visits",
                            "visitors"
                        ]
                    }
                )
            except requests.RequestException as e:  # qualcosa è andato storto
                self.logger.err(self.sensor_name, e)
                return
            # verifica se la risposta e' 200 ok
            if response.status_code != 200:
                self.logger.err(self.sensor_name, "Login request status code {}".format(response.status_code))
            # estrai il json
            try:
                response_json = response.json()
            except json.JSONDecodeError as e:  # la risposta non ha un json
                self.logger.err(self.sensor_name, e)
                return
            # verifica che la risposta sia ok
            if not response_json["status"] or response_json["responseStatus"] != 200:  # non ok
                # TODO: FARE LA PROSSIMA RICHESTA MOLTO PRIMA DEL SOLITO
                self.logger.err(self.sensor_name, "Response status: {}".format(response_json["responseStatus"]))
                self.logger.err(self.sensor_name, "Message: {}".format(response_json["message"]))
                return
            total_pages = response_json["pages"]
            # per ogni 'oggetto ritornato'
            for val in response_json["data"]:
                # calcola variabili semplici
                self.transiti += val["visits"]
                # calcola se ita o stranieri
                if val["nationality"] == "ITALIANS":
                    self.visitatori_italiani += val["visitors"]
                else:
                    self.visitatori_stranieri += val["visitors"]
                # calcola sesso
                if val["gender"] == "M":
                    self.maschi += val["visitors"]
                else:
                    self.femmine += val["visitors"]
                # calcola eta media
                if val["age"] == "15-25":
                    self.eta_media += 20 * val["visitors"]
                elif val["age"] == "25-35":
                    self.eta_media += 30 * val["visitors"]
                elif val["age"] == "35-45":
                    self.eta_media += 40 * val["visitors"]
                elif val["age"] == "45-55":
                    self.eta_media += 50 * val["visitors"]
                elif val["age"] == "55-65":
                    self.eta_media += 60 * val["visitors"]
                else:  # TODO: gestire quando viene ritornato null
                    self.eta_media += 70 * val["visitors"]
                # calcola distanza dal luogo di casa
                if val["homeDistance"] == "000-010":
                    self.distanza_casa_media += 5 * val["visitors"]
                elif val["homeDistance"] == "010-020":
                    self.distanza_casa_media += 15 * val["visitors"]
                elif val["homeDistance"] == "020-030":
                    self.distanza_casa_media += 25 * val["visitors"]
                elif val["homeDistance"] == "030-040":
                    self.distanza_casa_media += 35 * val["visitors"]
                elif val["homeDistance"] == "040-050":
                    self.distanza_casa_media += 45 * val["visitors"]
                else:  # TODO: gestire quando viene ritornato null
                    self.distanza_casa_media += 55 * val["visitors"]
                # calcola distanza dal luogo di lavoro
                if val["workDistance"] == "000-010":
                    self.distanza_lavoro_media += 5 * val["visitors"]
                elif val["workDistance"] == "010-020":
                    self.distanza_lavoro_media += 15 * val["visitors"]
                elif val["workDistance"] == "020-030":
                    self.distanza_lavoro_media += 25 * val["visitors"]
                elif val["workDistance"] == "030-040":
                    self.distanza_lavoro_media += 35 * val["visitors"]
                elif val["workDistance"] == "040-050":
                    self.distanza_lavoro_media += 45 * val["visitors"]
                else:  # TODO: gestire quando viene ritornato null
                    self.distanza_lavoro_media += 55 * val["visitors"]
            actual_page += 1
        # calcola la media complessiva
        self.eta_media /= (self.visitatori_italiani + self.visitatori_stranieri)
        self.distanza_lavoro_media /= (self.visitatori_italiani + self.visitatori_stranieri)
        self.distanza_casa_media /= (self.visitatori_italiani + self.visitatori_stranieri)
        # blocca la guardia
        self.measurements_mutex.acquire()
        # aggiorna le misurazioni
        self.measurements = {
            "visitatori_italiani": self.visitatori_italiani,
            "visitatori_stranieri": self.visitatori_stranieri,
            "transiti": self.transiti,
            "maschi": self.maschi,
            "femmine": self.femmine,
            "eta_media": self.eta_media,
            "distanza_lavoro_media": self.distanza_lavoro_media,
            "distanza_casa_media": self.distanza_casa_media
        }
        # sblocca la guardia
        self.measurements_mutex.release()
        # avvisa che le misurazioni sono state ottenute correttamente
        self.logger.info(self.sensor_name, "Got measurements correctly")
        # reimposta i dati
        self.__reset_data()

    def __bool__(self):
        return True
