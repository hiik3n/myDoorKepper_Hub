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
                _data = self._parse_ble_payload_v1(message.payload.get_items()['16b Service Data'])

                if _data is None:
                    return False

                if _data[0] == '0001':
                    _payload = encode_json({'ts': message.ts,
                                            'battery_level': round(_data[1] * 3.6 * 100 / 1023)/100})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("battery/%s/%s" % (message.recipient,
                                                                     message.sender),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif _data[0] == '0002':
                    _payload = encode_json({'ts': message.ts,
                                            'temperature': round(_data[1] * 3.6 * 10000 / 1023)/100})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       'lm35'),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                else:
                    self.logger.warning("unknown ble payload %s" % str(_data))
                    return False

            except KeyError as e:
                self.logger.warning("ble payload error %s" % repr(e))
                return False
        else:
            return None

    def add_connector(self, connector):
        self.connector = connector

    # def _parse_ble_payload_v0(self, payload_str):
    #     if len(payload_str) != 6:
    #         self.logger.warning("ble payload error (len!=6) %s" % payload_str)
    #         return False
    #     try:
    #         return int(payload_str[0:4], 16)/100
    #     except KeyError as e:
    #         self.logger.warning("ble payload error (int(%s, 16)) %s" % (payload_str[4:6], payload_str))
    #         return False

    def _parse_ble_payload_v1(self, payload_str):
        if len(payload_str) != 8:
            self.logger.warning("ble payload error (len!=8) %s" % payload_str)
            return None
        try:
            return payload_str[0:4], int(payload_str[5:8], 16)
        except KeyError as e:
            self.logger.warning("ble payload error %s" % payload_str)
            return None


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    bcPkgLM35 = BleMessage(mac="abc",
                       rssi=-53,
                       ts=123456789,
                       sender='abc',
                       recipient='def',
                       payload=BlePayload(payload=[('1', 'Complete 16b Services', '00aa'),
                                                   ('1', 'Complete Local Name', 'XXX\x00'),
                                                   ('1', '16b Service Data', '0002004a'),
                                                   ('1', 'Manufacturer', '0002004a'),
                                                   ('1', 'Flags', '06')]))

    bcPkgBatt = BleMessage(mac="abc",
                       rssi=-53,
                       ts=123456789,
                       sender='abc',
                       recipient='def',
                       payload=BlePayload(payload=[('1', 'Complete 16b Services', '00aa'),
                                                   ('1', 'Complete Local Name', 'XXX\x00'),
                                                   ('1', '16b Service Data', '0001033b'),
                                                   ('1', 'Manufacturer', '0002004a'),
                                                   ('1', 'Flags', '06')]))
    handler = BleMessageHandler()
    handler.add_connector(MqttConnectorInterface())
    print(handler.process(bcPkgLM35))
    print(handler.process(bcPkgBatt))
