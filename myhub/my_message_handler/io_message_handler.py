import logging
from myhub.my_message_handler.message_handler_interface import MessageHandlerInterface
from myhub.my_message import IOMessage
from myhub.helper_functions import encode_json
from myhub.my_connector import MqttConnectorInterface


class IOMessageHandler(MessageHandlerInterface):
    messageCode = "IO_MSG"

    def __init__(self):
        self.logger = logging.getLogger()
        self.connector = None

    def process(self, message):
        if isinstance(message, IOMessage):
            if self.connector is None:
                self.logger.warning("Connector for IO Message Handler is None")
                return False

            self.logger.debug("processing %s" % repr(message))

            assert isinstance(message, IOMessage)
            try:
                if message.type == IOMessage.SHT_MESSAGE:
                    _data = self._parse_sht_payload(message.payload)
                    _payload = encode_json({'ts': message.ts,
                                            'temperature': _data[0],
                                            'humidity': _data[1]})
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       IOMessage.SHT_MESSAGE),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif message.type == IOMessage.PIR_MESSAGE:
                    _payload = encode_json({'ts': message.ts,
                                            'pir': message.payload})
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       IOMessage.PIR_MESSAGE),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif message.type == IOMessage.CONTACT_MESSAGE:
                    _payload = encode_json({'ts': message.ts,
                                            'contact': message.payload})
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       IOMessage.CONTACT_MESSAGE),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                else:
                    self.logger.warning("Unknown IO Payload %s" % repr(message))
                    return False
            except KeyError as e:
                self.logger.warning("IO payload error %s" % repr(e))
                return False
        else:
            return None

    def add_connector(self, connector):
        self.connector = connector

    def _parse_sht_payload(self, payload):
        try:
            _payloadSplited = payload.split(',')
            if len(_payloadSplited) != 2:
                self.logger.warning('SHT payload error (!=2) %s' % payload)
                return False
            # Evaluate results
            float(_payloadSplited[0])
            float(_payloadSplited[1])

            return _payloadSplited
        except KeyError as e:
            self.logger.warning("ble payload error (int(%s, 16)) %s" % (payload[4:6], payload))
            return False


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    msg =IOMessage(type=IOMessage.SHT_MESSAGE, payload='1,2', ts=1234567, sender='abc', recipient='def')
    handler = IOMessageHandler()
    handler.add_connector(MqttConnectorInterface())
    logging.debug(handler.process(msg))
