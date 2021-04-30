# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import time
from threading import Thread
import paho.mqtt.client as mqtt

# AMBIENT IMPORT
from Utils.Logger import Logger
import Utils.Configs as Configs


# LA NUOVA CLASSE Client
class Client:

    def __init__(self, configs):
        # init logger
        self.configs = Configs.load(file_name=configs)
        self.logger = Logger(file_name=self.configs["log_file"])
        # init client
        self.client = mqtt.Client()
        self.client.username_pw_set(self.configs["token"])
        # set abstract functions
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log
        # set default attributes
        self.host = self.configs["host"]
        self.port = self.configs["port"]
        self.keep_alive = self.configs["keep_alive"]
        self.thread = None
        self.qos = self.configs["qos"]

    # FUNZIONE DI TRANSMISSIONE DATI
    def transmit_data(self):
        while self.client.is_connected():
            time.sleep(10)

    # ESEGUITA QUANDO CI SI CONNETTE
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:  # connesso correttamente
            self.logger.info("MQTT Client", "Connesso a {}:{}".format(self.host, self.port))
            # imposta la path di invio
            client.subscribe('v1/devices/me/attributes/response/+', self.qos)
            # avvia il thread di invio dati
            self.thread = Thread(target=self.transmit_data)
            self.thread.start()
        else:  # errore nella connessione
            Logger.err("MQTT Client", "Connessione fallita. Codice errore: {}".format(rc))

    # ESEGUITA QUANDO CI SI DISCONNETTE
    def on_disconnect(self, client, userdata, message):
        self.logger.info("MQTT Client", "Disconnesso: {}".format(message))

    # ESEGUITA QUANDO VIENE RICEVUTO UN MESSAGGIO DAL SERVER
    def on_message(self, client, userdata, message):
        self.logger.info("MQTT Client", "Messaggio ricevuto: {}".format(str(message.payload.decode("utf-8"))))

    # ESEGUITA QUANDO VIENE PUBBLICATO UN RISULTATO SU SERVER
    def on_publish(self, lient, userdata, mid):
        self.logger.info("MQTT Client", "Messaggio inviato")

    # ESEGUITA QUANDO VIENE INSERITA UNA PATH PER L'INVIO DEI DATI
    def on_subscribe(self, client, userdata, mid, granted_qos):
        self.logger.info("MQTT Client", "Mid: {}. QoS garantiti: {}".format(mid, granted_qos))

    # FUNZIONE DI LOG
    def on_log(self, client, userdata, level, buf):
        if level == mqtt.MQTT_LOG_INFO or level == mqtt.MQTT_LOG_NOTICE or level == mqtt.MQTT_LOG_DEBUG:
            self.logger.info("MQTT Client", buf)
        elif level == mqtt.MQTT_LOG_WARNING:
            self.logger.warn("MQTT Client", buf)
        elif level == mqtt.MQTT_LOG_ERR:
            self.logger.err("MQTT Client", buf)

    def connect(self):
        self.logger.info("MQTT Client", "Tentativo di connessione a {}:{}".format(self.host, self.port))
        self.client.connect(self.host, self.port, self.keep_alive)
        self.client.loop_forever()
