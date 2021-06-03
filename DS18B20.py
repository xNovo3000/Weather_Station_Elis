# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import glob
import json
import time

# AMBIENT IMPORT
from Utils.AbstractSensor import AbstractSensor


# GESTISCE IL SENSORE DS18B20
class DS18B20(AbstractSensor):

    def __init__(self):
        AbstractSensor.__init__(self, "DS18B20")
        self.measurements["ground_temperature"] = 0.0
        # prova a caricare il file da cui leggere le misurazioni
        try:
            self.device_file = glob.glob(self.configurations["device_file_path"])[0] \
                               + "/" + self.configurations["device_name"]
        except Exception as e:
            self.logger.err(self.sensor_name, "Error loading device. {}".format(e))
            self.device_file = None
    
    def __read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines
    
    def __crc_check(self, lines):
        crc_check = "NO"
        if self.configurations["crc_check"]:
            crc_check = "YES"
        return lines[0].strip()[-3:] == crc_check
        
    def read(self):
        attempts = 0
        lines = self.__read_temp_raw()
        success = self.__crc_check(lines)
        while not success and attempts < self.configurations["read_attempts"]:
            time.sleep(self.configurations["wait_time"])
            lines = self.__read_temp_raw()
            success = self.__crc_check(lines)
            attempts += 1
        if success:
            temp_line = lines[1]
            equal_pos = temp_line.find(self.configurations["temp_line_token"])
            if equal_pos != -1:
                temp_string = temp_line[equal_pos + 2:]
                ground_temp_c = float(temp_string) / 1000.0
                self.measurements["ground_temperature"] = ground_temp_c
                self.logger.debug(self.sensor_name, json.dumps(self.measurements))
            else:
                self.logger.warn(self.sensor_name, "Error reading measurements. equal_pos = -1")
        else:
            self.logger.warn(self.sensor_name, "Error reading measurements. Success = False")
        
    def __bool__(self):
        return AbstractSensor.__bool__(self) and self.device_file is not None
