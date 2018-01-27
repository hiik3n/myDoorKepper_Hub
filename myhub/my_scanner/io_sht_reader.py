import logging
import time
import RPi.GPIO as GPIO
from pi_sht1x import SHT1x

from myhub.my_message import IOMessage

DATA_PIN = 18
SCK_PIN = 23


class IoPiShtReader(object):

    def __init__(self):
        self.logger = logging.getLogger()
        self.reader = SHT1x(DATA_PIN, SCK_PIN, gpio_mode=GPIO.BCM)

    def read_sht1x(self):
        try:
            temp = self.reader.read_temperature()
            humidity = self.reader.read_humidity(temp)

            if (temp is not None) and (humidity is not None):
                return IOMessage(type=IOMessage.SHT_MESSAGE, payload='%s,%s' % (temp, humidity))
            else:
                self.logger.warning('Failed to read sht data %s %s' % (temp, humidity))
                return None
        except Exception as e:
            self.logger.warning(repr(e))
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    logging.debug("Hello")

    bcScanner = IoPiShtReader()

    while 1:
        try:
            sensorData = IoPiShtReader.read_sht1x()
            if sensorData is not None:
                print("publish %s,%s" % sensorData)
            time.sleep(10)

        except Exception as e:
            print("Exception: %s" % e)
            time.sleep(10)
