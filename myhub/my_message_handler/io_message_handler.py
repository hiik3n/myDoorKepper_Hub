import logging
from myhub.my_message_handler.message_handler_interface import MessageHandlerInterface
from myhub.my_message import IOMessage


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
                    return self.connector.publish("sensor/hub01/knot02/sht",
                                                  payload=("%s,%s" % (_data[0], _data[1])),
                                                  qos=0,
                                                  retain=False)
                else:
                    self.logger.warning("Unknown IO Payload %s" % repr(e))
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
            self.logger.warning("ble payload error (int(%s, 16)) %s" % (payload_str[4:6], payload_str))
            return False


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    msg =IOMessage(type=IOMessage.SHT_MESSAGE, payload='1,2')
    handler = IOMessageHandler()
    handler.add_connector('temp')
    logging.debug(handler.process(msg))
