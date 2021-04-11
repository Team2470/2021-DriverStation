from communication.interface import CommunicationBackend, CommunicationState
from serial import Serial

import log
import structlog

# Setup logging
# log.setup()
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

        # Stats
        self._sent_bytes = 0
        self._received_bytes = 0
        self._running = False

    def connect(self):
        logger.info("Trying to open serial port", port=self.port.port)
        self._sent_bytes = 0
        self._received_bytes = 0
        self.port.open()

        self._running = True

    def disconnect(self):
        logger.info("Trying to close serial port", port=self.port.port)
        self.port.close()

    def is_running(self) -> bool:
        return self._running

    def get_comm_state(self) -> CommunicationState:
        if self.port.is_open:
            return CommunicationState.CONNECTED
        return CommunicationState.DISCONNECTED

    def read(self):
        data = self.port.readline()
        self._received_bytes += len(data)
        if len(data) == 0:
            logger.warn("Empty response")
            return

        # TODO this data needs to get piped somewhere better, so the logout is not
        # horrible
        logger.info("Arduino:", data=data)

    def write(self, data: bytes):
        self.port.write(data)
        self._sent_bytes += len(data)

    def sent_bytes(self) -> int:
        return self._sent_bytes

    def rec_bytes(self) -> int:
        return self._received_bytes