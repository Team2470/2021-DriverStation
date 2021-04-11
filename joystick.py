import pygame
import log
import structlog
import protocol

# Setup logging
logger = structlog.get_logger()


class JoystickState:
    def __init__(self, axis, buttons, hats):
        self.axis = axis
        self.buttons = buttons
        self.hats = hats

    @staticmethod
    def new(stick):
        axis = []
        for i in range(0, stick.get_numaxes()):
            axis.append(stick.get_axis(i))
        axis = list(map(JoystickState.fix_axis, axis))

        buttons = []
        for i in range(0, stick.get_numbuttons()):
            buttons.append(stick.get_button(i))
        buttons = list(map(lambda x: bool(x), buttons))

        hats = []
        for i in range(0, stick.get_numhats()):
            hats.append(stick.get_hat(i))
        hats = list(map(lambda x: bool(x), hats))

        return JoystickState(axis, buttons, hats)

    @staticmethod
    def fix_axis(x):
        ret = 0
        if x > 0:
            ret = int(x * 128)
        else:
            ret = int(x * 127)
        if 128 < ret:
            ret = 128
        elif ret < -127:
            ret = -127
        return -ret

    def button_word(self):
        word = 0
        for buttonNum, pressed in enumerate(self.buttons):
            word |= int(pressed) << buttonNum
        return word
    # @staticmethod
    # def fix_hat(hat):
    #     x, y = hat
    #     if x = 0

    def get_joystick_1_pkt(self):
        # Build up the joystick 1 packet
        pkt = protocol.Joystick1Packet()
        length = self.axis
        if len(length) <= 1:
            pkt.axis0 = self.axis[0]
        if len(length) <= 2:
            pkt.axis1 = self.axis[1]
        if len(length) <= 3:
            pkt.axis2 = self.axis[2]
        if len(length) <= 4:
            pkt.axis3 = self.axis[3]
        if len(length) <= 5:
            pkt.axis4 = self.axis[4]
        if len(length) <= 6:
            pkt.axis5 = self.axis[5]
        pkt.buttonWord = self.button_word()

    def get_joystick_2_pkt(self):
        # Build up the joystick 1 packet
        pkt = protocol.Joystick2Packet()
        length = self.axis
        if len(length) <= 1:
            pkt.axis0 = self.axis[0]
        if len(length) <= 2:
            pkt.axis1 = self.axis[1]
        if len(length) <= 3:
            pkt.axis2 = self.axis[2]
        if len(length) <= 4:
            pkt.axis3 = self.axis[3]
        if len(length) <= 5:
            pkt.axis4 = self.axis[4]
        if len(length) <= 6:
            pkt.axis5 = self.axis[5]
        pkt.buttonWord = self.button_word()

class JoystickManager:
    def __init__(self, joystick_mapping):
        self.__joysticks = {}
        self.__joystick_mapping = joystick_mapping
        self.joysticks = {}

        # Intiailize pygame
        pygame.display.init()
        pygame.joystick.init()

    def loop(self):
        pygame.event.pump()

        # Get list of current joysticks
        joysticks = {}
        for joystick in [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]:
            joysticks[joystick.get_guid()] = joystick

        # Detect joysticks lost
        for uuid in self.__joysticks:
            if not uuid in joysticks:
                logger.warn("Lost joystick", uuid=self.__joysticks[uuid].get_guid(), name=self.__joysticks[uuid].get_name())

        # Detect new joysticks
        for uuid in joysticks:
            if not uuid in self.__joysticks:
                logger.warn("New joystick", uuid=joysticks[uuid].get_guid(), name=joysticks[uuid].get_name())

        self.__joysticks = joysticks

        # Build up joystick states
        self.joysticks = {}
        for uuid in self.__joysticks:
            # Lookup the "DriverStation Number". Like how the FRC driverstation
            # has 0-5. This allows us to persist the joystick to Driverstation Number
            # accross runs.
            if uuid in self.__joystick_mapping:
                ds_num = self.__joystick_mapping[uuid]
                self.joysticks[ds_num] = JoystickState.new(self.__joysticks[uuid])
            else:
                # TODO Add support for assigning the next available ds num.
                pass