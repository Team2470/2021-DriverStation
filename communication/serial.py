from communication.interface import CommunicationBackend
from serial import Serial

import log
import structlog

# Setup logging
log.setup()
logger = structlog.get_logger()


class SerialBackend(CommunicationBackend):
    # Serial port communication backend
    # TODO Add support for serial ports that come and go...

    def __init__(self, config):
        logger.info("Using Serial communication backend", config=config)

        # Open Serial port
        self.port = Serial()
        self.port.port = config["port"]
        self.port.baudrate = config["baudrate"]
        self.port.timeout = config["timeout"]

    def init(self):
        logger.info("Trying to open serial port", port=self.port.port)
        self.port.open()

    def read(self):
        data = self.port.readline()
        if len(data) == 0:
            logger.warn("Empty response")
            return

        # TODO this data needs to get piped somehwere better, so the logout is not
        # horrible
        logger.info("Arduino:", data=data)

    def write(self, data: bytes):
        self.port.write(data)