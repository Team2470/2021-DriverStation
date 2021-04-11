from communication.interface import CommunicationBackend
from communication.interface import CommunicationState

import log
import structlog
import asyncio
from bleak import BleakScanner, BleakClient, BleakError
from threading import Thread, Lock
from queue import Queue, Empty, Full
import time

# Setup logging
# log.setup()
logger = structlog.get_logger()

# UUIDs for the Elagoo Bluetooth module
UUID_TX = "0000ffe2-0000-1000-8000-00805f9b34fb"
UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"

class BluetoothBackend(CommunicationBackend):
    # Bluetooth port communication backend

    def __init__(self, config):
        logger.info("Using Bluetooth communication backend", config=config)

        self.lock = Lock()
        self.cmd_queue = None
        self.comm_thread = None

        self.bytes_tx = 0
        self.bytes_rx = 0
        self.running = False
        self.comm_state = CommunicationState.DISCONNECTED
        self.mac_address = config["mac_address"]

    def connect(self):
        with self.lock:
            if self.running:
                logger.warn("connect was called on a backend that is currently running")
                return

            # Mark that we are now running
            self.running = True

        self.cmd_queue = Queue(maxsize=50)
        def start():
            while self.running:
                # Continuously connect to the bluetooth module
                with self.lock:
                    self.comm_state = CommunicationState.CONNECTING
                logger.info("Connecting...", mac_address=self.mac_address)

                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.run_comms(loop))
                except BleakError as e:
                    if "was not found" in str(e):
                        logger.warning("Device not found", error=e)
                except Exception as e:
                    logger.warning("Error in comm loop", e=e)
                finally:
                    logger.warn("Communication attempt ended")

            self.comm_state = CommunicationState.DISCONNECTED


        # Start Asysnc communication thread
        self.comm_thread = Thread(target=start)
        self.comm_thread.start()

    def disconnect(self):
        # Set flag to stop communication thread
        self.running = False

    def get_comm_state(self) -> CommunicationState:
        with self.lock:
            return self.comm_state

    def read(self):
        # For now lets not read from the bluetooth module
        pass

    def write(self, data: bytes):
        # Write packet to Bluetooth module, if we are connected
        if self.get_comm_state() != CommunicationState.CONNECTED:
            return

        try:
            self.cmd_queue.put(data, block=False)
        except Full:
            logger.warning("Command queue is full")

    def sent_bytes(self) -> int:
        with self.lock:
            return self.bytes_tx

    def rec_bytes(self) -> int:
        with self.lock:
            return self.bytes_rx

    def uart_data_received(self, sender, data):
        print( "RX> {0}".format(data))

        self.bytes_rx += len(data)
        if len(data) == 0:
            logger.warn("Empty response")
            return

        # TODO this data needs to get piped somewhere better, so the logout is not
        # horrible
        logger.info("Arduino:", data=str(data))

    async def run_comms(self, loop):
        def disconnected_callback(client):
            logger.warn("Bluetooth disconnected callback called!")
            with self.lock:
                # Lost connection, attempting to reconnect
                self.comm_state = CommunicationState.CONNECTING

        async with BleakClient(self.mac_address, loop=loop, disconnected_callback=disconnected_callback) as client:
            with self.lock:
                running = self.running
                self.comm_state = CommunicationState.CONNECTED


            # Start receiver
            await client.start_notify(UUID_RX, self.uart_data_received)

            # Send commands
            while running:
                try:
                    cmd = self.cmd_queue.get(timeout=1) # Block for up to 1 second
                    with self.lock:
                        self.bytes_tx += len(cmd)
                    logger.debug("Received packet", cmd=cmd)

                    await client.write_gatt_char(UUID_TX, cmd, False)
                    await asyncio.sleep(0.01) # TODO remove, this is probably not needed
                except Empty:
                    logger.debug("No command packet is available")

                with self.lock:
                    running = self.running
