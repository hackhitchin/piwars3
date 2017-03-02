import core
import time
import cwiid


class calibration:
    def __init__(self, core_module, wm):
        """Class Constructor"""
        self.killed = False
        self.core_module = core_module
        self.wiimote = wm
        self.ticks = 0

        # Define mode enums
        self.mode_none = 0
        self.mode_left = 1
        self.mode_right = 2

        # Default current mode to NONE
        self.mode = self.mode_none

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """

        # Loop indefinitely, or until this thread is flagged as stopped.
        while self.wiimote and not self.killed:
            # While in RC mode, get joystick states and pass speeds to motors.

            buttons_state = self.wiimote.get_buttons()
            classic_buttons_state = self.wiimote.get_classic_buttons()
            if buttons_state is not None:
                if (buttons_state & cwiid.BTN_A):
                    print("BUTTON_A")
                if (buttons_state & cwiid.BTN_B):
                    print("BUTTON_B")

                if (buttons_state & cwiid.BTN_1):
                    print("BUTTON_1")
                if (buttons_state & cwiid.BTN_2):
                    print("BUTTON_2")

                if (buttons_state & cwiid.BTN_PLUS):
                    print("BUTTON_PLUS")
                if (buttons_state & cwiid.BTN_MINUS):
                    print("BUTTON_MINUS")

                if (buttons_state & cwiid.BTN_HOME):
                    print("BUTTON_HOME")

                if (classic_buttons_state & cwiid.BTN_UP):
                    print("BUTTON_UP")
                if (classic_buttons_state & cwiid.BTN_DOWN):
                    print("BUTTON_DOWN")
                if (classic_buttons_state & cwiid.BTN_LEFT):
                    print("BUTTON_LEFT")
                if (classic_buttons_state & cwiid.BTN_RIGHT):
                    print("BUTTON_RIGHT")

            if classic_buttons_state is not None:
                if (classic_buttons_state & cwiid.CLASSIC_BTN_UP):
                    print("KEY_UP")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_DOWN):
                    print("KEY_DOWN")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_LEFT):
                    print("KEY_LEFT")
                    self.mode = self.mode_left
                if (classic_buttons_state & cwiid.CLASSIC_BTN_RIGHT):
                    print("KEY_RIGHT")
                    self.mode = self.mode_right

                if (classic_buttons_state & cwiid.CLASSIC_BTN_A):
                    print("KEY_A")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_B):
                    print("KEY_B")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_X):
                    print("KEY_X")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_Y):
                    print("KEY_Y")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_L):
                    print("KEY_L")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_R):
                    print("KEY_R")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_PLUS):
                    print("KEY_PLUS")
                if (classic_buttons_state & cwiid.CLASSIC_BTN_MINUS):
                    print("KEY_MINUS")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_HOME):
                    print("KEY_HOME")

            # Sleep between loops to allow other stuff to
            # happen and not over burden Pi and Arduino.
            time.sleep(0.05)


if __name__ == "__main__":
    core = core.Core()
    calibration = calibration(core)
    try:
        calibration.run_auto()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        calibration.stop()
        core.set_neutral()
        print("Quitting")
