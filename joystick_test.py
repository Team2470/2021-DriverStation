import unittest

from joystick import JoystickState

class JoystickTest(unittest.TestCase):
    def test_button_word(self):
        state = JoystickState([], [True, True, True, True, True, True], [])
        self.assertEqual(0b00111111, state.button_word())

        state = JoystickState([], [False, False, False, False, False, False], [])
        self.assertEqual(0b00000000, state.button_word())

        state = JoystickState([], [False, True, False, False, False, False], [])
        self.assertEqual(0b00000010, state.button_word())

        state = JoystickState([], [False, True, False, False, False, True], [])
        self.assertEqual(0b00100010, state.button_word())


if __name__ == '__main__':
    unittest.main()
