#encoding: UTF-8
'''
+ IHS +
Version: v0.1
Updated: 12/March/2021 (Covid-19)
@author: +-- NetcomGroup Innovation Team --+
'''

import bme280
import smbus2
import time
import Configuration
# LOGGER SETUP
import logging
logger = logging.getLogger(__name__)
bme280_sensor_measurements_dict = {}

def init_bme280_sensor(port, address):
    try:
        global bme280_sensor_measurements_dict
        bus = None
        bus = smbus2.SMBus(port)
        bme280.load_calibration_params(bus, address)
        bme280_sensor_measurements_dict = {"humidity": None, "pressure": None, "ambient_temperature": None}
        return True, bus
    except Exception as e:
        message = "ERROR: An error occurred during init_bme280_sensor of bme280 sensor. %s" % e
        logger.error(message)
        return False, None

def get_measurements(bus, port=Configuration.BME280_SENSOR_PORT, address=Configuration.BME280_SENSOR_ADDRESS,
                        measurements_data_file_path = Configuration.BME280_SENSOR_MEASUREMENTS_DATA_FILE_PATH,
                        measurements_data_store_mode = Configuration.BME280_SENSOR_MEASUREMENTS_DATA_STORE_MODE):
    '''

    :param port:
    :param address:
    :return: {"humidity": humidity, "pressure": pressure, "ambient_temperature": ambient_temperature}
    '''
    try:
        global bme280_sensor_measurements_dict
        bme280_data = bme280.sample(bus, address)
        bme280_sensor_measurements_dict["humidity"] = bme280_data.humidity
        bme280_sensor_measurements_dict["pressure"] = bme280_data.pressure
        bme280_sensor_measurements_dict["ambient_temperature"] = bme280_data.temperature

        message_to_store = "humidity=%s;pressure=%s;ambient_temperature=%s\n" % (str(bme280_sensor_measurements_dict["humidity"]),
                                                                                 str(bme280_sensor_measurements_dict["pressure"]),
                                                                                 str(bme280_sensor_measurements_dict["ambient_temperature"]))
        logger.info("BME280 SENSOR Measurements: %s" % message_to_store)
        return True, bme280_sensor_measurements_dict
    except Exception as e:
        message = "ERROR: An error occurred during get_measurements of bme280 sensor. %s" % e
        logger.error(message)
        return False, {}



def get_measurements_thread(port=Configuration.BME280_SENSOR_PORT, address=Configuration.BME280_SENSOR_ADDRESS,
                            measurements_data_file_path = Configuration.BME280_SENSOR_MEASUREMENTS_DATA_FILE_PATH,
                            measurements_data_store_mode = Configuration.BME280_SENSOR_MEASUREMENTS_DATA_STORE_MODE):
    '''

    :param port:
    :param address:
    :return: {"humidity": humidity, "pressure": pressure, "ambient_temperature": ambient_temperature}
    '''
    f = None
    try:
        f = open(measurements_data_file_path, measurements_data_store_mode)
        while True:
            time.sleep(Configuration.BME280_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
            bus = smbus2.SMBus(port)
            bme280.load_calibration_params(bus, address)
            bme280_data = bme280.sample(bus, address)
            humidity = bme280_data.humidity
            pressure = bme280_data.pressure
            ambient_temperature = bme280_data.temperature
            message_to_store = "humidity=%s;pressure=%s;ambient_temperature=%s\n" % (str(humidity), str(pressure), str(ambient_temperature))
            logger.info("BME280 SENSOR Measurements: %s" % message_to_store)
            f.write(message_to_store)
            logger.info("BME280 SENSOR Measurements stored correctly in file.")
            f.flush()
    except Exception as e:
        message = "ERROR: An error occurred during get_measurements of bme280 sensor. %s" % e
        logger.error(message)
    finally:
        if f:
            f.close()

