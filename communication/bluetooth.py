from communication.interface import CommunicationBackend

import log
import structlog
import asyncio
from bleak import BleakScanner, BleakClient, BleakError
from threading import Thread, Lock
from queue import Queue, Empty, Full

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
        self.connected = False
        self.mac_address = config["mac_address"]

    def connect(self):
        self.cmd_queue = Queue(maxsize=50)
        def start():
            with self.lock:
                self.running = True
                self.connected = False

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_comms(loop))
            except Exception as e:
                logger.warning("Error in comm loop", e=e)
            finally:
                with self.lock:
                    print("Updating")
                    self.running = False
                    self.connected = False

        # Start Asysnc communication thread
        self.comm_thread = Thread(target=start)
        self.comm_thread.start()

    def disconnect(self):
        # Set flag to stop communication thread
        self.running = False

    def is_connected(self):
        with self.lock:
            return self.connected

    def read(self):
        # For now lets not read from the bluetooth module
        pass

    def write(self, data: bytes):
        # Write packet to Bluetooth module
        try:
            self.cmd_queue.put(data, block=False)
        except Full:
            logger.warning("Command queue is full")

    def sent_bytes(self):
        with self.lock:
            return self.bytes_tx

    def rec_bytes(self):
        with self.lock:
            return self.bytes_rx

    async def run_comms(self, loop):
        def disconnected_callback(client):
            logger.warn("Bluetooth disconnected callback called!")
            with self.lock:
                # self.connected = False
                # self.running = False
                pass

        self.connected = True
        async with BleakClient(self.mac_address, loop=loop, disconnected_callback=disconnected_callback) as client:
            running = self.running

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
