from communication.interface import CommunicationBackend

import log
import structlog

# Setup logging
log.setup()
logger = structlog.get_logger()

class BluetoothBackend(CommunicationBackend):
    # Serial port communication backend
    # TODO Add support for serial ports that come and go...

    def __init__(self, config):
        logger.info("Using Bluetooth communication backend", config=config)
        # TODO

    def connect(self):
        logger.info("Trying to setup bluetooth", port=self.port.port)
        # TODO

    def read(self):
        # TODO
        pass

    def write(self, data: bytes):
        # TODO
        pass
