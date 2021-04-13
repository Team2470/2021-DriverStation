
import os
import serial

# The following block is from: https://github.com/pyserial/pyserial/blob/master/serial/tools/list_ports.py#L28-L36
# chose an implementation, depending on os
from typing import List

if os.name == 'nt':  # sys.platform == 'win32':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))


def available_ports() -> List[str]:
    iterator = sorted(comports(include_links=False))

    ports = []
    for n, (port, _, _) in enumerate(iterator, 1):
        ports.append(port)

    return ports