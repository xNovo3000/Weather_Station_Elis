# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import math
import statistics
from gpiozero import MCP3008
from gpiozero import Button

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# GET AVERAGE OF ANGLES
def average(angles):
    sin_sum = 0
    cos_sum = 0
    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)
    flen = float(len(angles))
    s = sin_sum / flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s / c))
    avg = 0.0
    if s > 0 and c > 0:
        avg = arc
    elif c < 0:
        avg = arc + 180
    elif s < 0 and c > 0:
        avg = arc + 360
    return 0.0 if avg == 360 else avg


# THE SENSOR CLASS
class WSA80422(AbstractSensor):

    # PERMETTE DI AGGIUSTARE LE CONFIGURAZIONI PER [vanes_volt_angle_dict]
    def __adjust_configs(self):
        vanes_volt_angle_dict_v1 = self.configurations["vanes_volt_angle_dict"]
        vanes_volt_angle_dict_v2 = {}
        for key, value in vanes_volt_angle_dict_v1.items():
            vanes_volt_angle_dict_v2[float(key)] = value
        self.configurations["vanes_volt_angle_dict"] = vanes_volt_angle_dict_v2

    def __init__(self):
        AbstractSensor.__init__(self, "WSA80422")
        self.__adjust_configs()
        # init temporary vars
        self.anemometer_spins = 0
        self.wind_speeds = []
        self.wind_directions = []
        # inizializza gli output
        self.measurements["wind_direction_average"] = 0
        self.measurements["wind_gust"] = 0
        self.measurements["wind_speed_mean"] = 0
        self.measurements["rainfall"] = 0.0
        # inizializza sensore del vento
        try:
            self.wind_speed_sensor_switch_reed = Button(self.configurations["wind_gpio_pin"])
            self.wind_speed_sensor_switch_reed.when_pressed = self.__anemometer_spinned
        except Exception as e:
            self.wind_speed_sensor_switch_reed = None
            self.logger.err(self.sensor_name, "Wind sensor init error {}".format(e))
        # inizializza adc
        try:
            self.adc = MCP3008(channel=self.configurations["adc_channel"])
        except Exception as e:
            self.adc = None
            self.logger.err(self.sensor_name, "ADC init error {}".format(e))
        # inizializza sensore pioggia
        try:
            self.rain_sensor_switch_reed = Button(self.configurations["rain_gpio_pin"])
            self.rain_sensor_switch_reed.when_pressed = self.__bucket_tipped
        except Exception as e:
            self.rain_sensor_switch_reed = None
            self.logger.err(self.sensor_name, "Rain sensor init error {}".format(e))
        # avvisa che il sensore si è avviato correttamente se è realmente così
        if self:
            self.logger.info(self.sensor_name, "Initialized sensor correctly")

    # OGNI META' ROTAZIONE AGGIUNGI 1
    def __anemometer_spinned(self):
        self.anemometer_spins += 1
        self.logger.debug(self.sensor_name, "Anemometer spinned")

    # OGNI VOLTA IL CONTENITORE DELL'ACQUA SI SVUOTA
    def __bucket_tipped(self):
        self.measurements["rainfall"] += self.configurations["rain_gauge_bucket_size"]
        self.logger.debug(self.sensor_name, "Bucket tipped")

    # CALCOLA LA VELOCITA' DEL VENTO
    def __calculate_wind_speed(self):
        cm_in_a_km = 100000.0
        secs_in_an_hour = 3600
        circumference_cm = (2 * math.pi) * self.configurations["anemometer_radius"]
        rotations = self.anemometer_spins / 2.0
        dist_km = (circumference_cm * rotations) / cm_in_a_km
        km_per_sec = dist_km / self.configurations["pooling_rate"]
        km_per_hour = km_per_sec * secs_in_an_hour
        self.anemometer_spins = 0
        return km_per_hour * self.configurations["wind_adjustment"]

    # CALCOLA LA DIREZIONE DEL VENTO
    def __calculate_wind_direction(self):
        wind_dir = round(self.adc.value * self.configurations["vanes_vin"], 1)
        if wind_dir in self.configurations["vanes_volt_angle_dict"]:
            return self.configurations["vanes_volt_angle_dict"][wind_dir]
        else:
            self.logger.warn(self.sensor_name, "Direction not in vanes_volt_angle_dict")
            return 0

    # LEGGI LE MISURAZIONI
    def on_read(self):
        # blocca la guardia
        self.measurements_mutex.acquire()
        # ottieni le nuove misurazioni
        wind_speed = self.__calculate_wind_speed()
        wind_direction = self.__calculate_wind_direction()
        # inserscile nella lista
        self.wind_speeds.append(wind_speed)
        self.wind_directions.append(wind_direction)
        # sblocca la guardia
        self.measurements_mutex.release()
        # per quanto riguarda il log, questo viene fatto quando
        # vengono prese perché devono essere ancora normalizzate

    # OTTIENI LE MISURAZIONE E PULISCILE
    def get_measurements(self):
        # blocca la guardia
        self.measurements_mutex.acquire()
        # se ci sono direzioni del vento e le velocità calcolane la media, il massimo e la statistica
        if len(self.wind_directions) > 0 and len(self.wind_speeds) > 0:
            self.measurements["wind_direction_average"] = average(self.wind_directions)
            self.measurements["wind_gust"] = max(self.wind_speeds)
            self.measurements["wind_speed_mean"] = statistics.mean(self.wind_speeds)
        # pulisci i vettori di appoggio
        self.wind_speeds.clear()
        self.wind_directions.clear()
        # sblocca la guardia
        self.measurements_mutex.release()
        # logga le misurazioni in debug
        self.logger.debug(self.sensor_name, json.dumps(self.measurements))
        # ottieni la copia delle misurazioni
        measurements = AbstractSensor.get_measurements(self)
        # resetta la pioggia (perché è un contatore)
        self.measurements["rainfall"] = 0.0
        # ritorna le misurazioni
        return measurements

    # VERIFICA SE IL SENSORE SI TROVA IN UNO STATO ACCETTABILE PER L'ESECUZIONE
    def __bool__(self):
        cond1 = self.wind_speed_sensor_switch_reed is not None
        cond2 = self.adc is not None
        cond3 = self.rain_sensor_switch_reed is not None
        return AbstractSensor.__bool__(self) and cond1 and cond2 and cond3
