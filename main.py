import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'myhub'))
import time
import logging
from config import *
from myhub.my_connector import MqttConnector
from myhub.my_queue import MyQueue
from myhub.my_message_handler import MessageProcessor, IOMessageHandler, MqttMessageHandler, BleMessageHandler

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
        # Message handler for IO Message
        ioMsgHandler = IOMessageHandler()
        msgProcessor.add_handler(ioMsgHandler)
        # Message handler for MQTT Message
        mqttMsgHandler = MqttMessageHandler()
        msgProcessor.add_handler(mqttMsgHandler)
        # Message handler for BLE Message
        bleMsgHandler = BleMessageHandler()
        msgProcessor.add_handler(bleMsgHandler)

        while 1:
            logging.debug("Hi")

            # Handle received messages
            while not receiveQueue.is_empty():
                msgProcessor.process(receiveQueue.get())

            # Handle sent messages
            while not sendQueue.is_empty():
                msgProcessor.process(sendQueue.get())

            time.sleep(30)

    except Exception as e:
        logging.error("Exception %s" % repr(e))
