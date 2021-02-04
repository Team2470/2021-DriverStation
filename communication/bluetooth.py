from communication.interface import CommunicationBackend

import log
import structlog
import asyncio
from bleak import BleakScanner, BleakClient, BleakError
import threading

# Setup logging
log.setup()
logger = structlog.get_logger()

# UUIDs for the Elagoo Bluetooth module
UUID_TX = "0000ffe2-0000-1000-8000-00805f9b34fb"
UUID_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"

# macOS uses a UUID thing instead of a the modules mac address
address = "74B1AEEB-6720-4DCB-94BC-623775EA3529"

class BluetoothBackend(CommunicationBackend):
    # Serial port communication backend
    # TODO Add support for serial ports that come and go...

    def __init__(self, config):
        logger.info("Using Bluetooth communication backend", config=config)
        self.loop = asyncio.get_event_loop()
        self.comm_thread = threading.Thread(target=self.run)

    def init(self):
        logger.info("Starting comm thread")
        self.comm_thread.start()

    def run(self):
        self.loop.run_until_complete(self.discover_and_wait())
        self.loop.run_until_complete(self.comm_loop())

    # Discover available devices, and wait for our module
    async def discover_and_wait(self):
        device_found = False
        while not device_found:
            print("Scanning for device...")
            devices = await BleakScanner.discover()
            for d in devices:
                print("Address:", d.address, "Name:", d.name)
                if d.address == address:
                    print("Device found!")
                    device_found = True
                    break

    async def comm_loop(self):
        # TODO need to handling the modules coming and going

        disconnected_event = asyncio.Event()

        def disconnected_callback(client):
            print("Disconnected callback called!")
            disconnected_event.set()

        async with BleakClient(address, loop=self.loop, disconnected_callback=disconnected_callback) as client:
            print("Connected")

            # print("Starting notify callback")
            # await client.start_notify(UUID_NORDIC_RX, uart_data_received)

            while True: # TODO do not send data if we disconnected
                print("Sending command")
                # await client.write_gatt_char(UUID_NORDIC_TX, bytearray("!c200046\r\n", encoding='utf8'), False)
                await client.write_gatt_char(UUID_TX, bytearray("!j00000000000000008B\r\n", encoding='utf8'),
                                             False)
                await asyncio.sleep(0.02) # Send at a rate of 50Hz

            print("Sleeping until device disconnects...")
            await disconnected_event.wait()
            print("Connected: {0}".format(await client.is_connected()))

            print("Ending...")
            # await client.stop_notify(UUID_NORDIC_RX)

            await asyncio.sleep(
                0.5
            )  # Sleep a bit longer to allow _cleanup to remove all BlueZ notifications nicely...

    def read(self):
        # TODO
        pass

    async def write(self, data: bytes):
        logger.info("Writing Data", data = data)
        # await self.client.write_gatt_char(UUID_TX, bytearray("!j00000000000000008B\r\n", encoding='utf8'), False)

    # async def uart_data_received(sender, data):
    #     # TODO needs to be plumbed in
    #     logger.debug("RX", data=data)
    #     # TODO Pipe this output to somewhere

    def disconnected_callback(self):
        print("Disconnected callback called!")
        # TODO Figure this out
        # disconnected_event.set()


