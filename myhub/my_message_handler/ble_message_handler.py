import logging
from myhub.my_message_handler.message_handler_interface import MessageHandlerInterface
from myhub.my_message import BleMessage, BlePayload
from myhub.helper_functions import encode_json
from myhub.my_connector import MqttConnectorInterface


class BleMessageHandler(MessageHandlerInterface):
    messageCode = "BLE_MSG"

    def __init__(self):
        self.logger = logging.getLogger()
        self.connector = None

    def process(self, message):
        if isinstance(message, BleMessage):
            if self.connector is None:
                self.logger.warning("Connector for Ble Message Handler is None")
                return False

            self.logger.debug("processing %s" % repr(message))

            assert isinstance(message, BleMessage)
            try:
                # self.logger.debug("mac: %s, rssi: %s, data: %s" % (message.mac, message.rssi,
                #                                                    message.payload.get_items()['16b Service Data']))
                _data = self._parse_ble_payload_v0(message.payload.get_items()['16b Service Data'])

                _payload = encode_json({'ts': message.ts,
                                        'temperature': _data})
                self.logger.debug('payload %s' % str(_payload))
                return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                   message.sender,
                                                                   'lm35'),
                                              payload=_payload,
                                              qos=0,
                                              retain=False)

                # return self.connector.publish("sensor/hub02/knot02/lm35",
                #                               payload=("%s,%s" % (_data, 0)),
                #                               qos=0,
                #                               retain=False)
            except KeyError as e:
                self.logger.warning("ble payload error %s" % repr(e))
                return False
        else:
            return None

    def add_connector(self, connector):
        self.connector = connector

    def _parse_ble_payload_v0(self, payload_str):
        if len(payload_str) != 6:
            self.logger.warning("ble payload error (len!=6) %s" % payload_str)
            return False
        try:
            return int(payload_str[0:4], 16)/100
        except KeyError as e:
            self.logger.warning("ble payload error (int(%s, 16)) %s" % (payload_str[4:6], payload_str))
            return False


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    bcPkg = BleMessage(mac="abc",
                       rssi=-53,
                       ts=123456789,
                       sender='abc',
                       recipient='def',
                       payload=BlePayload(payload=[('1', 'Complete 16b Services', '00aa'),
                                                   ('1', 'Complete Local Name', 'GAPButton\x00'),
                                                   ('1', '16b Service Data', '0b451c'),
                                                   ('1', 'Flags', '06')]))
    handler = BleMessageHandler()
    handler.add_connector(MqttConnectorInterface())
    print(handler.process(bcPkg))
