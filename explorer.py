# https://github.com/hbldh/bleak/blob/364f76a34f06ccd03eb8119f774fc3d3fdfa8ddf/examples/service_explorer.py
"""
Service Explorer
----------------
An example showing how to access and print out the services, characteristics and
descriptors of a connected GATT server.
Created on 2019-03-25 by hbldh <henrik.blidh@nedomkull.com>
"""
import platform
import asyncio
import logging

from bleak import BleakClient


async def run(address, debug=False):
    log = logging.getLogger(__name__)
    if debug:
        import sys

        log.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        log.addHandler(h)

    async with BleakClient(address) as client:
        x = await client.is_connected()
        log.info("Connected: {0}".format(x))

        for service in client.services:
            log.info("[Service] {0}: {1}".format(service.uuid, service.description))
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                    except Exception as e:
                        value = str(e).encode()
                else:
                    value = None
                log.info(
                    "\t[Characteristic] {0}: (Handle: {1}) ({2}) | Name: {3}, Value: {4} ".format(
                        char.uuid,
                        char.handle,
                        ",".join(char.properties),
                        char.description,
                        value,
                    )
                )
                for descriptor in char.descriptors:
                    value = await client.read_gatt_descriptor(descriptor.handle)
                    log.info(
                        "\t\t[Descriptor] {0}: (Handle: {1}) | Value: {2} ".format(
                            descriptor.uuid, descriptor.handle, bytes(value)
                        )
                    )


if __name__ == "__main__":
    address = "74B1AEEB-6720-4DCB-94BC-623775EA3529"
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(run(address, True))


# Output from my (Ryan) module:
# Connected: True
# [Service] 0000ffe0-0000-1000-8000-00805f9b34fb: Vendor specific
# 	[Characteristic] 0000ffe1-0000-1000-8000-00805f9b34fb: (Handle: 2) (notify) | Name: Vendor specific, Value: None
# 		[Descriptor] 00002902-0000-1000-8000-00805f9b34fb: (Handle: 4) | Value: b'\x01\x00'
# 	[Characteristic] 0000ffe2-0000-1000-8000-00805f9b34fb: (Handle: 5) (write-without-response) | Name: Vendor specific, Value: None
#
