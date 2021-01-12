from threading import Thread
from threading import RLock
import pygame
import time
import log

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
    return ret


class JoystickState:
    def __init__(self, axis, buttons):
        self.axis = list(map(fix_axis, axis))
        self.buttons = list(map(lambda x: bool(x), buttons))

def make_state(stick):
    axes = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if stick is not None:
        for i in range(0, stick.get_numaxes()):
            if i == len(axes):
                break
            axes[i] = stick.get_axis(i)
        for i in range(0, stick.get_numbuttons()):
            if i == len(buttons):
                break
            buttons[i] = stick.get_button(i)
    return JoystickState(axes, buttons)

class Joysticks:
    def __init__(self):
        self.__joysticks = []
        self.joysticks = []

    def init(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("No joysticks found")
        else:
            for i in range(0, pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                joy.init()
                self.__joysticks.append(joy)
                self.joysticks = make_state(None)
        self.running = True

    def loop(self):
        pygame.event.pump()
        self.joysticks = []
        for joy in self.__joysticks:
            self.joysticks.append(make_state(joy))
