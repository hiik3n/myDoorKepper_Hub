import logging
import time
import RPi.GPIO as GPIO
from myhub.helper_functions import get_timestamp

from myhub.my_message import IOMessage

DATA_PIN = 24


class IoPiPirReader(object):

    def __init__(self):
        self.logger = logging.getLogger()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read_pir(self, pir_period=60, pir_wait=0.2):
        try:
            # read data in 60 second, return the sum
            _count = pir_period/pir_wait
            _sum = 0
            self.logger.debug('Reading...(%s)' % pir_period)
            while _count > 0:
                _pirState = GPIO.input(DATA_PIN)
                # self.logger.debug('Read PIR %s' % _pirState)
                if _pirState == 1:
                    _sum += 1
                elif _pirState == 0:
                    pass
                else:
                    self.logger.warning('Failed to read pir data %s' % _pirState)
                    return None

                # Decrease counter
                _count -= 1
                time.sleep(pir_wait)
            # return _sum
            return IOMessage(type=IOMessage.PIR_MESSAGE, payload='%s' % _sum, ts=get_timestamp())
        except Exception as e:
            self.logger.warning(repr(e))
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    logging.debug("Hello")

    ioReader = IoPiPirReader()

    while 1:
        try:
            sensorData = ioReader.read_pir()
            if sensorData is not None:
                print("publish %s" % sensorData)
            time.sleep(10)

        except Exception as e:
            print("Exception: %s" % e)
            time.sleep(10)
