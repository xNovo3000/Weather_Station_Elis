# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import time
import math
import statistics
from threading import Thread
from gpiozero import MCP3008
from gpiozero import Button

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger import Logger
from . import static_functions


# CLASSE DEL WSA
class WSA80422:

    # INIT
    def __init__(self):
        # init configs
        self.configs = Configs.load("wsa_80422.json", static_functions.adjust)
        self.logger = Logger(file_name=self.configs["log_file"])
        # init vars
        self.wind_rotations_count = 0
        self.gust = 0
        self.rain_sensor_count = 0
        self.wind_speed_list = []
        self.wind_direction_list = []
        # init wind sensor
        try:
            self.wind_speed_sensor_switch_reed = Button(self.configs["wind_gpio_pin"])
            self.wind_speed_sensor_switch_reed.when_pressed = self.spin
        except Exception as e:
            self.wind_speed_sensor_switch_reed = None
            self.logger.err("WSA80422", "Wind sensor init error {}".format(e))
        # init adc
        try:
            self.adc = MCP3008(channel=self.configs["adc_channel"])
        except Exception as e:
            self.adc = None
            self.logger.err("WSA80422", "ADC init error {}".format(e))
        # init rain sensor
        try:
            self.rain_sensor_switch_reed = Button(self.configs["rain_gpio_pin"])
            self.rain_sensor_switch_reed.when_pressed = self.bucket_tipped
        except Exception as e:
            self.rain_sensor_switch_reed = None
            self.logger.err("WSA80422", "Rain sensor init error {}".format(e))
        # init wind reading thread
        self.reading_thread = Thread(target=self.__read_wind)
        self.reading_thread.start()

    # EVERY HALF ROTATION, ADD 1 TO THE COUNT
    def spin(self):
        self.wind_rotations_count += 1

    # EVERY TIME THE BUCKET TIPS
    def bucket_tipped(self):
        self.rain_sensor_count += 1

    # READS WIND MEASURAMENTS EVERY x MILLISECONDS
    def __read_wind(self):
        while True:
            # insert wind speed and angle to the dictionary
            self.wind_speed_list.append(self.__calculate_wind_speed())
            self.wind_direction_list.append(self.__calculate_wind_direction())
            # sleep for interval of reading
            time.sleep(self.configs["read_interval"])

    # GET THE WIND SPEED
    def __calculate_wind_speed(self):
        try:
            cm_in_a_km = 100000.0
            secs_in_an_hour = 3600
            circumference_cm = (2 * math.pi) * self.configs["anemometer_radius"]
            rotations = self.wind_rotations_count / 2.0
            dist_km = (circumference_cm * rotations) / cm_in_a_km
            km_per_sec = dist_km / self.configs["read_interval"]
            km_per_hour = km_per_sec * secs_in_an_hour
            self.wind_rotations_count = 0
            return km_per_hour * self.configs["wind_adjustment"]
        except Exception as e:
            self.logger.warn("WSA80422", "Error reading wind speed {}".format(e))
            return 0

    # GET THE WIND DIR
    def __calculate_wind_direction(self):
        wind_dir = round(self.adc.value * self.configs["vanes_vin"], 1)
        if wind_dir in self.configs["vanes_volt_angle_dict"]:
            return self.configs["vanes_volt_angle_dict"][wind_dir]
        else:
            self.logger.warn("WSA80422", "Error reading wind direction, direction not in vanes_volt_angle_dict")
            return 0

    # GET ALL THE CURRENT MEASURAMENTS
    def get_measurements(self):
        # get measurements
        wind_direction_average = 0.0
        if len(self.wind_direction_list) > 0:
            wind_direction_average = static_functions.average(self.wind_direction_list)
        wind_gust = 0.0
        wind_speed_mean = 0.0
        if len(self.wind_speed_list) > 0:
            wind_gust = max(self.wind_speed_list)
            wind_speed_mean = statistics.mean(self.wind_speed_list)
        # insert into dict
        measurements = {
            "wind_direction_average": wind_direction_average,
            "wind_gust": wind_gust,
            "wind_speed_mean": wind_speed_mean,
            "rainfall": self.rain_sensor_count
        }
        # reset
        self.wind_direction_list = []
        self.wind_speed_list = []
        self.rain_sensor_count = 0
        # return
        return measurements

    # CHECK IF CLASS IS OK
    def __bool__(self):
        cond1 = self.wind_speed_sensor_switch_reed is not None
        cond2 = self.adc is not None
        cond3 = self.reading_thread is not None
        cond4 = self.rain_sensor_switch_reed is not None
        return cond1 and cond2 and cond3 and cond4
