# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
from datetime import datetime, timedelta
import pytz
import urllib3
import requests

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# CROWD CELL
class VodafoneEnhancedCrowdCell(AbstractSensor):

    def __init__(self, area_name):
        AbstractSensor.__init__(self, "VodafoneEnhancedCrowdCell")
        self.area_name = area_name
        self.date_format = "%Y%m%d"
        self.dimensions = ["age", "gender", "nationality", "homeDistance", "workDistance", "region", "municipality"]
        self.measurements = []
        if area_name == "INDOOR":
            self.device_id = self.configurations["indoor_device_id"]
        else:
            self.device_id = self.configurations["outdoor_device_id"]
        # [urllib3] disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
            "password": self.configurations["password"],
        }, verify=False)
        # check response
        if response.status_code == 200:
            self.logger.debug(self.sensor_name, "Risposta ricevuta con successo".format(response.status_code))
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
        request_url = "https://{}/api/plugins/telemetry/DEVICE/{}/values/timeseries"\
            .format(self.configurations["host"], self.device_id)
        self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
        # generate request
        response = requests.get(
            url=request_url,
            headers={
                "X-Authorization": "Bearer {}".format(thingsboard_token)
            },
            params={
                "keys": "visite"
            },
            verify=False
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
            return datetime.fromtimestamp(json_response["visite"][0]["ts"] / 1000) + timedelta(days=1)
        else:  # 90 giorni prima
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
            verify=False
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
            },
            verify=False
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
            # generate macro-container
            macro_container = {
                "visitatori": 0,
                "visite": 0,
                "tempo_medio_permanenza": 0,
            }
            self.logger.debug(self.sensor_name, "Verifico la presenza di dati per la data {}".format(timestamp))
            # generate request
            response = requests.post(
                url=request_url,
                headers={
                    "X-API-Key": vodafone_token
                },
                json={
                    "area": self.area_name,
                    "pdvId": pdv_id,
                    "date": timestamp.strftime(self.date_format),
                    "dimensionsList": ["gender"],
                    "filtersList": [],
                    "page": 1
                },
                verify=False
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
                break
            for data in json_response["data"]:
                # get all data
                macro_container["visite"] += data["visits"]
                macro_container["visitatori"] += data["visitors"]
                macro_container["tempo_medio_permanenza"] += data["totalDwellTime"]
            # normalize "totalDwellTime"
            macro_container["tempo_medio_permanenza"] /= macro_container["visitatori"]
            # do this for every dimension
            for dimension in self.dimensions:
                # print choosen dimension
                self.logger.debug(self.sensor_name, "Dimensione selezionata: {}".format(dimension))
                # init page numbers
                actual_page = 1
                total_pages = 1
                # do this for every page
                while actual_page <= total_pages:
                    self.logger.debug(self.sensor_name, "Invio richiesta a: {}".format(request_url))
                    # generate request
                    response = requests.post(
                        url=request_url,
                        headers={
                            "X-API-Key": vodafone_token
                        },
                        json={
                            "area": self.area_name,
                            "pdvId": pdv_id,
                            "date": timestamp.strftime(self.date_format),
                            "dimensionsList": [dimension],
                            "filtersList": [],
                            "page": 1
                        },
                        verify=False
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
                    result = self.phase_5_dispatch(dimension, response.json()["data"])
                    # add to macro-container
                    macro_container.update(result)
                    # increase page number
                    actual_page += 1
            # save data
            self.measurements_mutex.acquire()
            self.measurements.append({
                "ts": timestamp.astimezone(pytz.utc).replace(
                    hour=12, minute=0, second=0, microsecond=0
                ).timestamp() * 1000,
                "values": macro_container
            })
            self.measurements_mutex.release()
            # add one day to timestamp
            timestamp += timedelta(days=1)

    def phase_5_dispatch(self, dimension, array_data):
        # log
        self.logger.debug(self.sensor_name, "Spacchetto {}. Dati grezzi: {}".format(dimension, array_data))
        # check dimension and redirect to the function
        if dimension == "gender":
            return self.phase_5_dispatch_gender(array_data)
        elif dimension == "nationality":
            return self.phase_5_dispatch_nationality(array_data)
        elif dimension == "age":
            return self.phase_5_dispatch_age(array_data)
        elif dimension == "homeDistance":
            return self.phase_5_dispatch_distance(array_data, "casa", "homeDistance")
        elif dimension == "workDistance":
            return self.phase_5_dispatch_distance(array_data, "lavoro", "workDistance")
        elif dimension == "region":
            return self.phase_5_dispatch_region(array_data)
        elif dimension == "municipality":
            return self.phase_5_dispatch_municipality(array_data)
        else:
            raise NotImplementedError("Invalid dimension")

    @classmethod
    def phase_5_dispatch_gender(cls, array_data):
        container = {
            "visitatori_maschi": 0,
            "visitatori_femmine": 0
        }
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data["gender"] is not None:
                if data["gender"] == "M":
                    container["visitatori_maschi"] += data["visitors"]
                else:  # "F"
                    container["visitatori_femmine"] += data["visitors"]
        return container

    @classmethod
    def phase_5_dispatch_nationality(cls, array_data):
        container = {
            "visitatori_italiani": 0,
            "visitatori_stranieri": 0
        }
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data["nationality"] is not None:
                if data["nationality"] == "ITALIANS":
                    container["visitatori_italiani"] += data["visitors"]
                else:  # "FOREIGNERS"
                    container["visitatori_stranieri"] += data["visitors"]
        return container

    @classmethod
    def phase_5_dispatch_age(cls, array_data):
        container = {
            "eta_15_25": 0,
            "eta_25_35": 0,
            "eta_35_45": 0,
            "eta_45_55": 0,
            "eta_55_65": 0,
            "eta_65_plus": 0,
            "eta_media": 0
        }
        total = 0
        weight = 0
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data["age"] is not None:
                weight += data["visitors"]
                if data["age"] == "[15-25]":
                    container["eta_15_25"] += data["visitors"]
                    total += data["visitors"] * 20
                elif data["age"] == "(25-35]":
                    container["eta_25_35"] += data["visitors"]
                    total += data["visitors"] * 30
                elif data["age"] == "(35-45]":
                    container["eta_35_45"] += data["visitors"]
                    total += data["visitors"] * 40
                elif data["age"] == "(45-55]":
                    container["eta_45_55"] += data["visitors"]
                    total += data["visitors"] * 50
                elif data["age"] == "(55-65]":
                    container["eta_55_65"] += data["visitors"]
                    total += data["visitors"] * 60
                else:  # ">65"
                    container["eta_65_plus"] += data["visitors"]
                    total += data["visitors"] * 70
        if weight > 0:
            container["eta_media"] = total / weight
        return container

    @classmethod
    def phase_5_dispatch_distance(cls, array_data, spot, dimension_name):
        container = {
            "distanza_{}_0_10".format(spot): 0,
            "distanza_{}_10_20".format(spot): 0,
            "distanza_{}_20_30".format(spot): 0,
            "distanza_{}_30_40".format(spot): 0,
            "distanza_{}_40_50".format(spot): 0,
            "distanza_{}_50_plus".format(spot): 0,
            "distanza_{}_media".format(spot): 0
        }
        total = 0
        weight = 0
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data[dimension_name] is not None:
                weight += data["visitors"]
                if data[dimension_name] == "000-010":
                    container["distanza_{}_0_10".format(spot)] += data["visitors"]
                    total += data["visitors"] * 5
                elif data[dimension_name] == "010-020":
                    container["distanza_{}_10_20".format(spot)] += data["visitors"]
                    total += data["visitors"] * 15
                elif data[dimension_name] == "020-030":
                    container["distanza_{}_20_30".format(spot)] += data["visitors"]
                    total += data["visitors"] * 25
                elif data[dimension_name] == "030-040":
                    container["distanza_{}_30_40".format(spot)] += data["visitors"]
                    total += data["visitors"] * 35
                elif data[dimension_name] == "040-050":
                    container["distanza_{}_40_50".format(spot)] += data["visitors"]
                    total += data["visitors"] * 45
                else:  # "50+"
                    container["distanza_{}_50_plus".format(spot)] += data["visitors"]
                    total += data["visitors"] * 55
        if weight > 0:
            container["distanza_{}_media".format(spot)] = total / weight
        return container

    @classmethod
    def phase_5_dispatch_region(cls, array_data):
        container = {
            "regione_abruzzo": 0,
            "regione_basilicata": 0,
            "regione_calabria": 0,
            "regione_campania": 0,
            "regione_emilia_romagna": 0,
            "regione_friuli_venezia_giulia": 0,
            "regione_lazio": 0,
            "regione_liguria": 0,
            "regione_lombardia": 0,
            "regione_marche": 0,
            "regione_molise": 0,
            "regione_piemonte": 0,
            "regione_puglia": 0,
            "regione_sardegna": 0,
            "regione_sicilia": 0,
            "regione_toscana": 0,
            "regione_trentino_alto_adige": 0,
            "regione_umbria": 0,
            "regione_valle_aosta": 0,
            "regione_veneto": 0,
        }
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data["region"] is not None:
                if data["region"] == "ABRUZZO":
                    container["regione_abruzzo"] += data["visitors"]
                elif data["region"] == "BASILICATA":
                    container["regione_basilicata"] += data["visitors"]
                elif data["region"] == "CALABRIA":
                    container["regione_calabria"] += data["visitors"]
                elif data["region"] == "CAMPANIA":
                    container["regione_campania"] += data["visitors"]
                elif data["region"] == "EMILIA-ROMAGNA":
                    container["regione_emilia_romagna"] += data["visitors"]
                elif data["region"] == "FRIULI-VENEZIA GIULIA":
                    container["regione_friuli_venezia_giulia"] += data["visitors"]
                elif data["region"] == "LAZIO":
                    container["regione_lazio"] += data["visitors"]
                elif data["region"] == "LIGURIA":
                    container["regione_liguria"] += data["visitors"]
                elif data["region"] == "LOMBARDIA":
                    container["regione_lombardia"] += data["visitors"]
                elif data["region"] == "MARCHE":
                    container["regione_marche"] += data["visitors"]
                elif data["region"] == "MOLISE":
                    container["regione_molise"] += data["visitors"]
                elif data["region"] == "PIEMONTE":
                    container["regione_piemonte"] += data["visitors"]
                elif data["region"] == "PUGLIA":
                    container["regione_puglia"] += data["visitors"]
                elif data["region"] == "SARDEGNA":
                    container["regione_sardegna"] += data["visitors"]
                elif data["region"] == "SICILIA":
                    container["regione_sicilia"] += data["visitors"]
                elif data["region"] == "TOSCANA":
                    container["regione_toscana"] += data["visitors"]
                elif data["region"] == "TRENTINO-ALTO ADIGE/SUDTIROL":
                    container["regione_trentino_alto_adige"] += data["visitors"]
                elif data["region"] == "UMBRIA":
                    container["regione_umbria"] += data["visitors"]
                elif data["region"] == "VALLE D'AOSTA/VALLE'E D'AOSTE":
                    container["regione_valle_aosta"] += data["visitors"]
                else:  # "VENETO"
                    container["regione_veneto"] += data["visitors"]
        return container

    @classmethod
    def phase_5_dispatch_municipality(cls, array_data):
        container = {
            "citta_roma": 0,
            "citta_fuori_roma": 0,
        }
        for data in array_data:
            if isinstance(data["visitors"], str):  # "*" avoider
                continue
            if data["municipality"] is not None:
                if data["municipality"] == "ROMA":
                    container["citta_roma"] += data["visitors"]
                else:
                    container["citta_fuori_roma"] += data["visitors"]
        return container

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
