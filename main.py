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

import Utils.bme280_sensor.bme280_api as bme280_sensor_api
import Utils.ds18b20_sensor.ds18b20_api as ds18b20_sensor_api
import Utils.weather_sensor_assembly_80422.wsa_80422_api as weather_sensor_assembly_80422_api
import time
import statistics

import json
import paho.mqtt.client as mqtt
import threading


store_wind_speed_list = []
store_wind_direction_list = []

def main():
    # CONFIGURAZIONE PARAMETRI THINGSBOARD
    #
    # Data capture and upload interval in seconds. Less interval will eventually hang the DHT22.
    # INTERVAL=2
    client = mqtt.Client()
    # ssl.match_hostname = lambda x, y: True
    # client.tls_set(ca_certs="mqtt_pkcs12.pem", certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
    #           tls_version=ssl.PROTOCOL_TLSv1, ciphers=None)

    # Set access token
    client.username_pw_set(Configuration.THINGSBOARD_ACCESS_TOKEN)

    # callback cycle client
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    # Connect to ThingsBoard using default MQTT port and 60 seconds keep alive interval
    client.connect(Configuration.THINGSBOARD_HOST, Configuration.THINGSBOARD_MQTT_PORT,
                   Configuration.THINGSBOARD_KEEP_ALIVE)

    client.loop_forever()

def on_publish(client, userdata, result):
    print("Data published on '%s', userdata: %s, result:%s\n" % (Configuration.THINGSBOARD_HOST, str(userdata), str(result)))


def on_message(client, userdata, message):
    print("message received ", str(message.payload.decode("utf-8")))
    print("message topic=", message.topic)
    print("message qos=", message.qos)
    print("message retain flag=", message.retain)


def on_connect(client, userdata, flags, rc):
    if not rc:
        print("Connection established correctly on IP '{}' and PORT '{}'...".format(
            Configuration.THINGSBOARD_HOST,
            Configuration.THINGSBOARD_MQTT_PORT))
        client.subscribe('v1/devices/me/attributes/response/+', Configuration.THINGSBOARD_QOS)

        # Start thread for data transmission on ThingsBoard
        thread_transmit_data = threading.Thread(target=transmit_data, args=(client,))
        thread_transmit_data.start()

    else:
        print("Connection not established correctly, with error code: {} ".format(rc))


def on_disconnect(client, userdata, rc):
    print("disconnecting reason: " + str(rc))



def transmit_data(client_mqtt):

    global store_wind_direction_list, store_wind_speed_list
    f = None
    measurements_dict = {}
    try:

        f = open(Configuration.WEATHER_STATION_DATA_FILE_PATH, Configuration.WEATHER_STATION_DATA_FILE_MODE)
        f.write("time;wind_direction_average;wind_gust;wind_speed_mean;rainfall;ground_temperature;humidity;pressure;ambient_temperature\n")

        # Get measurements from BME280 SENSOR -> {"humidity": humidity, "pressure": pressure, "ambient_temperature": ambient_temperature}
        bme280_sensor_init_status, bme280_sensor_bus = bme280_sensor_api.init_bme280_sensor(Configuration.BME280_SENSOR_PORT, Configuration.BME280_SENSOR_ADDRESS)

        # Get measurements from DS18B20 SENSOR -> {"ground_temperature": ground_temp_c}
        # Create data file
        ds18b20_sensor_obj = ds18b20_sensor_api.DS18B20(Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_FILE_PATH, Configuration.DS18B20_SENSOR_MEASUREMENTS_DATA_STORE_MODE)


        # Get measurements from WIND SENSOR and RAIN SENSOR -> {"wind_speed": speed_km_per_hour}
        wind_sensor_speed_init_status = weather_sensor_assembly_80422_api.init_wind_speed_sensor()
        wind_sensor_adc_status, adc = weather_sensor_assembly_80422_api.init_adc_mcp3008(Configuration.WIND_SENSOR_ADC_MCP3008_CHANNEL)
        rain_sensor_init_status = weather_sensor_assembly_80422_api.init_rain_sensor()

        start_time_data_rec = time.time()
        while True:
            start_time = time.time()
            while time.time() - start_time <= Configuration.WIND_TIME_INTERVAL:
                wind_start_time = time.time()
                weather_sensor_assembly_80422_api.reset_wind_count()
                while time.time() - wind_start_time <= Configuration.WIND_TIME_INTERVAL_DIRECTION:
                    if wind_sensor_adc_status:
                        store_wind_direction_list.append(weather_sensor_assembly_80422_api.get_wind_direction_average(adc))
                status_final_wind_speed, final_wind_speed_dict = weather_sensor_assembly_80422_api.calculate_wind_speed(Configuration.WIND_SENSOR_MEASUREMENTS_DATA_WAIT_TIME)
                if status_final_wind_speed:
                    store_wind_speed_list.append(final_wind_speed_dict.get("wind_speed"))

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
                status_ground_temp, ground_temp_measurement_dict = ds18b20_sensor_obj.get_measurements()
                if status_ground_temp:
                    ground_temp = ground_temp_measurement_dict.get("ground_temperature")

            if bme280_sensor_init_status:
                status_bme280_measurements, bme280_sensor_measurements_dict = bme280_sensor_api.get_measurements(bme280_sensor_bus)
                if status_bme280_measurements:
                    humidity = bme280_sensor_measurements_dict.get("humidity")
                    pressure = bme280_sensor_measurements_dict.get("pressure")
                    ambient_temperature = bme280_sensor_measurements_dict.get("ambient_temperature")

            f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (str(round(time.time() - start_time_data_rec, 3)), str(wind_direction_average), str(wind_gust), str(wind_speed_mean), str(rainfall), str(ground_temp), str(humidity), str(pressure), str(ambient_temperature)))
            f.flush()

            # Dizionario misure da trasmettere su Thingsboard
            measurements_dict = {"wind_direction_average": str(round(wind_direction_average, 3)),
                                 "wind_gust": str(round(wind_gust, 3)),
                                 "wind_speed_mean": str(round(wind_speed_mean, 3)),
                                 "rainfall": str(round(rainfall, 3)),
                                 "ground_temp": str(round(ground_temp, 3)),
                                 "humidity": str(round(humidity, 3)),
                                 "pressure": str(round(pressure, 3)),
                                 "ambient_temperature": str(round(ambient_temperature, 3))}

            # Si pubblicano i dati su ThingsBoard
            client_mqtt.publish('v1/devices/me/telemetry', json.dumps(measurements_dict), Configuration.THINGSBOARD_QOS)
            logger.info("OK data published: %s" % str(measurements_dict))

            time.sleep(Configuration.PUBLISH_TIME)



    except Exception as e:
        logger.error("ERROR: An error occurred: %s" % e)
    except KeyboardInterrupt:
        logger.info("Stop Script! by keyboard")
    finally:
        if f:
            f.close()


if __name__ == '__main__':
    main()