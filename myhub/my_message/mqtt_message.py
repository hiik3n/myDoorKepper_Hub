class MqttMessage(object):
    messageCode = "MQTT_MSG"

    def __init__(self, *args, **kwargs):
        self.mid = kwargs['mid'] if 'mid' in kwargs.keys() else None
        self.topic = kwargs['topic'] if 'topic' in kwargs.keys() else None
        self.qos = kwargs['qos'] if 'qos' in kwargs.keys() else None
        self.payload = kwargs['payload'] if 'payload' in kwargs.keys() else None

    def __repr__(self):
        return "%s-%s-%s-%s" % (self.mid, self.topic, self.qos, self.payload)