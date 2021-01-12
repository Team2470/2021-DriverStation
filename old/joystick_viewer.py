import pygame
from tkinter import *
import threading
import joystick


class JoyEntry(Frame):
    def __init__(self, left, right, master=None):
        Frame.__init__(self, master)
        self.right = Label(self, text=right)
        self.right.pack(side=RIGHT)

        self.left = Label(self, text=left)
        self.left.pack(side=LEFT)

        self.pack()


class JoystickStateFrame(Frame):
    def __init__(self, stick, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.stick = stick
        self.joystick = JoyEntry("Joystick:", stick.get_id(), master=self)
        self.joystick.pack()
        self.axis = Label(self, text=("Axis %s" % stick.get_numaxes()))
        self.axis.pack()

        self.axes = []
        for i in range(0, stick.get_numaxes()):
            entry = JoyEntry(("Axis " + str(i)), str(0), master=self)
            self.axes.append(entry)

        self.buttons = []
        self.button_count = Label(self,text="Buttons %s" % stick.get_numbuttons())
        self.button_count.pack()
        for i in range(0, stick.get_numbuttons()):
            entry = JoyEntry(("Buttons " + str(i)), str(False), master=self)
            self.buttons.append(entry)

    def update(self):
        for i in range(0, self.stick.get_numaxes()):
            value = joystick.fix_axis(self.stick.get_axis(i))
            self.axes[i].right['text'] = "%.2f" % value
        for i in range(0, self.stick.get_numbuttons()):
            value = self.stick.get_button(i)
            self.buttons[i].right['text'] = str(bool(value))


class JoystickViewer(Frame):
    def __init__(self, master):
        Frame.__init__(self, master=None)
        self.pack()
        self.joysticks = []
        if pygame.joystick.get_count() == 0:
            self.no_joysticks = Label(self, text="No Joysticks Connected")
            self.no_joysticks.pack()
        else:
            for i in range(0, pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(i)
                joy.init()
                print("Found joystick ", joy.get_name())
                self.joysticks.append(joy)
        self.joy_states = []
        for joy in self.joysticks:
            state = JoystickStateFrame(joy, master=self)
            state.pack()
            self.joy_states.append(state)

    def update(self):
        while True:
            pygame.event.pump()
            for joy in self.joy_states:
                joy.update()


def update(viewer):
    viewer.update()


if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()

    root = Tk(className="Joystick Viewer")
    root.minsize(400, 400)
    joy = JoystickViewer(master=root)
    update_thread = threading.Thread(target=update, args=(joy,))
    update_thread.start()
    joy.mainloop()
    root.destroy()
    sys.exit(0)