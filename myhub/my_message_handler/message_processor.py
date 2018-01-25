import logging


class MessageProcessor(object):
    messageCode = "ALL_MSG"

    def __init__(self):
        self.logger = logging.getLogger()
        self.handler = []

    def process(self, message):
        for _handler in self.handler:
            if _handler.process(message) is not None:
                break
        return None

    def add_handler(self, handler):
        self.handler.append(handler)


if __name__ == "__main__":
    import time
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime
