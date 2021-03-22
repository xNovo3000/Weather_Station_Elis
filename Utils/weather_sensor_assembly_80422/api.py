#encoding: UTF-8
'''
+ IHS +
Version: v0.1
Updated: 15/March/2021 (Covid-19)
@author: +-- NetcomGroup Innovation Team --+
'''
import time
import math
import statistics
import Configuration
# LOGGER SETUP
import logging
logger = logging.getLogger(__name__)
from gpiozero import MCP3008
from gpiozero import Button
import time

values = []
wind_count = 0
rain_sensor_count = 0
store_speeds = []
gust = 0



def voltage_divider(r1, r2, v_in):
    '''
    Partitore di tensione
    :return:
    '''
    v_out = (v_in * r1)/(r1 + r2)
    return round(v_out, 3)

def calculate_lookup_table_resistance_voltage(wind_vanes_resistance_lookup_table_list, r1, v_in):
    '''
    Calolca la tabella resistenza-tensione
    Reference Link: https://projects.raspberrypi.org/en/projects/build-your-own-weather-station/7
    :return:
    '''
    try:
        resistance_voltage_dict = {}
        for resistance in wind_vanes_resistance_lookup_table_list:
            resistance_voltage_dict.update({resistance: round(voltage_divider(Configuration.WIND_SENSOR_VANES_R1, resistance, Configuration.WIND_SENSOR_VANES_VIN), 1)})
        logger.info(resistance_voltage_dict)
        return True, resistance_voltage_dict
    except Exception as e:
        message = "ERROR: An error occurred during calculate_lookup_table_resistance_voltage of wind sensor. %s" % e
        logger.error(message)
        return False, {}


def init_wind_speed_sensor(gpio_pin_number):
    '''

    :return:
    '''
    try:
        wind_speed_sensor_switch_reed = Button(gpio_pin_number)
        wind_speed_sensor_switch_reed.when_pressed = spin
        return True
    except Exception as e:
        message = "ERROR: An error occurred during init_wind_speed_sensor of wind sensor. %s" % e
        logger.error(message)
        return False


def spin():
    '''
    Every half-rotation, add 1 to count
    :return:
    '''
    global wind_count
    wind_count = wind_count + 1


def calculate_wind_speed(time_sec):
    '''

    :param time_sec:
    :return: {"wind_speed": km_per_hour * Configuration.WIND_ADJUSTMENT}
    '''
    try:
        global wind_count
        global gust
        wind_speed_dict = {}
        cm_in_a_km = 100000.0
        secs_in_an_hour = 3600
        circumference_cm = (2 * math.pi) * Configuration.WIND_ANEMOMETER_RADIUS_CM
        rotations = wind_count / 2.0
        dist_km = (circumference_cm * rotations) / cm_in_a_km
        km_per_sec = dist_km/time_sec
        km_per_hour = km_per_sec * secs_in_an_hour
        wind_speed_dict.update({"wind_speed": km_per_hour * Configuration.WIND_ADJUSTMENT})
        return True, wind_speed_dict
    except Exception as e:
        message = "ERROR: An error occurred during get_measurements of wind sensor. %s" % e
        logger.error(message)
        return False, {}


def get_measurements_thread(measurements_data_file_path=Configuration.WIND_SENSOR_MEASUREMENTS_DATA_FILE_PATH,
                            measurements_data_store_mode=Configuration.WIND_SENSOR_MEASUREMENTS_DATA_STORE_MODE):
    '''

    :param measurements_data_file_path:
    :param measurements_data_store_mode:
    :return:
    '''
    f = None
    try:
        f = open(measurements_data_file_path, measurements_data_store_mode)
        while True:
            start_time = time.time()
            while time.time() - start_time <= Configuration.WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME:
                reset_wind_count()
                time.sleep(Configuration.WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
                wind_speed_status, wind_speed_dict = calculate_wind_speed()
                if wind_speed_status:
                    store_speeds.append(wind_speed_dict.get("wind_speed"))

            wind_gust = max(store_speeds)
            wind_speed_mean = statistics.mean(store_speeds)
            message_to_store = "wind_speed_mean=%s;wind_gust=%s\n" % (str(wind_speed_mean), str(wind_gust))
            logger.info("WIND SENSOR Measurements: %s" % message_to_store)
            f.write(message_to_store)
            logger.info("WIND SENSOR Measurements stored correctly in file.")
            f.flush()
    except Exception as e:
        message = "ERROR: An error occurred during get_measurements of wind sensor. %s" % e
        logger.error(message)
    finally:
        if f:
            f.close()


def reset_wind_count():
    global wind_count
    wind_count = 0

def reset_gust():
    '''

    :return:
    '''
    global gust
    gust = 0

def init_adc_mcp3008(channel=Configuration.WIND_SENSOR_ADC_MCP3008_CHANNEL):
    '''

    :return:
    '''
    try:
        adc = None
        adc = MCP3008(channel=channel)
        return True, adc
    except Exception as e:
        message = "ERROR: An error occurred during init_adc_mcp3008 of wind sensor. %s" % e
        logger.error(message)
        return False, None


def get_average(angles):
    sin_sum = 0
    cos_sum = 0

    for angle in angles:
        r = math.radians(angle)
        sin_sum += math.sin(r)
        cos_sum += math.cos(r)

    flen = float(len(angles))
    s = sin_sum /flen
    c = cos_sum / flen
    arc = math.degrees(math.atan(s/c))
    average = 0.0

    if s > 0 and c > 0:
        average = arc
    elif c < 0:
        average = arc + 180
    elif s < 0 and c > 0:
        average = arc + 360

    return 0.0 if average == 360 else average

#get_value()
def get_wind_direction_average(adc, v_in=Configuration.WIND_SENSOR_VANES_VIN, wind_sensor_vanes_volt_angle_dict=Configuration.WIND_SENSOR_VANES_VOLT_ANGLE_DICT, wind_time_interval_direction=Configuration.WIND_TIME_INTERVAL_DIRECTION):
    '''

    :param length:
    :return:
    '''
    data = []
    start_time = time.time()

    while time.time() - start_time <= wind_time_interval_direction:
        wind = round(adc.value*v_in, 1)
        if not wind in wind_sensor_vanes_volt_angle_dict:
            logger.warning('WARNING: unknown wind direction value: %s' % str(wind))
        else:
            data.append(wind_sensor_vanes_volt_angle_dict[wind])

    return get_average(data)

def init_rain_sensor(gpio_pin_number):
    '''

    :return:
    '''
    try:
        rain_sensor_switch_reed = Button(gpio_pin_number)
        rain_sensor_switch_reed.when_pressed = bucket_tipped
        return True
    except Exception as e:
        message = "ERROR: An error occurred during init_rain_sensor of weather sensor. %s" % e
        logger.error(message)
        return False

def bucket_tipped():
    '''

    :return:
    '''
    global rain_sensor_count
    rain_sensor_count += 1

def get_rainfall():

    return rain_sensor_count * Configuration.RAIN_GAUGE_BUCKET_SIZE

def reset_rainfall():
    global rain_sensor_count
    rain_sensor_count = 0

