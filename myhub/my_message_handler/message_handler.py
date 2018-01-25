import logging


class MessageHandler(object):
    messageCode = "ALL_MSG"

    def __init__(self):
        self.logger = logging.getLogger()
        self.connectorList = []

    def process(self, message):
        return None

    def add_connector(self, connector):
        self.connectorList.append(connector)


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime
