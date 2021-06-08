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

    __DATE_FORMAT = "%Y%M%d"

    def __init__(self):
        AbstractSensor.__init__(self, "VodafoneCrowdCell")
        self.real_pooling_rate = self.configurations["pooling_rate"]
        self.__reset_data()

    def __reset_data(self):
        self.visitatori_totali = 0
        self.visitatori_italiani = 0
        self.visitatori_stranieri = 0
        self.visitatori_maschi = 0
        self.visitatori_femmine = 0  # non scrivo visitatrici per questioni di omogeneità delle chiavi
        self.visite_totali = 0  # per le visite calcolo SOLO le totali
        self.distanza_casa_0_10 = 0
        self.distanza_casa_10_20 = 0
        self.distanza_casa_20_30 = 0
        self.distanza_casa_30_40 = 0
        self.distanza_casa_40_50 = 0
        self.distanza_casa_50_plus = 0
        self.distanza_casa_media = 0
        self.distanza_lavoro_0_10 = 0
        self.distanza_lavoro_10_20 = 0
        self.distanza_lavoro_20_30 = 0
        self.distanza_lavoro_30_40 = 0
        self.distanza_lavoro_40_50 = 0
        self.distanza_lavoro_50_plus = 0
        self.distanza_lavoro_media = 0
        self.tempo_permanenza_medio = 0  # gmove dovrebbe dare dati più precisi, al momento li passo lo stesso
        self.eta_15_25 = 0
        self.eta_25_35 = 0
        self.eta_35_45 = 0
        self.eta_45_55 = 0
        self.eta_55_65 = 0
        self.eta_65_plus = 0
        self.eta_media = 0
        self.regione_abruzzo = 0
        self.regione_basilicata = 0
        self.regine_calabria = 0
        self.regione_campania = 0
        self.regione_emilia_romagna = 0
        self.regione_friuli_venezia_giulia = 0
        self.regione_lazio = 0
        self.regione_liguria = 0
        self.regione_lombardia = 0
        self.regione_marche = 0
        self.regione_molise = 0
        self.regione_piemonte = 0
        self.regione_puglia = 0
        self.regione_sardegna = 0
        self.regione_sicilia = 0
        self.regione_toscana = 0
        self.regione_trentino_alto_adige = 0
        self.regione_umbria = 0
        self.regione_valle_aosta = 0
        self.regione_veneto = 0

    def read(self):

        # FASE 1: LOGIN
        response = requests.post(
            url="{}/userbackend/login".format(self.configurations["base_url"]),
            json={
                "accessKey": self.configurations["access_key"],
                "secretKey": self.configurations["secret_key"]
            }
        )
        # estrai il json
        body = response.json()
        # verifica se il login è ok
        if response.status_code != 200:
            self.logger.warn(self.sensor_name, "Login response code: {}".format(response.status_code))
            self.logger.warn(self.sensor_name, "Login response message: {}".format(body["message"]))
            raise Exception(body["message"])
        # logga il risultato
        self.logger.info(self.sensor_name, "Login response code: {}".format(response.status_code))
        self.logger.info(self.sensor_name, "Login response message: {}".format(body["message"]))
        # estrai il token
        token = body["token"]

        # FASE 2: OTTIENI I DATI DI TUTTI I PDV DA VODAFONE
        response = requests.post(
            url="{}/retail/stores".format(self.configurations["base_url"]),
            headers={
                "X-API-Key": token,
            }
        )
        # estrai il json
        body = response.json()
        # verifica se il login è ok
        if response.status_code != 200:
            self.logger.warn(self.sensor_name, "Stores response code: {}".format(response.status_code))
            self.logger.warn(self.sensor_name, "Stores response message: {}".format(body["message"]))
            raise Exception(body["message"])
        # logga il risultato
        self.logger.info(self.sensor_name, "Stores response code: {}".format(response.status_code))
        self.logger.info(self.sensor_name, "Stores response message: {}".format(body["message"]))
        # salva l'id del pdv
        pdv_id = body["stores"][0]["id"]

        # FASE 3: VERIFICARE SE I DATI DELLA SETTIMANA ESISTONO

    # def data_exists(self, week, pdv_id, token):
    #     response = requests.post(
    #         url="{}/retail/daily".format(self.configurations["base_url"]),
    #         headers={
    #             "X-API-Key": token,
    #         },
    #         json={
    #             "area": "OUTDOOR",
    #             "pdvId": pdv_id,
    #             "date": date.strftime(VodafoneCrowdCell.__DATE_FORMAT),
    #             "dimensionsList": [dimension],
    #             "filtersList": [],
    #             "page": current_page
    #         }
    #     )

    def get_data_from_dimension_and_date(self, dimension, date, pdv_id, token):
        current_page = 1
        total_pages = 1
        result = []
        # per ogni pagina
        while current_page <= total_pages:
            # effettua la richiesta
            response = requests.post(
                url="{}/retail/daily".format(self.configurations["base_url"]),
                headers={
                    "X-API-Key": token,
                },
                json={
                    "area": "OUTDOOR",
                    "pdvId": pdv_id,
                    "date": date.strftime(VodafoneCrowdCell.__DATE_FORMAT),
                    "dimensionsList": [dimension],
                    "filtersList": [],
                    "page": current_page
                }
            )
            # estrai il json
            body = response.json()
            # verifica se è ok
            if response.status_code != 200:
                self.logger.warn(self.sensor_name, "Data response code: {}".format(response.status_code))
                self.logger.warn(self.sensor_name, "Data response message: {}".format(body["message"]))
                raise Exception(body["message"])
            # logga il risultato
            self.logger.info(self.sensor_name, "Data response code: {}".format(response.status_code))
            self.logger.info(self.sensor_name, "Data response message: {}".format(body["message"]))
            # aggiungi al risultato
            for item in body["data"]:
                result.append(item)
        # ritorna il risultato
        return result

    def dispatch_specific_dimension(self, dimension, list_of_items):
        # genera il risultato
        result = {}
        # verifica ogni massa
        for item in list_of_items:
            # null check
            if item[dimension] is None:
                result["null"] = item["visitors"]
            else:
                result[item[dimension]] = item["visitors"]
        # ritorna
        return result
