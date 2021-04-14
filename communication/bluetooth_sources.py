
import asyncio
from bleak import BleakScanner, BleakClient, BleakError


def avaiable_devices():
    result = []

    async def run():
        devices = await BleakScanner.discover()
        for d in devices:
            result.append(d)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

    return result