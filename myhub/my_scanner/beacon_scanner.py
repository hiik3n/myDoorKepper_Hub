import sys
import os
import logging
import time

from myhub.my_message.ble_payload import BlePayload
from myhub.my_message import BleMessage
from bluepy.btle import Scanner, BTLEException
from myhub.helper_functions import get_timestamp


class BleScanner(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.scanner = Scanner(iface=0)

    def scan(self, period=10):
        return self.scanner.scan(period)

    def scan_beacon(self, mac_address, period=10):
        _pkgList = []
        _devs = self.scan(period)
        for _dev in _devs:
            for _mac in mac_address:
                if _dev.addr == _mac.lower():
                    _bcPkg = BleMessage(mac=_dev.addr,
                                        rssi=_dev.rssi,
                                        payload=BlePayload(payload=_dev.getScanData()),
                                        ts=get_timestamp())
                    self.logger.debug("BLE get %s" % _bcPkg)
                    _pkgList.append(_bcPkg)
        return _pkgList


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    logging.debug("Hello")

    bc1Mac = ["d6:cd:c3:a9:00:85", "fe:8d:8e:65:e9:73"]

    bcScanner = BleScanner()

    while 1:
        try:
            print("get %s from %s" % (bc1Mac, str(bcScanner.scan_beacon(bc1Mac))))
            time.sleep(10)

        except BTLEException as e:
            print("BTLEException: %s" % e)
            time.sleep(10)
