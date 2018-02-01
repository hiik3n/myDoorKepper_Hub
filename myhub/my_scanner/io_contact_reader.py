import logging
import time
import RPi.GPIO as GPIO
from myhub.helper_functions import get_timestamp

from myhub.my_message import IOMessage

DATA_PIN = 25
OPEN_STATE = 0
CLOSE_STATE = 1


class IoPiContactReader(object):

    def __init__(self):
        self.logger = logging.getLogger()
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(DATA_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read_contact(self, period=0.5, wait=2, timeout=60):
        try:
            _curState = None
            _counter = 0
            _counterTimeOut = 0
            while 1:
                _newState = GPIO.input(DATA_PIN)
                # self.logger.debug('READ contact %s' % _newState)
                if (_newState == CLOSE_STATE) or (_newState == OPEN_STATE):
                    # Initialize
                    if _curState is None:
                        _curState = _newState

                    _counterTimeOut += 1
                    if _curState == _newState:
                        if _counterTimeOut > (timeout/period):
                            return IOMessage(type=IOMessage.CONTACT_MESSAGE,
                                             payload='%s' % (1 - _newState), ts=get_timestamp())
                        else:
                            _counter = 0
                            time.sleep(period)
                            continue
                    else:
                        if _counter > (wait/period):
                            return IOMessage(type=IOMessage.CONTACT_MESSAGE,
                                             payload='%s' % (1 - _newState), ts=get_timestamp())
                        else:
                            _counter += 1
                            time.sleep(period)
                            continue
                else:
                    self.logger.warning('Failed to read contact data %s' % _newState)
                    return None
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
