#!/usr/bin/env python
import sys
import cwiid
import logging
import time
import threading
from wiimote import Wiimote, WiimoteException
import RPi.GPIO as GPIO

import core
import rc

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class launcher:
    def __init__(self):

        # Initialise wiimote, will be created at beginning of loop.
        self.wiimote = None
        # Instantiate CORE / Chassis module and store in the launcher.
        self.core = core.Core()

        GPIO.setwarnings(False)
        self.GPIO = GPIO

        self.challenge = None
        self.challenge_thread = None

        # Shutting down status
        self.shutting_down = False

        self.killed = False

    def stop_threads(self):
        """ Single point of call to stop any RC or Challenge Threads """
        if self.challenge:
            self.challenge.stop()
            self.challenge = None
            self.challenge_thread = None
            logging.info("Stopping Challenge Thread")
        else:
            logging.info("No Challenge Thread")
        # Safety setting
        self.core.enable_motors(False)

    def run(self):
        """ Main Running loop controling bot mode and menu state """
        self.wiimote = None
        try:
            self.wiimote = Wiimote()

        except WiimoteException:
            logging.error("Could not connect to wiimote. please try again")

        # Never stop looking for wiimote.
        while not self.killed:
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

                if buttons_state is not None:
                    if (buttons_state & cwiid.BTN_A):
                        # Kill any previous Challenge / RC mode
                        self.stop_threads()

                        # Inform user we are about to start RC mode
                        logging.info("Entering into RC Mode")
                        self.challenge = rc.rc(self.core, self.wiimote)

                        # Create and start a new thread
                        # running the remote control script
                        logging.info("Starting RC Thread")
                        self.challenge_thread = threading.Thread(
                            target=self.challenge.run)
                        self.challenge_thread.start()
                        logging.info("RC Thread Running")

                    if (buttons_state & cwiid.BTN_B):
                        # Kill any previous Challenge / RC mode
                        self.stop_threads()

                    if (buttons_state & cwiid.BTN_UP):
                        logging.info("BUTTON_UP")
                    if (buttons_state & cwiid.BTN_DOWN):
                        logging.info("BUTTON_DOWN")
                    if (buttons_state & cwiid.BTN_LEFT):
                        logging.info("BUTTON_LEFT")
                    if (buttons_state & cwiid.BTN_RIGHT):
                        logging.info("BUTTON_RIGHT")

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
                        # Neither Z buttons pressed,
                        # allow motors to move freely.
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
        launcher.wiimote = None
        launcher.stop_threads()  # This will set neutral for us.
        print("Stopping")
