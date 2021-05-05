import math
import numpy as np
from suitcase.structure import Structure
from suitcase.fields import BaseField
from suitcase.fields import Magic
from suitcase.fields import CRCField

PACKET_START_CHAR = b'\x24'
PROTOCOL_FLOAT_LENGTH = 7
PROTOCOL_UINT16_LENGTH = 2
PROTOCOL_UINT8_LENGTH = 1

MSGID_DS_CONTROL = b'\x70'
DS_CONTROL_LENGTH  = 11


def valid_message(data):
    if type(data) != str:
        return False
    if len(data) < 2:
        return False
    if data[0] != PACKET_START_CHAR:
        return False
    if data[1] is MSGID_DS_CONTROL:
        return len(data) == DS_CONTROL_LENGTH

    return False


def checksum(data):
    ret = 0
    for char in data:
        ret += char
    return (ret % 256)

class ProtocolUInt16(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT16_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(np.uint16(self._value))
        else:
            stream.write(np.uint16(0))

    def unpack(self, data):
        # Expecting a hexadecimal string
        self._value = np.uint16(int(data, 16))


class ProtocolSInt16(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT16_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(np.uint16(self._value))
        else:
            stream.write(np.uint16(0))

    def unpack(self, data):
        # Expecting a hexadecimal string
        self._value = np.int16(int(data, 16))


class ProtocolUInt8(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT8_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(np.uint8(self._value))
        else:
            stream.write(np.uint8(0))

    def unpack(self, data):
        self._value = np.int8(int(data, 8))  # TODO is this right?


class ProtocolSInt8(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT8_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(np.int8(self._value))
        else:
            stream.write(np.int8(0))

    def unpack(self, data):
        self._value = np.int8(int(data, 8)) # TODO is this right?

class ControlPacket(Structure):
    start = Magic(PACKET_START_CHAR)
    type = Magic(MSGID_DS_CONTROL)

    # Bits 0>4 = Mode
    # Bit 5 = enabled
    # Bit 6 = estopped
    controlByte = ProtocolUInt8()

    buttonWord = ProtocolUInt16()
    axis0 = ProtocolUInt8()
    axis1 = ProtocolUInt8()
    axis2 = ProtocolUInt8()
    axis3 = ProtocolUInt8()
    axis4 = ProtocolUInt8()
    axis5 = ProtocolUInt8()

    checksum = CRCField(ProtocolUInt8(), checksum, 0, -1)