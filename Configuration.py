# encoding: UTF-8

"""
Version: 0.2
Updated: 19/04/2021
Author: NetcomGroup Innovation Team
"""

import os

# GENERAL CONFIGURATION PARAMETERS
PROJECT_ROOT_PATH = os.path.dirname(__file__)
FILES_PATH = os.path.join(PROJECT_ROOT_PATH, "Files")
LOG_PATH = os.path.join(FILES_PATH, "Log")
ID_WEATHER_STATION = "01"
WEATHER_STATION_DATA_FILE_PATH = os.path.normpath(
    os.path.join(FILES_PATH, "weather_station_data_file_{}.txt".format(ID_WEATHER_STATION))
)
WEATHER_STATION_DATA_FILE_MODE = "a+"
# GENERAL CONFIGURATION PARAMETERS

# THINGSBOARD CONFIGURATION
THINGSBOARD_HOST = 'iothings.netcomgroup.eu'  # 85.47.183.27
THINGSBOARD_ACCESS_TOKEN = 'sTDQN6xTkw5i4pstfcBi'  # identifica univocamente il device creato su Thingsboard
THINGSBOARD_MQTT_PORT = 1883
THINGSBOARD_KEEP_ALIVE = 60  # [s]
THINGSBOARD_QOS = 1
PUBLISH_TIME = 3  # [s]
# THINGSBOARD CONFIGURATION

# BME280 SENSOR
BME280_SENSOR_PORT = 1
BME280_SENSOR_ADDRESS = 0x77  # Adafruit BME280 address. Other BME280s may be different
BME280_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(
    os.path.join(FILES_PATH, "bme280_sensor_measurements_data_{}.txt".format(ID_WEATHER_STATION))
)  # il file dove verranno salvati i dati
BME280_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+"  # file store mode -> a+ (append), w+ (new file)
BME280_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60  # [s]
# BME280 SENSOR

# DS18B20 SENSOR
DS18B20_DEVICE_FILE_PATH = "/sys/bus/w1/devices/28*"
DS18B20_DEVICE_NAME = "w1_slave"
DS18B20_READ_ATTEMPTS = 3
DS18B20_CRC_CHECK = "YES"
DS18B20_TEMP_LINE_TOKEN = "t="
DS18B20_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(
    os.path.join(FILES_PATH, "ds18b20_sensor_measurements_data_{}.txt".format(ID_WEATHER_STATION))
)  # il file dove verranno salvati i dati
DS18B20_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+"  # file store mode -> a+ (append), w+ (new file)
DS18B20_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60  # [s]
# DS18B20 SENSOR

# WIND SENSOR
WIND_ANEMOMETER_RADIUS_CM = 9.0  # [cm] Anemometer radius
WIND_TIME_INTERVAL = 5.0  # [s]
WIND_TIME_INTERVAL_DIRECTION = 5.0  # [s]
WIND_ADJUSTMENT = 1.8  # Anemometer factor (see on datasheet)
WIND_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(
    os.path.join(FILES_PATH, "wind_sensor_measurements_data_{}.txt".format(ID_WEATHER_STATION))
)  # il file dove verranno salvati i dati
WIND_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+"  # file store mode -> a+ (append), w+ (new file)
WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60  # [s]
WIND_SENSOR_BUTTON_GPIO_PIN_NUMBER = 5
WIND_SENSOR_ADC_MCP3008_CHANNEL = 0
WIND_SENSOR_VANES_R1 = 4700  # [ohm] E' il valore della resistenza utilizzata dal wind vanes, riportata nel datasheet
WIND_SENSOR_VANES_VIN = 3.3  # [V]
# E' il dizionario che mette in relazione la tensione e l'angolo
# [Link] https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/7
WIND_SENSOR_VANES_VOLT_ANGLE_DICT = {
    0.4: 0.0,
    1.4: 22.5,
    1.2: 45.0,
    2.8: 67.5,
    2.7: 90.0,
    2.9: 112.5,
    2.2: 135.0,
    2.5: 157.5,
    1.8: 180.0,
    2.0: 202.5,
    0.7: 225.0,
    0.8: 247.5,
    0.1: 270.0,
    0.3: 292.5,
    0.2: 315.0,
    0.6: 337.5
}
# Da valutare quando arriverà l'hardware bisognerà leggere i valori
# in uscita dall'adc in seguito ad un giro completo del wind vanes
RAIN_GAUGE_BUTTON_GPIO_PIN_NUMBER = 6
RAIN_GAUGE_BUCKET_SIZE = 0.2794  # The quantity of rain that causes the gauge's bucket to tip
# WIND SENSOR

# LOG CONFIGURATION
LOG_FILE_NAME_PATH_WEATHER_STATION = os.path.normpath(os.path.join(LOG_PATH, "Logging_Weather_Station.ini"))
LOG_COLOR = {
    "INFO": "\033[94m",
    "WARN": "\033[93m",
    "ERR": "\033[91m",
    "NONE": "\033[0m",
}
# LOG CONFIGURATION
