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
from Utils.Logger import get_logger
import Utils.Configs as Configs


# LA CLASSE ESTESA DA TUTTI I CLIENT
class AbstractClient(Thread):

    # INIZIALIZZA LE BASI DEL CLIENT
    def __init__(self, client_name):
        Thread.__init__(self)
        # carica le variabili di base
        self.can_run = True
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
    def __on_connect(self, client, userdata, flags, rc):
        if rc == 0:  # connesso correttamente
            host = self.configurations["host"]
            port = self.configurations["port"]
            self.logger.debug("MQTT", "Connected to {}:{}".format(host, port))
            # imposta la path di invio
            client.subscribe('v1/devices/me/attributes/response/+', self.configurations["qos"])
            # avvia il thread di invio dati
            if not self.is_alive():
                Thread.start(self)
        else:  # errore nella connessione
            self.logger.err("MQTT", "Connection failed. Error code: {}".format(rc))

    # ESEGUITA QUANDO CI SI DISCONNETTE
    def __on_disconnect(self, client, userdata, message):
        self.logger.debug("MQTT", "Disconnected: {}".format(message))

    # ESEGUITA QUANDO VIENE RICEVUTO UN MESSAGGIO DAL SERVER
    def __on_message(self, client, userdata, message):
        self.logger.debug("MQTT", "Message sent: {}".format(str(message.payload.decode("utf-8"))))

    # ESEGUITA QUANDO VIENE PUBBLICATO UN RISULTATO SU SERVER
    def __on_publish(self, lient, userdata, mid):
        self.logger.debug("MQTT", "Message sent")

    # ESEGUITA QUANDO VIENE INSERITA UNA PATH PER L'INVIO DEI DATI
    def __on_subscribe(self, client, userdata, mid, granted_qos):
        self.logger.debug("MQTT", "Mid: {}. Granted QOS: {}".format(mid, granted_qos))

    # FUNZIONE DI LOG
    def __on_log(self, client, userdata, level, buf):
        if level == mqtt.MQTT_LOG_DEBUG:
            self.logger.debug("MQTT", buf)
        elif level == mqtt.MQTT_LOG_INFO or level == mqtt.MQTT_LOG_NOTICE:
            self.logger.info("MQTT", buf)
        elif level == mqtt.MQTT_LOG_WARNING:
            self.logger.warn("MQTT", buf)
        elif level == mqtt.MQTT_LOG_ERR:
            self.logger.err("MQTT", buf)

    # METODO CHIAMATO OGNI [publish_time]
    def on_publish(self):
        self.logger.warn(self.client_name, "AbstractClient.on_publish(self) not implemented!")

    # METODO CHIAMATO QUANDO IL CLIENT VIENE STOPPATO
    def on_stop(self):
        self.logger.info(self.client_name, "AbstractClient.on_stop(self) not implemented!")

    # CHIAMATO DA Thread.start(self)
    def run(self):
        self.logger.info(self.client_name, "Started client")
        time.sleep(self.configurations["publish_time"])  # attendi che i sensori lavorino prima
        while self:
            begin = time.time()
            try:
                self.on_publish()
            except Exception as e:
                self.logger.err(self.client_name, "A {} error occured: {}".format(type(e), e))
                self.can_run = False
                begin = time.time()  # forza l'uscita dalla funzione
            end = time.time()
            if (end - begin) < self.configurations["publish_time"]:
                time.sleep(self.configurations["publish_time"] - (end - begin))
            else:
                self.logger.warn(self.client_name, "Publish time is lower of {} seconds".format(end - begin))
        self.logger.info(self.client_name, "Stopped client")

    # PRIMA DI CHIAMARE IL VERO JOIN INVALIDA IL CLIENT
    def join(self, timeout=...):
        self.can_run = False
        AbstractClient.join(self)

    # AL POSTO DI FAR PARTIRE IL THREAD PROVA A CONNETTERSI AL CLIENT MQTT
    def start(self):
        host = self.configurations["host"]
        port = self.configurations["port"]
        keep_alive = self.configurations["keep_alive"]
        self.logger.info(self.client_name, "Connecting to {}:{}".format(host, port))
        self.client.connect(host, port, keep_alive)
        self.client.loop_forever()

    # VERIFICA SE IL CLIENT SI TROVA IN UNO STATO ACCETTABILE PER L'ESECUZIONE
    def __bool__(self):
        return self.can_run
