import logging
import time
import RPi.GPIO as GPIO
from myhub.helper_functions import get_timestamp

from myhub.my_message import IOMessage

DATA_PIN = 25


class IoPiContactReader(object):

    def __init__(self):
        self.logger = logging.getLogger()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read_contact(self, contact_period=60, contact_wait=0.5):
        try:
            # read data in 60 second, return the sum
            _count = contact_period/contact_wait
            _sum = 0
            self.logger.debug('Reading...(%s)' % contact_period)
            while _count > 0:
                _state = GPIO.input(DATA_PIN)
                if _state == 1:
                    _sum += 1
                elif _state == 0:
                    pass
                else:
                    self.logger.warning('Failed to read contact data %s' % _state)
                    return None

                # Decrease counter
                _count -= 1
                time.sleep(contact_wait)
            # return _sum
            return IOMessage(type=IOMessage.CONTACT_MESSAGE, payload='%s' % _sum, ts=get_timestamp())
        except Exception as e:
            self.logger.warning(repr(e))
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    logging.debug("Hello")

    ioReader = IoPiContactReader()

    while 1:
        try:
            sensorData = ioReader.read_contact()
            if sensorData is not None:
                print("publish %s" % sensorData)
            time.sleep(10)

        except Exception as e:
            print("Exception: %s" % e)
            time.sleep(10)
