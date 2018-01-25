import logging
from .message_handler_interface import MessageHandlerInterface


class BleMessageHandler(MessageHandlerInterface):
    messageCode = "BLE_MSG"

    def __init__(self):
        self.logger = logging.getLogger()
        self.connector = None

    def process(self, message):
        return None

    def add_connector(self, connector):
        self.connector = connector


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime
