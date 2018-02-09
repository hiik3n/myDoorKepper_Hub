import logging
from bisect import bisect
from myhub.my_message_handler.message_handler_interface import MessageHandlerInterface
from myhub.my_message import BleMessage, BlePayload
from myhub.helper_functions import encode_json, NTC_10K_TEMPERATURE_REFERENCE_LIST, NTC_10K_RESISTANCE_REFERENCE_LIST
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
                                            'rssi': message.rssi,
                                            'battery_level': round(_data[1] * 3.6 / 1023, 2)})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("battery/%s/%s" % (message.recipient,
                                                                     message.sender),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif _data[0] == '0002':
                    _payload = encode_json({'ts': message.ts,
                                            'rssi': message.rssi,
                                            'temperature': round(_data[1] * 3.6 * 100 / 1023, 2)})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       'lm35ble'),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif _data[0] == '0003':
                    _ntcOhm = _data[2] * 10 / (_data[1] - _data[2])
                    _ntcIndex = bisect(NTC_10K_RESISTANCE_REFERENCE_LIST, _ntcOhm)
                    _listLen = len(NTC_10K_TEMPERATURE_REFERENCE_LIST)
                    if _ntcIndex == 0:
                        self.logger.warning("Data error %s" % message)
                        return False
                    _ntcOhmHigh = NTC_10K_RESISTANCE_REFERENCE_LIST[_ntcIndex]
                    _ntcOhmLow = NTC_10K_RESISTANCE_REFERENCE_LIST[_ntcIndex - 1]
                    _ntcTempHigh = NTC_10K_TEMPERATURE_REFERENCE_LIST[_listLen - _ntcIndex - 1]
                    _ntcTempLow = NTC_10K_TEMPERATURE_REFERENCE_LIST[_listLen - _ntcIndex]
                    _ntcTemp = round(((_ntcOhm - _ntcOhmLow) / (_ntcOhmHigh - _ntcOhmLow) * (_ntcTempHigh - _ntcTempLow)) + _ntcTempLow, 2)
                    _payload = encode_json({'ts': message.ts,
                                            'rssi': message.rssi,
                                            'temperature': _ntcTemp,
                                            'battery_level': round(_data[1] * 3.6 / 1023, 2)})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       'ntc10ble'),
                                                  payload=_payload,
                                                  qos=0,
                                                  retain=False)
                elif _data[0] == '0004':
                    _ntcOhm = _data[2] * 10 / (_data[1] - _data[2])
                    _ntcIndex = bisect(NTC_10K_RESISTANCE_REFERENCE_LIST, _ntcOhm)
                    _listLen = len(NTC_10K_TEMPERATURE_REFERENCE_LIST)
                    if _ntcIndex == 0:
                        self.logger.warning("Data error %s" % message)
                        return False
                    _ntcOhmHigh = NTC_10K_RESISTANCE_REFERENCE_LIST[_ntcIndex]
                    _ntcOhmLow = NTC_10K_RESISTANCE_REFERENCE_LIST[_ntcIndex - 1]
                    _ntcTempHigh = NTC_10K_TEMPERATURE_REFERENCE_LIST[_listLen - _ntcIndex - 1]
                    _ntcTempLow = NTC_10K_TEMPERATURE_REFERENCE_LIST[_listLen - _ntcIndex]
                    _ntcTemp = round(((_ntcOhm - _ntcOhmLow) / (_ntcOhmHigh - _ntcOhmLow) * (_ntcTempHigh - _ntcTempLow)) + _ntcTempLow, 2)
                    _ldr = _data[3]
                    _dor = _data[4]
                    _payload = encode_json({'ts': message.ts,
                                            'rssi': message.rssi,
                                            'temperature': _ntcTemp,
                                            'light': _ldr,
                                            'door': _dor,
                                            'battery_level': round(_data[1] * 3.6 / 1023, 2)})
                    self.logger.debug('payload %s' % str(_payload))
                    return self.connector.publish("sensor/%s/%s/%s" % (message.recipient,
                                                                       message.sender,
                                                                       'ntcldrdorble'),
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

    def _parse_ble_payload_v1(self, payload_str):
        if len(payload_str) != 8 and len(payload_str) != 12 and len(payload_str) != 18:
            self.logger.warning("ble payload error (len!=8|12) %s" % payload_str)
            return None
        try:
            if len(payload_str) == 8:
                return payload_str[0:4], int(payload_str[5:8], 16)
            elif len(payload_str) == 12:
                return payload_str[0:4], int(payload_str[5:8], 16), int(payload_str[9:12], 16)
            elif len(payload_str) == 18:
                return payload_str[0:4],\
                       int(payload_str[5:8], 16),\
                       int(payload_str[9:12], 16), \
                       int(payload_str[13:16], 16),\
                       int(payload_str[17:18], 16)
            else:
                self.logger.warning("Should not be here %s" % payload_str)
                return None
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

    bcPkgNtc = BleMessage(mac="abc",
                           rssi=-53,
                           ts=123456789,
                           sender='abc',
                           recipient='def',
                           payload=BlePayload(payload=[('1', 'Complete 16b Services', '00aa'),
                                                       ('1', 'Complete Local Name', 'XXX\x00'),
                                                       ('1', '16b Service Data', '0003030c0184'),
                                                       ('1', 'Manufacturer', '0002004a'),
                                                       ('1', 'Flags', '06')]))
    bcPkgNtcLdrDor = BleMessage(mac="abc",
                          rssi=-53,
                          ts=123456789,
                          sender='abc',
                          recipient='def',
                          payload=BlePayload(payload=[('1', 'Complete 16b Services', '00aa'),
                                                      ('1', 'Complete Local Name', 'XXX\x00'),
                                                      #000400a400a600a700 0004038a01c9003e00
                                                      ('1', '16b Service Data', '0004038a01c9003e00'),
                                                      ('1', 'Manufacturer', '0002004a'),
                                                      ('1', 'Flags', '06')]))

    handler = BleMessageHandler()
    handler.add_connector(MqttConnectorInterface())
    print(handler.process(bcPkgLM35))
    print(handler.process(bcPkgBatt))
    print(handler.process(bcPkgNtc))
    print(handler.process(bcPkgNtcLdrDor))
