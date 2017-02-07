#!/usr/bin/env python
import sys
import cwiid
import logging
import time
# import drivetrain
from wiimote import Wiimote, WiimoteException
import RPi.GPIO as GPIO

import core


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class launcher:
    def __init__(self):

        # Initialise wiimote, will be created at beginning of loop.
        self.wiimote = None
        # Instantiate CORE / Chassis module and store in the launcher.
        self.core = core.Core()

        GPIO.setwarnings(False)
        self.GPIO = GPIO

        # Shutting down status
        self.shutting_down = False

    def run(self):
        """ Main Running loop controling bot mode and menu state """
        self.wiimote = None
        try:
            self.wiimote = Wiimote()

        except WiimoteException:
            logging.error("Could not connect to wiimote. please try again")

        # Constantly check wiimote for button presses
        while self.wiimote:
            buttons_state = self.wiimote.get_buttons()
            classic_buttons_state = self.wiimote.get_classic_buttons()

            # try:
            #    nunchuk_buttons_state = self.wiimote.get_nunchuk_buttons()
            #    if (nunchuk_buttons_state & cwiid.NUNCHUK_BTN_Z):
            #        print("BUTTON_Z")
            # except:
            #    print("Failed to get Nunchuck")

            # Show joystick state
            # try:
            #     joystick_state = self.wiimote.get_joystick_state()
            #     if joystick_state:
            #         print("joystick_state: {0}".format(joystick_state))
            # except:
            #     print("Failed to get Joystick")

            # try:
            #     l_joystick_state = \
            #         self.wiimote.get_classic_joystick_state(True)
            #     r_joystick_state = \
            #         self.wiimote.get_classic_joystick_state(False)
            #     if l_joystick_state:
            #         print("l_joystick_state: {0}".format(l_joystick_state))
            #     if r_joystick_state:
            #         print("r_joystick_state: {0}".format(r_joystick_state))
            # except:
            #     print("Failed to get Joystick")

            if buttons_state is not None:
                if (buttons_state & cwiid.BTN_A):
                    print("BUTTON_A")
                    if self.motors:
                        self.motors.send_command_motors("1\n")
                if (buttons_state & cwiid.BTN_B):
                    print("BUTTON_B")
                if (buttons_state & cwiid.BTN_UP):
                    print("BUTTON_UP")
                if (buttons_state & cwiid.BTN_DOWN):
                    print("BUTTON_DOWN")
                if (buttons_state & cwiid.BTN_LEFT):
                    print("BUTTON_LEFT")
                if (buttons_state & cwiid.BTN_RIGHT):
                    print("BUTTON_RIGHT")

            if classic_buttons_state is not None:
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_UP):
                #     print("KEY_UP")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_DOWN):
                #     print("KEY_DOWN")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_LEFT):
                #     print("KEY_LEFT")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_RIGHT):
                #     print("KEY_RIGHT")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_A):
                #     print("KEY_A")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_B):
                #     print("KEY_B")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_X):
                #     print("KEY_X")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_Y):
                #     print("KEY_Y")

                if (classic_buttons_state & cwiid.CLASSIC_BTN_ZL or
                        classic_buttons_state & cwiid.CLASSIC_BTN_ZR):
                    # One of the Z buttons pressed, disable
                    # motors and set neutral.
                    self.core.enable_motors(False)
                else:
                    # Neither Z buttons pressed, allow motors to move freely.
                    self.core.enable_motors(True)

                # if (classic_buttons_state & cwiid.CLASSIC_BTN_L):
                #     print("KEY_L")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_R):
                #     print("KEY_R")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_PLUS):
                #     print("KEY_PLUS")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_MINUS):
                #     print("KEY_MINUS")
                # if (classic_buttons_state & cwiid.CLASSIC_BTN_HOME):
                #     print("KEY_HOME")

            time.sleep(0.05)


if __name__ == "__main__":
    launcher = launcher()
    try:
        launcher.run()
    except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        print("Stopping")
