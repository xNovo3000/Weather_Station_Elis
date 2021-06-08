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
from datetime import datetime, timedelta

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

    # FLOW DELL'APPLICAZIONE
    # FASE 1: login e ottieni token
    # FASE 2: ottieni dati sui pdv e ottieni pdv dell'ELIS
    # FASE 3: verifica se i dati della settimana scorsa esistono
    # FASE 4: per ogni giorno della settimana
    #         -> ottieni i dati di ogni dimensione e inseriscili in self.measurements nel timestamp corrispondente

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
        pass

    # RITORNA VERO SE I DATI ESISTONO
    def week_data_exists(self, pdv_id, token, date):
        # ottieni l'anno e la settimana desiderata
        week_number = date.isocalendar()[1]
        # fai la richiesta
        response = requests.post(
            url="{}/retail/daily".format(self.configurations["base_url"]),
            headers={
                "X-API-Key": token,
            },
            json={
                "area": "OUTDOOR",
                "pdvId": pdv_id,
                "date": "{}{}".format(date.year, week_number),
                "dimensionsList": ["gender"],
                "filtersList": [],
                "page": 1
            }
        )
        # verifica la validità della risposta
        body = self.check_response_and_get_body(response, "Week check")
        # se c'è almeno una massa, ritorna true
        if len(body["data"]) > 0:
            return True
        else:
            return None

    # RITORNA TUTTE LE MASSE (ARRAY DI DIZIONARI)
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
            # ottieni i dati
            body = self.check_response_and_get_body(response, "Data")
            # aggiungi al risultato
            for item in body["data"]:
                result.append(item)
        # ritorna il risultato
        return result

    @classmethod
    def dispatch_specific_dimension(cls, dimension, data):
        # genera il risultato
        result = {}
        # verifica ogni massa
        for item in data:
            # null check
            if item[dimension] is None:
                result["null"] += item["visitors"]
            else:
                result[item[dimension]] = item["visitors"]
        # ritorna
        return result

    @classmethod
    def dispatch_dwell_visits_visitors(cls, data):
        # il risultato
        result = {
            "visite": 0,
            "visitatori_totali": 0,
            "tempo_permanenza_medio": 0
        }
        # verifica ogni massa
        for item in data:
            result["visite"] += item["visits"]
            result["visitatori_totali"] += item["visitors"]
            result["tempo_permanenza_medio"] += item["totalDwellTime"]
        # ritorna il risultato
        return result

    # VERIFICA SE LA RISPOSTA E' 200 OK E RITORNA IL BODY PARSANDOLO DA JSON
    def check_response_and_get_body(self, response, name):
        # estrai il json
        body = response.json()
        # verifica se è ok
        if response.status_code != 200:
            self.logger.warn(self.sensor_name, "{} response code: {}".format(name, response.status_code))
            self.logger.warn(self.sensor_name, "{} response message: {}".format(name, body["message"]))
            raise Exception(body["message"])
        # logga il risultato
        self.logger.info(self.sensor_name, "{} response code: {}".format(name, response.status_code))
        self.logger.info(self.sensor_name, "{} response message: {}".format(name, body["message"]))
        # ritorna il json
        return body

    # LOGIN: RITORNA IL TOKEN
    def login(self):
        # richiedi il login
        response = requests.post(
            url="{}/userbackend/login".format(self.configurations["base_url"]),
            json={
                "accessKey": self.configurations["access_key"],
                "secretKey": self.configurations["secret_key"]
            }
        )
        # estrai il json
        body = self.check_response_and_get_body(response, "Login")
        # estrai il token
        return body["token"]

    # RITORNA L'ID DEL PDV
    def get_pdv(self, token):
        response = requests.post(
            url="{}/retail/stores".format(self.configurations["base_url"]),
            headers={
                "X-API-Key": token,
            }
        )
        # estrai il json
        body = self.check_response_and_get_body(response, "Stores")
        # estrai l'id del pdv
        return body["stores"][0]["id"]

    # RITORNA I DATI PER IL GIORNO RICHIESTO
    def get_day_data(self, date, pdv_id, token):
        total_data = self.dispatch_dwell_visits_visitors(
            self.get_data_from_dimension_and_date("gender", date, pdv_id, token)
        )
        gender_data = self.dispatch_specific_dimension(
            "gender", self.get_data_from_dimension_and_date("gender", date, pdv_id, token)
        )
        age_data = self.dispatch_specific_dimension(
            "age", self.get_data_from_dimension_and_date("age", date, pdv_id, token)
        )
        nationality_data = self.dispatch_specific_dimension(
            "nationality", self.get_data_from_dimension_and_date("nationality", date, pdv_id, token)
        )
        work_distance_data = self.dispatch_specific_dimension(
            "workDistance", self.get_data_from_dimension_and_date("workDistance", date, pdv_id, token)
        )
        home_distance_data = self.dispatch_specific_dimension(
            "homeDistance", self.get_data_from_dimension_and_date("homeDistance", date, pdv_id, token)
        )
        region_data = self.dispatch_specific_dimension(
            "region", self.get_data_from_dimension_and_date("region", date, pdv_id, token)
        )

        return {
            "visitatori_maschi": gender_data["M"],
            "visitatori_femmine": gender_data["F"],
            "visitatori_italiani": nationality_data["ITALIANS"],
            "visitatori_stranieri": nationality_data["FOREIGNERS"],
            "visitatori_totali": gender_data["M"] + gender_data["F"] + gender_data["null"]
        }
