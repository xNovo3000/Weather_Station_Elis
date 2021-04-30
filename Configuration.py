#encoding: UTF-8
'''
+ IHS +
Version: v0.1
Updated: 12/March/2021 (Covid-19)
@author: +-- NetcomGroup Innovation Team --+
'''
import os

########################################################################I
##########    + GENERAL CONFIGURATION PARAMETERS +    ##################H
########################################################################S
PROJECT_ROOT_PATH = os.path.dirname(__file__) # La path della root di questo progetto #__file__ = D:\Users\Mediamotive\PycharmProjects\M3Alpha_Component\Core\Configuration.py
FILES_PATH = os.path.join(PROJECT_ROOT_PATH, "Files")
LOG_PATH = os.path.join(FILES_PATH, "Log")
ID_WEATHER_STATION = "01"
WEATHER_STATION_DATA_FILE_PATH = os.path.normpath(os.path.join(FILES_PATH, "weather_station_data_file_%s.txt" % ID_WEATHER_STATION))
WEATHER_STATION_DATA_FILE_MODE = "a+"

########################################################################I
################################    + THINGSBOARD +    #################H
########################################################################S
THINGSBOARD_HOST = 'iothings.netcomgroup.eu' #'85.47.183.27 #è ip corrispondente
THINGSBOARD_ACCESS_TOKEN = 'sTDQN6xTkw5i4pstfcBi' # identifica in maniera univoca il device creato su Thingsboard
THINGSBOARD_MQTT_PORT = 1883 #8080#30116
THINGSBOARD_KEEP_ALIVE = 60
THINGSBOARD_QOS = 1
PUBLISH_TIME = 10 # [s]

########################################################################I
##########    + BME280_SENSOR +    #####################################H
########################################################################S
BME280_SENSOR_PORT = 1
BME280_SENSOR_ADDRESS = 0x76 # Adafruit BME280 address. Other BME280s may be different
BME280_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(os.path.join(FILES_PATH, "bme280_sensor_measurements_data_%s.txt" % ID_WEATHER_STATION)) # file where will be stored the measurements data
BME280_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+" # store mode in file -> a+ (append), w+ (new file)
BME280_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60*1 # [s] time for next reading measurements

########################################################################I
##########    + DS18B20_SENSOR +    ####################################H
########################################################################S
DS18B20_DEVICE_FILE_PATH = "/sys/bus/w1/devices/28*"
DS18B20_DEVICE_NAME = "w1_slave"
DS18B20_READ_ATTEMPTS = 3
DS18B20_CRC_CHECK = "YES"
DS18B20_TEMP_LINE_TOKEN = "t="
DS18B20_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(os.path.join(FILES_PATH, "ds18b20_sensor_measurements_data_%s.txt" % ID_WEATHER_STATION))  # file where will be stored the measurements data
DS18B20_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+" # store mode in file -> a+ (append), w+ (new file)
DS18B20_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60*1 # [s] time for next reading measurements

########################################################################I
##########    + WIND_SENSOR +    #######################################H
########################################################################S
WIND_ANEMOMETER_RADIUS_CM = 9.0 # [cm] Anemometer radius
WIND_TIME_INTERVAL = PUBLISH_TIME -1 # [s] How often to report wind speed
WIND_TIME_INTERVAL_DIRECTION = PUBLISH_TIME - 1 # [s]
WIND_ADJUSTMENT = 1.8 # Anemometer factor (see on data sheet)
WIND_SENSOR_MEASUREMENTS_DATA_FILE_PATH = os.path.normpath(os.path.join(FILES_PATH, "wind_sensor_measurements_data_%s.txt" % ID_WEATHER_STATION))  # file where will be stored the measurements data
WIND_SENSOR_MEASUREMENTS_DATA_STORE_MODE = "a+" # store mode in file -> a+ (append), w+ (new file)
WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME = 60*1 # [s] time for next reading measurements
WIND_SENSOR_BUTTON_GPIO_PIN_NUMBER = 5
############### WIND VANES #######################
WIND_SENSOR_ADC_MCP3008_CHANNEL = 0
WIND_SENSOR_VANES_R1 = 4700 # [ohm] E' il valore della resistenza di riferimento utilizzata dal wind vanes, riportata nel datasheet
WIND_SENSOR_VANES_VIN = 3.3 # [v]
# E' il dizionario che mette in relazione la tensione e l'angolo
# Link ref: https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/7
# Riga di riferimento su guida: Reading values from an MCP3008 ADC is very easy, thanks to the gpiozero library.
# Da valutare quando arriverà l'hardware, bisognerà leggere i valori in uscita dall'adc, in seguito ad un giro completo del wind vanes
# Valori di tensione ottenuti usando lo script: wind_directiion_byo_calibartion_adc.py -> [0.1, 1.2, 1.8, 0.3, 0.2, 2.7, 0.7, 0.4, 2.2, 2.9, 0.8, 2.5, 2.8, 1.4, 2.0, 0.6]
WIND_SENSOR_VANES_VOLT_ANGLE_DICT = {0.4: 0.0, 1.4: 22.5, 1.2: 45.0, 2.8: 67.5, 2.7: 90.0, 2.9: 112.5, 2.2: 135.0, 2.5: 157.5, 1.8: 180.0, 2.0: 202.5, 0.7: 225.0, 0.8: 247.5, 0.1: 270.0, 0.3: 292.5, 0.2: 315.0, 0.6: 337.5, 0.0: 0}
############## RAIN GAUGE #########################
RAIN_GAUGE_BUTTON_GPIO_PIN_NUMBER = 6
RAIN_GAUGE_BUCKET_SIZE = 0.2794 # The quantity of rain that causes the gauge's bucket to tip



#####################################################
##########    + LOG +    ############################
#####################################################
LOG_FILE_NAME_PATH_WEATHER_STATION = os.path.normpath(os.path.join(LOG_PATH, "Logging_Weather_Station.ini"))
