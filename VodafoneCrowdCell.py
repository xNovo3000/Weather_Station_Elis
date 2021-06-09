# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import os
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
        self.measurements = []

    def read(self):
        # chiedi il login
        tk = self.login()
        # chiedi il pdv
        pdv_id = self.get_pdv(tk)
        # genera la data richiesta
        seven_days_before = datetime.today() - timedelta(days=7)
        # verifica se ci sono i dati
        if self.week_data_exists(pdv_id, tk, seven_days_before):
            # definisci l'ultimo lunedì
            last_monday = datetime.today() - timedelta(weeks=1, days=datetime.today().weekday())
            # ok, prendere i dati di ogni giorno della settimana e inserirli alle 12:00 del giorno stesso
            for i in range(7):
                # ottieni da data da richiedere a vodafone
                choosen_date = (last_monday + timedelta(days=i)).replace(hour=12, minute=0, second=0, microsecond=0)
                # richiedi i dati
                result = self.get_day_data(choosen_date, pdv_id, tk)
                # genera il timestamp
                timestamp = choosen_date.timestamp()
                # iniettalo nella lista delle misurazioni
                self.measurements_mutex.acquire()
                self.measurements.append({
                    "ts": timestamp,
                    "values": result
                })
                self.measurements_mutex.release()
            # la prossima richiesta deve avvenire tra 7 giorni
            self.configurations["pooling_rate"] = 604800
        else:
            # la prossima richiesta deve avvenire tra 1 giorno
            self.configurations["pooling_rate"] = 86400

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

    # VERIFICA SE LA RISPOSTA E' 200 OK E RITORNA IL BODY DA JSON A DICT/LIST
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
            "visitatori_totali": total_data["visitatori_totali"],
            "visite": total_data["visite"],
            "tempo_permanenza_medio": total_data["tempo_permanenza_medio"],
            "distanza_casa_0_10": home_distance_data["000-010"],
            "distanza_casa_10_20": home_distance_data["010-020"],
            "distanza_casa_20_30": home_distance_data["020-030"],
            "distanza_casa_30_40": home_distance_data["030-040"],
            "distanza_casa_40_50": home_distance_data["040-050"],
            "distanza_casa_50_plus": home_distance_data["50+"],
            "distanza_casa_media": self.get_weighted_distance_average(home_distance_data),
            "distanza_lavoro_0_10": work_distance_data["000-010"],
            "distanza_lavoro_10_20": work_distance_data["010-020"],
            "distanza_lavoro_20_30": work_distance_data["020-030"],
            "distanza_lavoro_30_40": work_distance_data["030-040"],
            "distanza_lavoro_40_50": work_distance_data["040-050"],
            "distanza_lavoro_50_plus": work_distance_data["50+"],
            "distanza_lavoro_media": self.get_weighted_distance_average(work_distance_data),
            "eta_15_25": age_data["[15-25]"],
            "eta_25_35": age_data["(25-35]"],
            "eta_35_45": age_data["(35-45]"],
            "eta_45_55": age_data["(45-55]"],
            "eta_55_65": age_data["(55-65]"],
            "eta_65_plus": age_data[">65"],
            "eta_media": self.get_weighted_age_average(age_data),
            "regione_abruzzo": region_data["ABRUZZO"],
            "regione_basilicata": region_data["BASILICATA"],
            "regine_calabria": region_data["CALABRIA"],
            "regione_campania": region_data["CAMPANIA"],
            "regione_emilia_romagna": region_data["EMILIA_ROMAGNA"],
            "regione_friuli_venezia_giulia": region_data["FRIULI_VENEZIA_GIULIA"],
            "regione_lazio": region_data["LAZIO"],
            "regione_liguria": region_data["LIGURIA"],
            "regione_lombardia": region_data["LOMBARDIA"],
            "regione_marche": region_data["MARCHE"],
            "regione_molise": region_data["MOLISE"],
            "regione_piemonte": region_data["PIEMONTE"],
            "regione_puglia": region_data["PUGLIA"],
            "regione_sardegna": region_data["SADEGNA"],
            "regione_sicilia": region_data["SICILIA"],
            "regione_toscana": region_data["TOSCANA"],
            "regione_trentino_alto_adige": region_data["TRENTINO_ALTO_ADIGE"],
            "regione_umbria": region_data["UMBRIA"],
            "regione_valle_aosta": region_data["VAL_D_AOSTA"],  # TODO: verificare se è corretto
            "regione_veneto": region_data["VENETO"],
        }

    @classmethod
    def get_weighted_distance_average(cls, distance_dict):
        # genera già il risultato
        result = 0.0
        # per ogni presenza nel dizionario calcola la media pesata
        for (key, value) in distance_dict.items():
            if key == "000-010":
                result += value * 5
            elif key == "010-020":
                result += value * 15
            elif key == "020-030":
                result += value * 25
            elif key == "030-040":
                result += value * 35
            elif key == "040-050":
                result += value * 45
            elif key == "50+":
                result += value * 55
        # ritorna il risultato finale
        return result

    @classmethod
    def get_weighted_age_average(cls, age_dict):
        # genera già il risultato
        result = 0.0
        # per ogni presenza nel dizionario calcola la media pesata
        for (key, value) in age_dict.items():
            if key == "[15-25]":
                result += value * 20
            elif key == "(25-35]":
                result += value * 30
            elif key == "(35-45]":
                result += value * 40
            elif key == "(45-55]":
                result += value * 50
            elif key == "(55-65]":
                result += value * 60
            elif key == ">65":
                result += value * 70
        # ritorna il risultato finale
        return result

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
