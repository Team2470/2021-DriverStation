import pygame
import log
import structlog

# Setup logging
log.setup()
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

    # @staticmethod
    # def fix_hat(hat):
    #     x, y = hat
    #     if x = 0

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