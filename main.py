import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'myhub'))
import time
import logging
import threading
import traceback
from config import *
from myhub.my_connector import MqttConnector
from myhub.my_queue import MyQueue
from myhub.my_message_handler import MessageProcessor, MqttMessageHandler


if __name__ == "__main__":

    # Log initialization
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(module)s - %(threadName)s - %(levelname)s - %(message)s')
    logging.Formatter.converter = time.gmtime

    try:

        logging.info("myHub-Main")

        logging.debug("Initial Queues")
        receiveQueue = MyQueue()
        sendQueue = MyQueue()

        logging.debug("Initial mqttConnector")
        mqttCloudConn = MqttConnector(client_id=MQTT_CLIENTID, host=MQTT_HOST, port=MQTT_PORT,
                                      username=MQTT_USERNAME, password=MQTT_PASSWORD,
                                      ca_cert=MQTT_CACERT, tls_version=MQTT_TLSVERSION, crt_file=MQTT_CERT, key_file=MQTT_KEY)
        res = mqttCloudConn.connect()
        logging.debug("Connected to MQTT Broker (code=%s)" % res)

        logging.debug("Initial MsgHandlers")
        # Message processor
        msgProcessor = MessageProcessor()

        # Message handler for MQTT Message
        mqttMsgHandler = MqttMessageHandler()
        msgProcessor.add_handler(mqttMsgHandler)

        if USE_BLE:
            from myhub.my_scanner import BleScanner, BTLEException
            from myhub.my_message_handler import BleMessageHandler

            def ble_scan_worker(scanner, queue):
                """thread worker function"""
                _beaconAddrs = ["d6:cd:c3:a9:00:85", "fe:8d:8e:65:e9:73", "cb:16:04:4a:10:56"]
                while 1:
                    try:
                        _bleMsgs = scanner.scan_beacon(_beaconAddrs)
                        for _msg in _bleMsgs:
                            _msg.sender = _msg.mac
                            _msg.recipient = HUB_ID
                            queue.put(_msg)
                        time.sleep(10)

                    except BTLEException as e:
                        logging.error("BTLEException: %s" % repr(e))
                        time.sleep(10)

            logging.debug("Initial BLE Scanner")
            bleScanner = BleScanner()

            # Message handler for BLE Message
            bleMsgHandler = BleMessageHandler()
            bleMsgHandler.add_connector(mqttCloudConn)
            msgProcessor.add_handler(bleMsgHandler)

            # Start thread to scan ble messages
            bleScanThread = threading.Thread(name='ble_scan_worker', target=ble_scan_worker,
                                             args=(bleScanner, receiveQueue,))
            bleScanThread.setDaemon(True)
            logging.debug("Start thread to scan ble messages")
            bleScanThread.start()

        if USE_IO:
            from myhub.my_message_handler import IOMessageHandler
            from myhub.my_scanner import IoPiShtReader

            IO_PI_SHT_READ_PERIOD_SECOND = 60

            def io_pi_sht_reader(reader, queue):
                while 1:
                    try:
                        _knotId = 'knot01'
                        _sensorData = reader.read_sht1x()
                        if _sensorData is not None:
                            logging.debug("GET %s" % repr(_sensorData))
                            _sensorData.sender = _knotId
                            _sensorData.recipient = HUB_ID
                            queue.put(_sensorData)
                        time.sleep(IO_PI_SHT_READ_PERIOD_SECOND)

                    except Exception as e:
                        logging.warning("Exception: %s" % e)
                        time.sleep(IO_PI_SHT_READ_PERIOD_SECOND)

            logging.debug("Initial IO Pi SHT Reader")
            ioPiShtReader = IoPiShtReader()

            # Message handler for IO Message
            ioMsgHandler = IOMessageHandler()
            ioMsgHandler.add_connector(mqttCloudConn)
            msgProcessor.add_handler(ioMsgHandler)

            # Start thread to read io SHT messages
            ioShtReadThread = threading.Thread(name='io_pi_sht_reader', target=io_pi_sht_reader,
                                               args=(ioPiShtReader, receiveQueue,))
            ioShtReadThread.setDaemon(True)
            logging.debug("Start thread to read io Pi Sht messages")
            ioShtReadThread.start()

        if USE_PIR:
            from myhub.my_message_handler import IOMessageHandler
            from myhub.my_scanner import IoPiPirReader

            def io_pi_pir_reader(reader, queue):
                while 1:
                    try:
                        _knotId = 'knot01'
                        # this line will take normally 60s
                        _sensorData = reader.read_pir()
                        if _sensorData is not None:
                            logging.debug("GET %s" % repr(_sensorData))
                            _sensorData.sender = _knotId
                            _sensorData.recipient = HUB_ID
                            queue.put(_sensorData)

                    except Exception as e:
                        logging.warning("Exception: %s, wait 30s" % e)
                        time.sleep(30)

            logging.debug("Initial IO Pi PIR Reader")
            ioPiPirReader = IoPiPirReader()

            # Message handler for IO Message
            ioPirMsgHandler = IOMessageHandler()
            ioPirMsgHandler.add_connector(mqttCloudConn)
            msgProcessor.add_handler(ioPirMsgHandler)

            # Start thread to read io PIR messages
            ioPirReadThread = threading.Thread(name='io_pi_pir_reader', target=io_pi_pir_reader,
                                               args=(ioPiPirReader, receiveQueue,))
            ioPirReadThread.setDaemon(True)
            logging.debug("Start thread to read io Pi PIR messages")
            ioPirReadThread.start()

        if USE_CONTACT:
            from myhub.my_message_handler import IOMessageHandler
            from myhub.my_scanner import IoPiContactReader

            def io_pi_contact_reader(reader, queue):
                while 1:
                    try:
                        _knotId = 'knot01'
                        _sensorData = reader.read_contact()
                        if _sensorData is not None:
                            logging.debug("GET %s" % repr(_sensorData))
                            _sensorData.sender = _knotId
                            _sensorData.recipient = HUB_ID
                            queue.put(_sensorData)

                    except Exception as e:
                        logging.warning("Exception: %s, wait some seconds" % e)
                        time.sleep(15)

            logging.debug("Initial IO Pi Contact Reader")
            ioPiContactReader = IoPiContactReader()

            # Message handler for IO Message
            ioContactMsgHandler = IOMessageHandler()
            ioContactMsgHandler.add_connector(mqttCloudConn)
            msgProcessor.add_handler(ioContactMsgHandler)

            # Start thread to read io Contact messages
            ioContactReadThread = threading.Thread(name='io_pi_contact_reader', target=io_pi_contact_reader,
                                                   args=(ioPiContactReader, receiveQueue,))
            ioContactReadThread.setDaemon(True)
            logging.debug("Start thread to read io Pi Contact messages")
            ioContactReadThread.start()

        while 1:
            # logging.debug("Hi")

            # Handle received messages
            while not receiveQueue.is_empty():
                msgProcessor.process(receiveQueue.get())

            # Handle sent messages
            while not sendQueue.is_empty():
                msgProcessor.process(sendQueue.get())

            time.sleep(1)

    except Exception as e:
        logging.error("Exception %s" % repr(traceback.print_exc()))
        exit(1)
