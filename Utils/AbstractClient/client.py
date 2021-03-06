# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
import time
from threading import Thread
import paho.mqtt.client as mqtt

# AMBIENT IMPORT
from Utils.Logger import get_logger, destroy_logger
import Utils.Configs as Configs


# LA CLASSE ESTESA DA TUTTI I CLIENT
class AbstractClient(Thread):

    # INIZIALIZZA LE BASI DEL CLIENT
    def __init__(self, client_name):
        Thread.__init__(self)
        self.valid = False
        self.client_name = client_name
        self.configurations = Configs.load(client_name)
        self.logger = get_logger(self.configurations["logger"])
        # carica il client mqtt
        self.client = mqtt.Client()
        self.client.username_pw_set(self.configurations["token"])
        # carica i callback per le funzioni del client mqtt
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_message = self.__on_message
        self.client.on_publish = self.__on_publish
        self.client.on_subscribe = self.__on_subscribe
        self.client.on_log = self.__on_log

    # ESEGUITA QUANDO CI SI CONNETTE
    def __on_connect(self, client, _userdata, _flags, rc):
        if rc == 0:  # connesso correttamente
            host = self.configurations["host"]
            port = self.configurations["port"]
            # valida il client
            self.valid = True
            # imposta la path di invio
            client.subscribe('v1/devices/me/attributes/response/+', self.configurations["qos"])
            # logga la riuscita della connessione
            self.logger.info("MQTT", "Connected to {}:{}".format(host, port))
        else:  # errore nella connessione
            self.logger.err("MQTT", "Connection failed. Error code: {}".format(rc))
            self.client.disconnect()

    # ESEGUITA QUANDO CI SI DISCONNETTE
    def __on_disconnect(self, _client, _userdata, message):
        self.logger.debug("MQTT", "Disconnected: {}".format(message))

    # ESEGUITA QUANDO VIENE RICEVUTO UN MESSAGGIO DAL SERVER
    def __on_message(self, _client, _userdata, message):
        self.logger.debug("MQTT", "Received message: {}".format(str(message.payload.decode("utf-8"))))

    # ESEGUITA QUANDO VIENE PUBBLICATO UN RISULTATO SU SERVER
    def __on_publish(self, _client, _userdata, _mid):
        self.logger.debug("MQTT", "Sent message")

    # ESEGUITA QUANDO VIENE INSERITA UNA PATH PER L'INVIO DEI DATI
    def __on_subscribe(self, _client, _userdata, mid, granted_qos):
        self.logger.debug("MQTT", "Mid: {}. Granted QoS: {}".format(mid, granted_qos))

    # FUNZIONE DI LOG
    def __on_log(self, _client, _userdata, level, buf):
        if level == mqtt.MQTT_LOG_NOTICE or level == mqtt.MQTT_LOG_DEBUG:
            self.logger.debug("MQTT", buf)
        elif level == mqtt.MQTT_LOG_INFO:
            self.logger.info("MQTT", buf)
        elif level == mqtt.MQTT_LOG_WARNING:
            self.logger.warn("MQTT", buf)
        elif level == mqtt.MQTT_LOG_ERR:
            self.logger.err("MQTT", buf)

    # METODO CHIAMATO OGNI [publish_time]
    def publish(self):
        self.logger.warn(self.client_name, "AbstractSensor.read(self) not implemented!")

    # CHIAMATO DA Thread.start(self)
    def run(self):
        self.logger.info(self.client_name, "Started client")
        time.sleep(self.configurations["publish_time"])
        while self:
            begin = time.time()
            try:
                self.publish()
            except Exception as e:
                self.logger.err(self.client_name, e)  # logga l'errore ricevuto
                self.valid = False  # invalida il client
            end = time.time()
            if (end - begin) < self.configurations["publish_time"]:
                time.sleep(self.configurations["publish_time"] - (end - begin))
            else:
                self.logger.warn(self.client_name, "Publish time is lower of {} seconds".format(end - begin))
        self.logger.info(self.client_name, "Stopped client")

    # AL POSTO DI FAR PARTIRE IL THREAD PROVA A CONNETTERSI AL CLIENT MQTT
    def start(self):
        # ottieni i valori
        host = self.configurations["host"]
        port = self.configurations["port"]
        keep_alive = self.configurations["keep_alive"]
        # logga il tentativo di connessione
        self.logger.info(self.client_name, "Trying to connect to {}:{}".format(host, port))
        # prova a connetterti
        try:
            self.client.connect(host, port, keep_alive)
            self.client.loop_start()
            Thread.start(self)
        except Exception as e:
            self.logger.err(self.client_name, e)

    # EFFETTUA IL JOIN SOLO SE IL THREAD E' REALMENTE PARTITO
    def join(self, timeout=...):
        if self.is_alive():
            Thread.join(self)
        destroy_logger(self.configurations["logger"])
        self.client.loop_stop(force=True)

    # VERIFICA SE IL CLIENT E' VALIDO
    def __bool__(self):
        return self.valid
