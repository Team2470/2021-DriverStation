#/usr/bin/env python3

import yaml
from joystick import JoystickManager
from communication import SerialBackend, BluetoothBackend
from serial.serialutil import PortNotOpenError
import time
import sys
import threading
import structlog
import log
import protocol


class DriverStation:

    def __init__(self):
        # Setup logging
        log.setup()
        self.logger = structlog.get_logger()
        self.config = {}
        self.communication_backend = None

    def load_settings(self, file_path):
        with open("config.yaml", 'r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        # Communication backend
        communication_backend_name = self.config["communication_backend"]
        if communication_backend_name == "serial":
            self.communication_backend = SerialBackend(self.config["serial"])
        elif communication_backend_name == "bluetooth":
            self.communication_backend = BluetoothBackend(self.config["bluetooth"])
        else:
            self.logger.fatal("Unsupported backend", communication_backend=communication_backend_name)

        # Setup the joystick manager
        joystick_manager = JoystickManager(self.config["joystick_mapping"])

    def get_settings(self):
        return self.config

    def connect(self):
        try:
            self.communication_backend.connect()
        except PortNotOpenError as e:
            self.logger.fatal("Unable to open serial port:" + str(e))

    def disconnect(self):
        # Todo: Shut down the thread
        try:
            self.communication_backend.disconnect()
        except PortNotOpenError as e:
            self.logger.fatal("Unable to close serial port:" + str(e))

    def is_connected(self):
        if self.communication_backend is not None:
            return self.communication_backend.is_connected()
        else:
            return False

    def run(self):
        self.logger.info("Starting...")
        running = True

        def comm_read_loop():
            while running:
                self.communication_backend.read()

        def main_loop():
            self.logger.info("Starting main loop...")
            while running:
                self.joystick_manager.loop()

                # Control packet
                # TODO

                # Right now just the first joystick, figure out how to properly handle joysticks later...
                if 1 in self.joystick_manager.joysticks:
                    joystick = self.joystick_manager.joysticks[1]

                    # Build up the joystick 1 packet
                    pkt = protocol.Joystick1Packet()
                    pkt.axis0 = joystick.axis[0]
                    pkt.axis1 = joystick.axis[1]
                    pkt.axis2 = joystick.axis[2]
                    pkt.axis3 = joystick.axis[3]
                    pkt.axis4 = joystick.axis[4]
                    pkt.axis5 = joystick.axis[5]
                    # TODO lets do buttons later....

                    p = pkt.pack()
                    # logger.info("Joystick1 packet", p=p)
                    self.communication_backend.write(p)

                # Right now just the first joystick, figure out how to properly handle joysticks later...
                if 2 in self.joystick_manager.joysticks:
                    joystick = self.joystick_manager.joysticks[2]

                    # Build up the joystick 1 packet
                    pkt = protocol.Joystick2Packet()
                    pkt.axis0 = joystick.axis[0]
                    pkt.axis1 = joystick.axis[1]
                    pkt.axis2 = joystick.axis[2]
                    pkt.axis3 = joystick.axis[3]
                    pkt.axis4 = joystick.axis[4]
                    pkt.axis5 = joystick.axis[5]
                    # TODO lets do buttons later....

                    p = pkt.pack()
                    # logger.info("Joystick2 packet", p=p)
                    self.communication_backend.write(p)

                time.sleep(0.02)

        # Start threads...
        comm_read_thread = threading.Thread(target=comm_read_loop)
        comm_read_thread.start()

        try:
            main_loop()  # Needs to be ran in the main loop
        except KeyboardInterrupt:
            running = False
            comm_read_thread.join()

        self.logger.info("Stopping...")
