#! /usr/bin/env python3

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

# Setup logging
log.setup()
logger = structlog.get_logger()

# Serial Communication Thread
#   - Open Serial Port/Keep Trying to open serial port
#   - Read in serial packets, and send events
#   - Write Serial Packets

# Joystick Thread
#   - Keep Track of joysticks coming/going
#   - Poll Joysticks

# Load config
config = {}
with open("config.yaml", 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Communication backend
communication_backend = None
communication_backend_name = config["communication_backend"]
if communication_backend_name == "serial":
    communication_backend = SerialBackend(config["serial"])
elif communication_backend_name == "bluetooth":
    communication_backend = BluetoothBackend(config["bluetooth"])
else:
    logger.fatal("Unsupported backend", communication_backend=communication_backend_name)

# Setup the joystick manager
joystick_manager = JoystickManager(config["joystick_mapping"])

# Main Loop
def run():
    logger.info("Starting...")
    running = True

    def comm_read_loop():
        while running:
            communication_backend.read()

    def main_loop():
        logger.info("Starting main loop...")
        while running:
            joystick_manager.loop()

            # Control packet
            # TODO

            # Right now just the first joystick, figure out how to properly handle joysticks later...
            if 1 in joystick_manager.joysticks:
                joystick = joystick_manager.joysticks[1]

                # Build up the joystick 1 packet
                pkt = protocol.Joystick1Packet()
                length = joystick.axis
                if len(length) <= 1:
                    pkt.axis0 = joystick.axis[0]
                if len(length) <= 2:
                    pkt.axis1 = joystick.axis[1]
                if len(length) <= 3:
                    pkt.axis2 = joystick.axis[2]
                if len(length) <= 4:
                    pkt.axis3 = joystick.axis[3]
                if len(length) <= 5:
                    pkt.axis4 = joystick.axis[4]
                if len(length) <= 6:
                    pkt.axis5 = joystick.axis[5]
                pkt.buttonWord = joystick.button_word()

                p = pkt.pack()
                #logger.info("Joystick1 packet", p=p)
                communication_backend.write(p)

            # Right now just the first joystick, figure out how to properly handle joysticks later...
            if 2 in joystick_manager.joysticks:
                joystick = joystick_manager.joysticks[2]

                # Build up the joystick 1 packet
                pkt = protocol.Joystick2Packet()
                length = joystick.axis
                if len(length) <= 1:
                    pkt.axis0 = joystick.axis[0]
                if len(length) <= 2:
                    pkt.axis1 = joystick.axis[1]
                if len(length) <= 3:
                    pkt.axis2 = joystick.axis[2]
                if len(length) <= 4:
                    pkt.axis3 = joystick.axis[3]
                if len(length) <= 5:
                    pkt.axis4 = joystick.axis[4]
                if len(length) <= 6:
                    pkt.axis5 = joystick.axis[5]
                pkt.buttonWord = joystick.button_word()

                p = pkt.pack()
                #logger.info("Joystick2 packet", p=p)
                communication_backend.write(p)

            time.sleep(0.02)

    # Try to see if the serial port is open...
    try:
        communication_backend.init()
    except PortNotOpenError as e:
        logger.fatal("Unable to open serial port:" + str(e))
        sys.exit(1)


    # Start threads...
    comm_read_thread = threading.Thread(target=comm_read_loop)
    comm_read_thread.start()

    try:
        main_loop() # Needs to be ran in the main loop
    except KeyboardInterrupt:
        running = False
        comm_read_thread.join()

    logger.info("Stopping...")

# Run!
run()
