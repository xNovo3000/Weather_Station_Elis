# encoding: UTF-8

"""
Version: 0.2
Updated: 30/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import glob
import time

# AMBIENT IMPORT
import Utils.Configs as Configs
from Utils.Logger import Logger


# GESTISCE UN SENSORE DS18B20
class DS18B20:

    def __init__(self):
        self.configs = Configs.load("ds18b20.json")
        self.logger = Logger(file_name=self.configs["log_file"])
        try:
            self.device_file = glob.glob(self.configs["device_file_path"])[0] + "/" + self.configs["device_name"]
        except Exception as e:
            self.logger.err("DS18B20", "Error loading device. {}".format(e))
            self.device_file = None

    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines

    def crc_check(self, lines):
        return lines[0].strip()[-3:] == self.configs["crc_check"]

    def get_measurements(self):
        try:
            ds18b20_sensor_measurements_dict = {}
            # temp_c = -255
            attempts = 0

            lines = self.read_temp_raw()
            success = self.crc_check(lines)

            while not success and attempts < self.configs["read_attempts"]:
                time.sleep(self.configs["wait_time"])
                lines = self.read_temp_raw()
                success = self.crc_check(lines)
                attempts += 1

            if success:
                temp_line = lines[1]
                equal_pos = temp_line.find(self.configs["temp_line_token"])
                if equal_pos != -1:
                    temp_string = temp_line[equal_pos + 2:]
                    ground_temp_c = float(temp_string) / 1000.0
                    self.logger.info("DS18B20", "Ground temperature = {}".format(ground_temp_c))
                    ds18b20_sensor_measurements_dict.update({"ground_temperature": ground_temp_c})
                    return ds18b20_sensor_measurements_dict
                else:
                    self.logger.err("DS18B20", "Error reading measurements. equal_pos = {}".format(equal_pos))
                    return {}
            else:
                self.logger.err("DS18B20", "Error reading measurements. Success = False")
                return {}

        except Exception as e:
            self.logger.err("DS18B20", "Error reading measurements. {}".format(e))
            return {}

    def __bool__(self):
        return self.device_file is not None
