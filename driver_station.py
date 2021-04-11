#! /usr/bin/env python3

import yaml
from joystick import JoystickManager
from communication import SerialBackend, BluetoothBackend, CommunicationState
from serial.serialutil import PortNotOpenError
import time
import threading
import structlog
import log
import protocol
from PySide2.QtCore import QObject, Signal, QThread


class DriverStation(QObject):

    # QT Callbacks
    finished = Signal()
    comms_stats = Signal(str, int, int)

    running = False
    communication_backend = None
    enabled = False

    def __init__(self):
        # Setup logging
        super().__init__()
        self.logger = structlog.get_logger()
        self.config = {}

    def load_settings(self, file_path):
        with open("config.yaml", 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        log.setup(self.config["logging"])

        # Communication backend
        communication_backend_name = self.config["communication_backend"]
        if communication_backend_name == "serial":
            self.communication_backend = SerialBackend(self.config["serial"])
        elif communication_backend_name == "bluetooth":
            self.communication_backend = BluetoothBackend(self.config["bluetooth"])
        else:
            self.logger.fatal("Unsupported backend", communication_backend=communication_backend_name)

        # Setup the joystick manager
        self.joystick_manager = JoystickManager(self.config["joystick_mapping"])

    def get_settings(self):
        return self.config

    def connect_port(self):
        try:
            self.communication_backend.connect()
            return True
        except PortNotOpenError as e:
            self.logger.fatal("Unable to open serial port:" + str(e))
            return False

    def disconnect_port(self):
        # Todo: Shut down the thread
        try:
            self.communication_backend.disconnect()
            return True
        except PortNotOpenError as e:
            self.logger.fatal("Unable to close serial port:" + str(e))
            return False

    def set_enabled(self, enable):
        self.enabled = enable

    def get_comm_state(self) -> CommunicationState:
        return self.communication_backend.get_comm_state()

    def get_comm_state_str(self) -> str:
        state = self.communication_backend.get_comm_state()
        if state == CommunicationState.CONNECTED:
            return "Connected"
        elif state == CommunicationState.CONNECTING:
            return "Connecting"
        elif state == CommunicationState.DISCONNECTED:
            return "Disconnected"
        else:
            return "Unknown"

    def is_enabled(self):
        return self.enabled

    def stop(self):
        self.running = False

    def run(self):
        self.logger.info("Starting...")
        self.running = True

        # Start threads...
        comm_read_thread = threading.Thread(target=self._comm_read_loop)
        comm_read_thread.start()

        try:
            self._main_loop()  # Needs to be ran in the main loop
        except KeyboardInterrupt:
            self.running = False
            comm_read_thread.join()

        self.logger.info("Stopping...")

    def _comm_read_loop(self):
        while self.running:
            self.communication_backend.read()

    def _main_loop(self):
        self.logger.info("Starting main loop...")
        while self.running:
            # Control packet
            pkt = protocol.ControlPacket()

            # For now, just set enabled
            pkt.controlByte = 0
            pkt.controlByte += (1 << 4) if self.enabled else 0x00
            p = pkt.pack()
            #self.logger.info("Control packet", p=p)
            self.logger.debug("Sending control packet", p=p)
            self.communication_backend.write(p)

            # Right now just the first joystick, figure out how to properly handle joysticks later...
            if 1 in self.joystick_manager.joysticks:
                joystick = self.joystick_manager.joysticks[1]

                # Build up the joystick 1 packet
                pkt = protocol.Joystick1Packet()
                length = len(joystick.axis)
                if length >= 1:
                    pkt.axis0 = joystick.axis[0]
                if length >= 2:
                    pkt.axis1 = joystick.axis[1]
                if length >= 3:
                    pkt.axis2 = joystick.axis[2]
                if length >= 4:
                    pkt.axis3 = joystick.axis[3]
                if length >= 5:
                    pkt.axis4 = joystick.axis[4]
                if length >= 6:
                    pkt.axis5 = joystick.axis[5]
                pkt.buttonWord = joystick.button_word()

                p = pkt.pack()
                self.logger.debug("Sending joystick1 packet", p=p)
                self.communication_backend.write(p)

            # Right now just the first joystick, figure out how to properly handle joysticks later...
            if 2 in self.joystick_manager.joysticks:
                joystick = self.joystick_manager.joysticks[2]

                # Build up the joystick 1 packet
                pkt = protocol.Joystick2Packet()
                length = len(joystick.axis)
                if length >= 1:
                    pkt.axis0 = joystick.axis[0]
                if length >= 2:
                    pkt.axis1 = joystick.axis[1]
                if length >= 3:
                    pkt.axis2 = joystick.axis[2]
                if length >= 4:
                    pkt.axis3 = joystick.axis[3]
                if length >= 5:
                    pkt.axis4 = joystick.axis[4]
                if length >= 6:
                    pkt.axis5 = joystick.axis[5]
                pkt.buttonWord = joystick.button_word()

                p = pkt.pack()
                self.logger.debug("Sending joystick2 packet", p=p)
                self.communication_backend.write(p)

            # Update read/write
            comm_state_str = self.get_comm_state_str()
            sent_bytes = self.communication_backend.sent_bytes()
            rec_bytes = self.communication_backend.rec_bytes()

            self.logger.debug("Updating comm stats", comm_state=comm_state_str, sent_bytes=sent_bytes, rec_bytes=rec_bytes)
            self.comms_stats.emit(comm_state_str, sent_bytes, rec_bytes)

            time.sleep(0.05)

        self.logger.warn("Main loop ending")
        self.finished.emit()