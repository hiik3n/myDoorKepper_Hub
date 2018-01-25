import queue
import logging


class MyQueue(object):

    def __init__(self, maxsize=500):
        self.logger = logging.getLogger()
        self.queue = queue.Queue(maxsize=maxsize)

    def put(self, message):
        if not self.queue.full():
            self.queue.put(message)
            return True
        else:
            self.logger.warning("The queue is full, can not put anything")
            return False

    def get(self):
        if self.queue.empty():
            self.logger.warning("The queue is empty, can not get anything")
            return None
        else:
            return self.queue.get()

    def is_empty(self):
        return self.queue.empty()

    def get_qsize(self):
        return self.queue.qsize()