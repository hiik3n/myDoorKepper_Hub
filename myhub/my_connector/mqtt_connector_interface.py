

class MqttConnectorInterface(object):

    def connect(self):
        pass

    def disconnect(self):
        pass

    def reconnect(self):
        pass

    def get_mqtt_handler(self):
        pass

    def publish(self, topic, payload=None, qos=0, retain=False):
        pass

    def is_connect(self):
        pass
