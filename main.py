#encoding: UTF-8
'''
+ IHS +
Version: v0.1
Updated: 12/March/2021 (Covid-19)
@author: +-- NetcomGroup Innovation Team --+
'''
import Configuration
# LOGGER SETUP (qui in mezzo non va fatto l'import di niente altrimenti potrebbe non funzionare il logger)
import logging.config
logging.config.fileConfig(Configuration.LOG_FILE_NAME_PATH_WEATHER_STATION)
logger = logging.getLogger(__name__)

import Utils.bme280_sensor.api as bme280_sensor_api
import Utils.ds18b20_sensor.api as ds18b20_sensor_api
import Utils.weather_sensor_assembly_80422.api as weather_sensor_assembly_80422_api
from gpiozero import Button
import time
import statistics

store_wind_speed_list = []
store_wind_direction_list = []


if __name__ == "__main__":

    f = None
    try:
        # Create data file
        f = open(Configuration.WEATHER_STATION_DATA_FILE_PATH, Configuration.WEATHER_STATION_DATA_FILE_MODE)
        f.write("time;wind_direction_average;wind_gust;wind_speed_mean;rainfall;ground_temperature;humidity;pressure;ambient_temperature\n")

        # Get measurements from BME280 SENSOR -> {"humidity": humidity, "pressure": pressure, "ambient_temperature": ambient_temperature}
        bme280_sensor_init_status, bme280_sensor_bus = bme280_sensor_api.init_bme280_sensor(Configuration.BME280_SENSOR_PORT, Configuration.BME280_SENSOR_ADDRESS)

        # Get measurements from DS18B20 SENSOR -> {"ground_temperature": ground_temp_c}
        ds18b20_sensor_obj = ds18b20_sensor_api.DS18B20(Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_FILE_PATH, Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_STORE_MODE)


        # Get measurements from WIND SENSOR -> {"wind_speed": speed_km_per_hour}
        wind_sensor_speed_init_status = weather_sensor_assembly_80422_api.init_wind_speed_sensor(Configuration.WIND_SENSOR_BUTTON_GPIO_PIN_NUMBER)
        wind_sensor_adc_status, adc = weather_sensor_assembly_80422_api.init_adc_mcp3008(Configuration.WIND_SENSOR_ADC_MCP3008_CHANNEL)
        rain_sensor_init_status = weather_sensor_assembly_80422_api.init_rain_sensor(Configuration.RAIN_GAUGE_BUTTON_GPIO_PIN_NUMBER)

        start_time_data_rec = time.time()
        while True:
            start_time = time.time()
            while time.time() - start_time <= Configuration.WIND_TIME_INTERVAL:
                wind_start_time = time.time()
                weather_sensor_assembly_80422_api.reset_wind_count()
                while time.time() - wind_start_time <= Configuration.WIND_TIME_INTERVAL_DIRECTION:
                    if wind_sensor_adc_status:
                        store_wind_direction_list.append(weather_sensor_assembly_80422_api.get_wind_direction_average(adc))
                final_wind_speed = weather_sensor_assembly_80422_api.calculate_wind_speed(Configuration.WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
                store_wind_speed_list.append(final_wind_speed)

            wind_direction_average = weather_sensor_assembly_80422_api.get_average(store_wind_direction_list)
            wind_gust = max(store_wind_speed_list)
            wind_speed_mean = statistics.mean(store_wind_speed_list)
            rainfall = weather_sensor_assembly_80422_api.get_rainfall()

            # Reset data
            weather_sensor_assembly_80422_api.reset_rainfall()
            weather_sensor_assembly_80422_api.reset_gust()
            store_wind_speed_list = []
            store_wind_direction_list = []

            if ds18b20_sensor_obj:
                ground_temp = ds18b20_sensor_obj.get_measurements().get("ground_temperature")

            if bme280_sensor_init_status == True:
                humidity = bme280_sensor_api.get_measurements(bme280_sensor_bus).get("humidity")
                pressure = bme280_sensor_api.get_measurements(bme280_sensor_bus).get("pressure")
                ambient_temperature = bme280_sensor_api.get_measurements(bme280_sensor_bus).get("ambient_temperature")

            f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (str(time.time() - start_time_data_rec), str(wind_direction_average), str(wind_gust), str(wind_speed_mean), str(rainfall), str(ground_temp), str(humidity), str(pressure), str(ambient_temperature)))
            f.flush()

    except Exception as e:
        logger.error("ERROR: An error occurred: %s" % e)
    finally:
        if f:
            f.close()