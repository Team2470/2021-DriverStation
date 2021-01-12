#/usr/bin/env python3

import yaml
from joystick import Joysticks
from serial import Serial
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
#   - Pool Joysticks

# Load config
config = {}
with open("config.yaml", 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Open Serial port
port = Serial()
port.port = config["serial"]["port"]
port.baudrate = config["serial"]["baudrate"]
port.timeout = config["serial"]["timeout"]

# Setup pygame for joysticks
joysticks = Joysticks()
joysticks.init()

# Main Loop
def run():
    logger.info("Starting...")
    running = True



    def comm_read_loop():
        while running:
            data = port.readline()
            if len(data) == 0:
                logger.warn("Empty response")
                continue

            logger.info("Arduino:", data=data)

    def comm_write_loop():
        while running:
            # logger.debug("Write to serial port")
            port.write("!j0000F60000000000A7\r\n".encode("utf8"))
            time.sleep(0.02)

    def main_loop():
        logger.info("Starting main loop...")
        while running:
            joysticks.loop()
            logger.info("Joystick", axis=joysticks.joysticks[0].axis, buttons=joysticks.joysticks[0].buttons)

            # Right now just the first joystick, figure out how to properly handle joysticks later...
            joystick1 = joysticks.joysticks[0]

            # Build up the joystick 1 packet
            joystick1pkt = protocol.Joystick1Packet()
            joystick1pkt.axis0 = joystick1.axis[0]
            joystick1pkt.axis1 = joystick1.axis[1]
            joystick1pkt.axis2 = joystick1.axis[2]
            joystick1pkt.axis3 = joystick1.axis[3]
            joystick1pkt.axis4 = joystick1.axis[4]
            joystick1pkt.axis5 = joystick1.axis[5]
            # TODO lets do buttons later....

            p = joystick1pkt.pack()
            #logger.info("Joystick1 packet", p=p)
            port.write(p)

            time.sleep(0.02)

    # Try to see if the serial port is open...
    try:
        logger.info("Trying to open serial port: " + port.port)
        port.open()
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