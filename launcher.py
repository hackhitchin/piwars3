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
import Calibration


logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class launcher:
    def __init__(self):

        self.reading_calibration = True

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

        # WiiMote LED counter to indicate mode
        # NOTE: the int value will be shown as binary on the wiimote.
        self.MODE_NONE = 1
        self.MODE_RC = 2
        self.MODE_WALL = 3
        self.MODE_MAZE = 4
        self.MODE_CALIBRATION = 5

    def stop_threads(self):
        """ Single point of call to stop any RC or Challenge Threads """

        if self.challenge:
            self.challenge.stop()
            self.challenge = None
            self.challenge_thread = None
            logging.info("Stopping Challenge Thread")
        else:
            logging.info("No Challenge Thread")

        # Reset LED to NO MODE
        if self.wiimote and self.wiimote.wm:
            self.wiimote.wm.led = self.MODE_NONE

        # Safety setting
        self.core.enable_motors(False)

    def read_config(self):
        # Read the config file when starting up.
        if self.reading_calibration:
            calibration = Calibration(core)
            calibration.read_config()

    def start_rc_mode(self):
        # Kill any previous Challenge / RC mode
        self.stop_threads()

        # Set Wiimote LED to RC Mode index
        if self.wiimote and self.wiimote.wm:
            self.wiimote.wm.led = self.MODE_RC

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

    def start_calibration_mode(self):
        # Kill any previous Challenge / RC mode
        self.stop_threads()

        # Set Wiimote LED to RC Mode index
        if self.wiimote and self.wiimote.wm:
            self.wiimote.wm.led = self.MODE_CALIBRATION

        # Inform user we are about to start RC mode
        logging.info("Entering into Calibration Mode")
        self.challenge = \
            Calibration.Calibration(self.core, self.wiimote)

        # Create and start a new thread
        # running the remote control script
        logging.info("Starting Calibration Thread")
        self.challenge_thread = threading.Thread(
            target=self.challenge.run)
        self.challenge_thread.start()
        logging.info("Calibration Thread Running")

    def run(self):
        """ Main Running loop controling bot mode and menu state """
        self.read_config()

        # Never stop looking for wiimote.
        while not self.killed:
            self.wiimote = None
            try:
                self.wiimote = Wiimote()

            except WiimoteException:
                logging.error("Could not connect to wiimote. please try again")

            # Reset LED to NO MODE
            if self.wiimote and self.wiimote.wm:
                self.wiimote.wm.led = self.MODE_NONE

            # Constantly check wiimote for button presses
            while self.wiimote:
                buttons_state = self.wiimote.get_buttons()
                classic_buttons_state = self.wiimote.get_classic_buttons()

                if buttons_state is not None:
                    if (buttons_state & cwiid.BTN_A):
                        self.start_rc_mode()

                    if (buttons_state & cwiid.BTN_HOME):
                        self.start_calibration_mode()

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
                    if (classic_buttons_state & cwiid.CLASSIC_BTN_ZL or
                            classic_buttons_state & cwiid.CLASSIC_BTN_ZR):
                        # One of the Z buttons pressed, disable
                        # motors and set neutral.
                        self.core.enable_motors(False)
                    else:
                        # Neither Z buttons pressed,
                        # allow motors to move freely.
                        self.core.enable_motors(True)

                time.sleep(0.05)

                # Verify Wiimote is connected each loop. If not, set wiimote
                # to None and it "should" attempt to reconnect.
                if not self.wiimote.wm:
                    self.stop_threads()
                    self.wiimote = None


if __name__ == "__main__":
    launcher = launcher()
    try:
        launcher.run()
    except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        launcher.wiimote = None
        launcher.stop_threads()  # This will set neutral for us.
        print("Stopping")
