#encoding: UTF-8
'''
+ IHS +
Version: v0.1
Updated: 12/March/2021 (Covid-19)
@author: +-- NetcomGroup Innovation Team --+
'''
import os
import glob
import time
import Configuration
# LOGGER SETUP
import logging
logger = logging.getLogger(__name__)

from threading import Thread


# add the lines below to /etc/modules (reboot to take effect)
# w1-gpio
# w1-therm

class DS18B20(Thread):

    def __init__(self, measurements_data_file_path, measurements_data_store_mode):
        Thread.__init__(self)
        self.device_file = glob.glob(Configuration.DS18B20_DEVICE_FILE_PATH)[0] + "/" + Configuration.DS18B20_DEVICE_NAME
        self.measurements_data_file_path = measurements_data_file_path
        self.measurements_data_store_mode = measurements_data_store_mode

    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines

    def crc_check(self, lines):
        return lines[0].strip()[-3:] == Configuration.DS18B20_CRC_CHECK

    def get_measurements(self):
        '''
        Metodo se si vuole usare come thread
        Funzione da invocare per leggere la temperatura
        :return: {"temperature": temp_c}
        '''
        try:
            ds18b20_sensor_measurements_dict = {}
            # temp_c = -255
            attempts = 0

            lines = self.read_temp_raw()
            success = self.crc_check(lines)

            while not success and attempts < Configuration.DS18B20_READ_ATTEMPTS:
                time.sleep(Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
                lines = self.read_temp_raw()
                success = self.crc_check(lines)
                attempts += 1

            if success:
                temp_line = lines[1]
                equal_pos = temp_line.find(Configuration.DS18B20_TEMP_LINE_TOKEN)
                if equal_pos != -1:
                    temp_string = temp_line[equal_pos + 2:]
                    ground_temp_c = float(temp_string) / 1000.0
                    message_to_store = "ground_temperature=%s\n" % str(ground_temp_c)
                    logger.info("DS18B20 SENSOR Measurements: %s" % message_to_store)
                    ds18b20_sensor_measurements_dict.update({"ground_temperature": ground_temp_c})
                    return True, ds18b20_sensor_measurements_dict
                else:
                    message = "ERROR: An error occurred during get_measurements of ds18b20 sensor. equal_pos:%s" % str(equal_pos)
                    logger.error(message)
                    return False, {}
            else:
                message = "ERROR: An error occurred during get_measurements of ds18b20 sensor. Success = False"
                logger.error(message)
                return False, {}

        except Exception as e:
            message = "ERROR: An error occurred during get_measurements of ds18b20 sensor. %s" % e
            logger.error(message)
            return False, {}

    def run(self):
        '''
        Metodo se si vuole usare come thread
        Funzione da invocare per leggere la temperatura
        :return: {"temperature": temp_c}
        '''
        f = None
        try:
            f = open(self.measurements_data_file_path, self.measurements_data_store_mode)
            # temp_c = -255
            attempts = 0

            lines = self.read_temp_raw()
            success = self.crc_check(lines)

            while not success and attempts < Configuration.DS18B20_READ_ATTEMPTS:
                time.sleep(Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
                lines = self.read_temp_raw()
                success = self.crc_check(lines)
                attempts += 1

            if success:
                temp_line = lines[1]
                equal_pos = temp_line.find(Configuration.DS18B20_TEMP_LINE_TOKEN)
                if equal_pos != -1:
                    temp_string = temp_line[equal_pos + 2:]
                    ground_temp_c = float(temp_string) / 1000.0
                    message_to_store = "ground_temperature=%s\n" % str(ground_temp_c)
                    logger.info("DS18B20 SENSOR Measurements: %s" % message_to_store)
                    f.write(message_to_store)
                    logger.info("DS18B20 SENSOR Measurements stored correctly in file.")
                    f.flush()

        except Exception as e:
            message = "ERROR: An error occurred during get_measurements of ds18b20 sensor. %s" % e
            logger.error(message)
        finally:
            if f:
                f.close()