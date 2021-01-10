#! /usr/bin/env python3

import asyncio
import logging
from bleak import BleakScanner, BleakClient
from datetime import datetime


address = "74B1AEEB-6720-4DCB-94BC-623775EA3529"

# Discover available devices
async def run():
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

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

# Connect to device and read its model number
# 74B1AEEB-6720-4DCB-94BC-623775EA3529: ELEGOO BT16
UUID_NORDIC_TX = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
UUID_NORDIC_RX = "0000ffe1-0000-1000-8000-00805f9b34fb"
command = b"Test\n"

def uart_data_received(sender, data):
    now = datetime.now()

    print(now, "RX> {0}".format(data))


print("Connecting...")
async def run(address, loop):
    disconnected_event = asyncio.Event()

    def disconnected_callback(client):
        print("Disconnected callback called!")
        disconnected_event.set()

    async with BleakClient(address, loop=loop, disconnected_callback=disconnected_callback) as client:
        print("Connected")

        print("Starting notify callback")
        await client.start_notify(UUID_NORDIC_RX, uart_data_received)

        print("Sleeping until device disconnects...")
        await disconnected_event.wait()
        print("Connected: {0}".format(await client.is_connected()))

        print("Ending...")
        # await client.stop_notify(UUID_NORDIC_RX)

        await asyncio.sleep(
            0.5
        )  # Sleep a bit longer to allow _cleanup to remove all BlueZ notifications nicely...

        # print("Read command")
        # while True:
        #   await client.write_gatt_char(UUID_NORDIC_TX, bytearray(c[0:20]), True)
        #   c = c[20:]


loop = asyncio.get_event_loop()
loop.run_until_complete(run(address, loop))
