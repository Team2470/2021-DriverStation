import math
import numpy as np
from suitcase.structure import Structure
from suitcase.fields import BaseField
from suitcase.fields import Magic
from suitcase.fields import CRCField

PACKET_START_CHAR = "!"
PROTOCOL_FLOAT_LENGTH = 7
PROTOCOL_UINT16_LENGTH = 4
PROTOCOL_UINT8_LENGTH = 2

MSGID_DS_CONTROL = 'c'
DS_CONTROL_LENGTH  = 10

MSGID_DS_JOYSTICK_1 = 'j'
MSGID_DS_JOYSTICK_2  = 'J'
DS_JOYSTICK_LENGTH =                22

MSGID_ROBOT_STATUS = 'S'
ROBOT_STATUS_LENGTH =                 10


def valid_message(data):
    if type(data) != str:
        return False
    if len(data) < 2:
        return False
    if data[0] != PACKET_START_CHAR:
        return False

    if data[1] is MSGID_DS_CONTROL:
        return len(data) == DS_CONTROL_LENGTH
    elif data[1] is MSGID_DS_JOYSTICK_1 or data[1] is MSGID_DS_JOYSTICK_2:
        return len(data) == DS_JOYSTICK_LENGTH
    elif data[1] is MSGID_ROBOT_STATUS:
        return len(data) == ROBOT_STATUS_LENGTH

    return False


def checksum(data):
    ret = 0
    for char in data:
        ret += char
    return ("%02X" % (ret % 256)).encode("utf8")


class ProtocolChecksum(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = 2

    def pack(self, stream):
        if type(self._value) is not bytes:
            raise RuntimeError("Not a bytes")
        stream.write(self._value)

    def unpack(self, data):
        print(data)
        self._value = data


class ProtocolUInt16(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT16_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(("%04X" % np.uint16(self._value)).encode("utf8"))
        else:
            stream.write("0000".encode("utf8"))

    def unpack(self, data):
        # Expecting a hexadecimal string
        self._value = np.uint16(int(data, 16))


class ProtocolSInt16(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT16_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(("%04X" % np.uint16(self._value)).encode("utf8"))
        else:
            stream.write("0000")

    def unpack(self, data):
        # Expecting a hexadecimal string
        self._value = np.int16(int(data, 16))


class ProtocolUInt8(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT8_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write(("%02X" % np.uint8(self._value)).encode("utf8"))
        else:
            stream.write("00".encode("utf8"))

    def unpack(self, data):
        self._value = np.int8(int(data, 16))  # TODO is this right?


class ProtocolSInt8(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_UINT8_LENGTH

    def pack(self, stream):
        if self._value is not None:
            stream.write("%02X" % np.uint8(self._value))
        else:
            stream.write("00")

    def unpack(self, data):
        self._value = np.int8(int(data, 16)) # TODO is this right?


class ProtocolFloat(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self.bytes_required = PROTOCOL_FLOAT_LENGTH

    def pack(self, stream):
        if self._value is not None:
            f = float(self._value)
            f = float(self._value)
            val = ""
            if f < 0:
                val += "-"
            else:
                val += " "

            f = abs(f)
            val += "%03d." % f
            val += "%02d" % int(round((f - math.floor(f)) * 100))
            stream.write(val)
        else:
            stream.write(" 000.00")

    def unpack(self, data):
        self._value = float(data)


class Joystick1Packet(Structure):
    start = Magic(bytearray("!", "utf8"))
    type = Magic(bytearray("j", "utf8"))

    buttonWord = ProtocolUInt16()
    axis0 = ProtocolUInt8()
    axis1 = ProtocolUInt8()
    axis2 = ProtocolUInt8()
    axis3 = ProtocolUInt8()
    axis4 = ProtocolUInt8()
    axis5 = ProtocolUInt8()

    checksum = CRCField(ProtocolChecksum(), checksum, 0, -4)
    termination = Magic(bytearray("\r\n", "utf8"))


if __name__ == "__main__":
    # y = YPRUpdate()
    # y.yaw = -222.11
    # y.pitch = 1
    # y.roll = 2
    # y.compas_heading = 3

    # print y.pack()
    # print float(" 052.00")
    # ypr = YPRUpdate.from_data("!y-000.09 006.18-005.11 147.26DF\r\n")
    # print y.yaw
    # print (make_quaternion_cmd_packet().pack())
    # q = QuaternionUpdate.from_data("!q22C8DF8A2AC8FE90D2DADAB2E5D6FEDD021F004A 023.554C\r\n")
    # print "22C8", int("22C8", 16), np.uint16(int("22C8", 16))
    # print q.temp_c

    s = Joystick1Packet.from_data("!j000000003F000000A4\r\n".encode("utf8"))
    print(s)

    s = Joystick1Packet()
    s.axis0 = -10
    print(s.pack())