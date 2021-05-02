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
        # init outputs
        self.measurements["wind_direction_average"] = 0
        self.measurements["wind_gust"] = 0
        self.measurements["wind_speed_mean"] = 0
        self.measurements["rainfall"] = 0.0
        # init wind sensor
        try:
            self.wind_speed_sensor_switch_reed = Button(self.configurations["wind_gpio_pin"])
            self.wind_speed_sensor_switch_reed.when_pressed = self.__spin
        except Exception as e:
            self.wind_speed_sensor_switch_reed = None
            self.logger.err(self.sensor_name, "Wind sensor init error {}".format(e))
        # init adc
        try:
            self.adc = MCP3008(channel=self.configurations["adc_channel"])
        except Exception as e:
            self.adc = None
            self.logger.err(self.sensor_name, "ADC init error {}".format(e))
        # init rain sensor
        try:
            self.rain_sensor_switch_reed = Button(self.configurations["rain_gpio_pin"])
            self.rain_sensor_switch_reed.when_pressed = self.__bucket_tipped
        except Exception as e:
            self.rain_sensor_switch_reed = None
            self.logger.err(self.sensor_name, "Rain sensor init error {}".format(e))

    # EVERY HALF ROTATION, ADD 1 TO THE COUNT
    def __spin(self):
        self.anemometer_spins += 1

    # EVERY TIME THE BUCKET TIPS
    def __bucket_tipped(self):
        self.measurements["rainfall"] += self.configurations["rain_gauge_bucket_size"]

    # GET THE WIND SPEED
    def __calculate_wind_speed(self):
        try:
            cm_in_a_km = 100000.0
            secs_in_an_hour = 3600
            circumference_cm = (2 * math.pi) * self.configurations["anemometer_radius"]
            rotations = self.anemometer_spins / 2.0
            dist_km = (circumference_cm * rotations) / cm_in_a_km
            km_per_sec = dist_km / self.configurations["pooling_rate"]
            km_per_hour = km_per_sec * secs_in_an_hour
            self.anemometer_spins = 0
            return km_per_hour * self.configurations["wind_adjustment"]
        except Exception as e:
            self.logger.warn(self.sensor_name, "Error reading wind speed {}".format(e))
            return 0

    # GET THE WIND DIR
    def __calculate_wind_direction(self):
        wind_dir = round(self.adc.value * self.configurations["vanes_vin"], 1)
        if wind_dir in self.configurations["vanes_volt_angle_dict"]:
            return self.configurations["vanes_volt_angle_dict"][wind_dir]
        else:
            self.logger.warn(self.sensor_name, "Direction not in vanes_volt_angle_dict")
            return 0

    def read(self):
        if self:
            self.measurements_mutex.acquire()  # lock guard
            # get async measurements
            wind_speed = self.__calculate_wind_speed()
            wind_direction = self.__calculate_wind_direction()
            # append to the existing ones
            self.wind_speeds.append(wind_speed)
            self.wind_directions.append(wind_direction)
            self.measurements_mutex.release()  # unlock guard
            # log the measurements

    def get_measurements(self):
        # calculate from temp data and clear them
        self.measurements_mutex.acquire()  # lock guard
        if len(self.wind_directions) > 0:
            self.measurements["wind_direction_average"] = average(self.wind_directions)
        if len(self.wind_speeds) > 0:
            self.measurements["wind_gust"] = max(self.wind_speeds)
            self.measurements["wind_speed_mean"] = statistics.mean(self.wind_speeds)
        self.wind_speeds.clear()
        self.wind_directions.clear()
        self.measurements_mutex.release()  # unlock guard
        # log data
        self.logger.info(self.sensor_name, json.dumps(self.measurements))
        # return the data
        return AbstractSensor.get_measurements(self)

    def __bool__(self):
        cond1 = self.wind_speed_sensor_switch_reed is not None
        cond2 = self.adc is not None
        cond4 = self.rain_sensor_switch_reed is not None
        return AbstractSensor.__bool__(self) and cond1 and cond2 and cond4
