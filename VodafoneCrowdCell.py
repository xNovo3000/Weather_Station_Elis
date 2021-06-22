# encoding: UTF-8

"""
Version: Vodafone-0.01
Updated: 17/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import requests
import pytz
from datetime import datetime, timedelta

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# VODAFONE CROWD CELL SENSOR
class VodafoneCrowdCell(AbstractSensor):

    __DATE_FORMAT = "%Y%m%d"

    def __init__(self, data_type):
        AbstractSensor.__init__(self, "VodafoneCrowdCell")
        self.data_type = data_type
        self.measurements = []

    def read(self):
        # chiedi il login
        tk = self.login()
        self.logger.debug(self.sensor_name, "Token: {}".format(tk))
        # chiedi il pdv
        pdv_id = self.get_pdv(tk)
        self.logger.debug(self.sensor_name, "PDV ID: {}".format(pdv_id))
        # genera la data richiesta
        seven_days_before = datetime.now(pytz.utc) - timedelta(days=14)
        self.logger.debug(self.sensor_name, "Requested timestamp: {}".format(seven_days_before))
        # verifica se ci sono i dati
        if self.week_data_exists(pdv_id, tk, seven_days_before):
            # definisci l'ultimo lunedì
            last_monday = datetime.now(pytz.utc) - timedelta(weeks=2, days=datetime.now(pytz.utc).weekday())
            self.logger.debug(self.sensor_name, "Last monday: {}".format(last_monday))
            # ok, prendere i dati di ogni giorno della settimana e inserirli alle 12:00 del giorno stesso
            for i in range(7):
                # ottieni da data da richiedere a vodafone
                choosen_date = (last_monday + timedelta(days=i)).replace(hour=12, minute=0, second=0, microsecond=0)
                self.logger.debug(self.sensor_name, "Choosen date: {}".format(choosen_date))
                # richiedi i dati
                result = self.get_day_data(choosen_date, pdv_id, tk)
                self.logger.debug(self.sensor_name, "Weekday {} results: {}".format(i + 1, result))
                # genera il timestamp
                timestamp = choosen_date.astimezone().timestamp() * 1000
                # iniettalo nella lista delle misurazioni
                self.measurements_mutex.acquire()
                self.measurements.append({
                    "ts": timestamp,
                    "values": result
                })
                self.measurements_mutex.release()
        self.logger.debug(
            self.sensor_name,
            "Sleep mode, next iteration in {} seconds".format(self.configurations["pooling_rate"])
        )

    # RITORNA VERO SE I DATI ESISTONO
    def week_data_exists(self, pdv_id, token, date):
        # genera l'url
        url = "{}/retail/weekly".format(self.configurations["base_url"])
        self.logger.debug(self.sensor_name, "Requesting weekly data from {}".format(url))
        # ottieni l'anno e la settimana desiderata
        week_number = date.isocalendar()[1]
        # fai la richiesta
        response = requests.post(
            url=url,
            headers={
                "X-API-Key": token,
            },
            json={
                "area": self.data_type,
                "pdvId": pdv_id,
                "date": "{}{}".format(date.year, week_number),
                "dimensionsList": ["gender"],
                "filtersList": [],
                "page": 1
            }
        )
        # verifica la validità della risposta
        body = self.check_response_and_get_body(response, "Week check")
        # logga il risultato ottenuto
        self.logger.debug(self.sensor_name, body)
        # se c'è almeno una massa, ritorna true
        if len(body["data"]) > 0:
            self.logger.debug(self.sensor_name, "Body data len > 0")
            return True
        else:
            self.logger.debug(self.sensor_name, "Body data len < 0")
            return None

    # RITORNA TUTTE LE MASSE (ARRAY DI DIZIONARI)
    def get_data_from_dimension_and_date(self, dimension, date, pdv_id, token):
        self.logger.debug(self.sensor_name, "Getting data from dimension {}".format(dimension))
        current_page = 1
        total_pages = 1
        result = []
        # per ogni pagina
        while current_page <= total_pages:
            # logga la pagina corrente sulle totali
            self.logger.debug(self.sensor_name, "Current page: {} - Total pages: {}".format(current_page, total_pages))
            # effettua la richiesta
            response = requests.post(
                url="{}/retail/daily".format(self.configurations["base_url"]),
                headers={
                    "X-API-Key": token,
                },
                json={
                    "area": self.data_type,
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
            current_page += 1
        # ritorna il risultato
        return result

    # @classmethod
    def dispatch_specific_dimension(self, dimension, data):
        # logga la dimensione e i dati
        self.logger.debug(self.sensor_name, "Data: {}".format(data))
        self.logger.debug(self.sensor_name, "Dimension: {}".format(dimension))
        # genera il risultato
        result = {
            "null": 0
        }
        # verifica ogni massa
        for item in data:
            # type check
            if isinstance(item["visitors"], str):
                continue
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
        # logga il body
        self.logger.debug(self.sensor_name, body)
        # ritorna il json
        return body

    # LOGIN: RITORNA IL TOKEN
    def login(self):
        # genera l'url per il login e loggalo
        url = "{}/userbackend/login".format(self.configurations["base_url"])
        self.logger.debug(self.sensor_name, url)
        # richiedi il login
        response = requests.post(
            url=url,
            json={
                "accessKey": self.configurations["access_key"],
                "secretKey": self.configurations["secret_key"]
            }
        )
        # estrai il json e loggalo
        body = self.check_response_and_get_body(response, "Login")
        self.logger.debug(self.sensor_name, body)
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
            "visitatori_maschi": gender_data.get("M", 0),
            "visitatori_femmine": gender_data.get("F", 0),
            "visitatori_italiani": nationality_data.get("ITALIANS", 0),
            "visitatori_stranieri": nationality_data.get("FOREIGNERS", 0),
            "visitatori_totali": total_data.get("visitatori_totali", 0),
            "visite": total_data.get("visite", 0),
            "tempo_permanenza_medio": total_data.get("tempo_permanenza_medio", 0),
            "distanza_casa_0_10": home_distance_data.get("000-010", 0),
            "distanza_casa_10_20": home_distance_data.get("010-020", 0),
            "distanza_casa_20_30": home_distance_data.get("020-030", 0),
            "distanza_casa_30_40": home_distance_data.get("030-040", 0),
            "distanza_casa_40_50": home_distance_data.get("040-050", 0),
            "distanza_casa_50_plus": home_distance_data.get("50+", 0),
            "distanza_casa_media": self.get_weighted_distance_average(home_distance_data),
            "distanza_lavoro_0_10": work_distance_data.get("000-010", 0),
            "distanza_lavoro_10_20": work_distance_data.get("010-020", 0),
            "distanza_lavoro_20_30": work_distance_data.get("020-030", 0),
            "distanza_lavoro_30_40": work_distance_data.get("030-040", 0),
            "distanza_lavoro_40_50": work_distance_data.get("040-050", 0),
            "distanza_lavoro_50_plus": work_distance_data.get("50+", 0),
            "distanza_lavoro_media": self.get_weighted_distance_average(work_distance_data),
            "eta_15_25": age_data.get("[15-25]", 0),
            "eta_25_35": age_data.get("(25-35]", 0),
            "eta_35_45": age_data.get("(35-45]", 0),
            "eta_45_55": age_data.get("(45-55]", 0),
            "eta_55_65": age_data.get("(55-65]", 0),
            "eta_65_plus": age_data.get(">65", 0),
            "eta_media": self.get_weighted_age_average(age_data),
            "regione_abruzzo": region_data.get("ABRUZZO", 0),
            "regione_basilicata": region_data.get("BASILICATA", 0),
            "regine_calabria": region_data.get("CALABRIA", 0),
            "regione_campania": region_data.get("CAMPANIA", 0),
            "regione_emilia_romagna": region_data.get("EMILIA-ROMAGNA", 0),
            "regione_friuli_venezia_giulia": region_data.get("FRIULI-VENEZIA GIULIA", 0),
            "regione_lazio": region_data.get("LAZIO", 0),
            "regione_liguria": region_data.get("LIGURIA", 0),
            "regione_lombardia": region_data.get("LOMBARDIA", 0),
            "regione_marche": region_data.get("MARCHE", 0),
            "regione_molise": region_data.get("MOLISE", 0),
            "regione_piemonte": region_data.get("PIEMONTE", 0),
            "regione_puglia": region_data.get("PUGLIA", 0),
            "regione_sardegna": region_data.get("SADEGNA", 0),
            "regione_sicilia": region_data.get("SICILIA", 0),
            "regione_toscana": region_data.get("TOSCANA", 0),
            "regione_trentino_alto_adige": region_data.get("TRENTINO-ALTO ADIGE/SUDTIROL", 0),
            "regione_umbria": region_data.get("UMBRIA", 0),
            "regione_valle_aosta": region_data.get("VALLE D'AOSTA/VALLE'E D'AOSTE", 0),
            "regione_veneto": region_data.get("VENETO", 0),
        }

    @classmethod
    def get_weighted_distance_average(cls, distance_dict):
        # genera già il risultato
        result = 0.0
        weight = 0
        # per ogni presenza nel dizionario calcola la media pesata
        for (key, value) in distance_dict.items():
            # aggiungi il peso
            weight += value
            # calcola
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
        if weight == 0:
            return 0
        else:
            return result / weight

    @classmethod
    def get_weighted_age_average(cls, age_dict):
        # genera già il risultato
        result = 0.0
        weight = 0
        # per ogni presenza nel dizionario calcola la media pesata
        for (key, value) in age_dict.items():
            # aggiungi il peso
            weight += value
            # calcola
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
        if weight == 0:
            return 0
        else:
            return result / weight

    # PULISCI LE MISURAZIONI UNA VOLTA LOGGATE SU THINGSBOARD
    def get_measurements(self):
        measurements = AbstractSensor.get_measurements(self)
        self.measurements_mutex.acquire()
        self.measurements.clear()
        self.measurements_mutex.release()
        return measurements
