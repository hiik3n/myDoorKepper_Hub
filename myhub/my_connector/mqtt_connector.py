import logging
import time
import paho.mqtt.client as mqtt
from myhub.my_connector import MqttConnectorInterface


class MqttConnector(MqttConnectorInterface):
    def __init__(self, client_id=None, host='127.0.0.1', port=1883, ca_cert=None, tls_version=None,
                 crt_file=None, key_file=None, username=None, password=None, on_message_callback=None):

        self.logger = logging.getLogger()

        self.subscribeList = []
        self.host = host
        self.port = port

        self._is_connect = False

        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        if on_message_callback is not None:
            self.client.on_message = on_message_callback

        if username is not None:
            self.client.username_pw_set(username, password)

        if tls_version is not None:
            self.client.tls_set(ca_certs=ca_cert, tls_version=tls_version, certfile=crt_file, keyfile=key_file)

    def add_subscribe_topic(self, topic_qos_tuple):
        self.subscribeList.append(topic_qos_tuple)

    def connect(self):
        try:
            self.logger.debug("connect")
            self.client.connect(self.host, self.port)
            self._add_subscription()
            self.client.loop_start()
            # time.sleep(15)
            _count = 10
            while (not self._is_connect) and (_count > 0):
                self.logger.info("Trying connect to Mqtt Broker")
                time.sleep(5)
                _count -= 1

            return _count > 0
        except Exception as e:
            self.logger.error("Can not connect to Broker (%s)" % repr(e))
            return False

    def disconnect(self):
        self.logger.debug("disconnect")
        self.client.loop_stop()
        self.client.disconnect()

    def reconnect(self):
        self.logger.debug("reconnect")
        self.client.loop_stop()
        self.client.reconnect()
        self._add_subscription()
        self.client.loop_start()

    def get_mqtt_handler(self):
        return self.client

    def _add_subscription(self):
        if len(self.subscribeList) > 0:
            self.client.subscribe(self.subscribeList)
        else:
            self.client.subscribe('#')

    def publish(self, topic, payload=None, qos=0, retain=False):
        try:
            self.client.publish(topic, payload, qos, retain)
            return True
        except Exception as e:
            self.logger.error("publish error %s" % repr(e))
            return False

    # The callback for when the client receives a CONNACK response from the server.
    def _on_connect(self, client, userdata, flags, rc):
        self.logger.debug("Connected with result code " + str(rc))
        self._is_connect = True

    # The callback for when a PUBLISH message is received from the server.
    def _on_message(self, client, userdata, msg):
        self.logger.debug("On message " + msg.topic + " " + str(msg.payload))

    def _on_disconnect(self, client, userdata, rc):
        self.logger.debug("Disconnect with result code " + str(rc))
        self._is_connect = False

    def is_connect(self):
        return self._is_connect


if __name__ == "__main__":

    import time
    from config import *

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime


    def on_message_callback(client, userdata, msg):
        assert isinstance(msg, mqtt.MQTTMessage)
        print("%s - %s - %s - %s" % (msg.mid, msg.topic, msg.qos, msg.payload.decode("utf-8")))
        # time.sleep(5)


    print("hello")
    mqttConn = MqttConnector(client_id=MQTT_CLIENTID, host=MQTT_HOST, port=MQTT_PORT,
                             username=MQTT_USERNAME, password=MQTT_PASSWORD,
                             ca_cert=MQTT_CACERT, tls_version=MQTT_TLSVERSION, crt_file=MQTT_CERT, key_file=MQTT_KEY,
                             on_message_callback=on_message_callback)

    mqttConn.connect()
    time.sleep(5)
    while 1:
        mqttConn.publish('test', "test")
        time.sleep(15)