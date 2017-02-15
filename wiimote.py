import cwiid
import logging

from numpy import clip, interp


class WiimoteException(Exception):
    pass


class WiimoteNunchukException(WiimoteException):
    pass


class Wiimote():
    """Wrapper class for the wiimote interaction"""
    def __init__(
        self,
        max_tries=5,
        joystick_range=None,
        joystick_classic_l_range=None,
        joystick_classic_r_range=None
    ):
        """ Constructor """
        # Initialise joystick ranges to EITHER
        # parameter passed in or default range.
        self.joystick_range = joystick_range if joystick_range else [50, 200]

        # It appears classic joysticks idle at raw value of 16 for both X and Y
        self.joystick_classic_l_range = joystick_classic_l_range \
            if joystick_classic_l_range else [50, 200]

        self.joystick_classic_r_range = joystick_classic_r_range \
            if joystick_classic_r_range else [50, 200]

        # Initialise wiimote
        self.wm = None
        attempts = 0

        logging.info("Press 1+2 on your Wiimote now...")

        # Attempt to get a connection to the wiimote
        # try a few times, as it can take a few attempts
        while not self.wm:
            try:
                self.wm = cwiid.Wiimote()
            except RuntimeError:
                if attempts == max_tries:
                    logging.error("cannot create connection")
                    raise WiimoteException(
                        "Could not create connection within {0} tries".format(
                            max_tries
                        )
                    )
                logging.error("Error opening wiimote connection")
                logging.error("attempt {0}".format(attempts))
                attempts += 1

        # set wiimote to report button presses and accelerometer state
        self.wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_EXT

        # Set led state
        self.wm.led = 1

    def get_state(self):
        """Get the full raw state of the wiimote.
        Returns: dict"""
        return self.wm.state if self.wm else None

    def get_joystick_state(self):
        """Returns a dictionary containing the state
           of the nunchuk joystick in the form """
        if 'nunchuk' not in self.get_state():
            logging.debug("state: {0}".format(self.get_state()))
            return None
        else:
            joystick_state_raw = self.wm.state['nunchuk']['stick']
            joystick_state_clipped = [
                clip(channel, *self.joystick_range)
                for channel
                in joystick_state_raw
            ]
            joystick_state_normalised = [
                interp(channel, self.joystick_range, [-1, 1])
                for channel
                in joystick_state_raw
            ]
            return dict(
                range=self.joystick_range,
                state=dict(
                    raw=joystick_state_raw,
                    clipped=joystick_state_clipped,
                    normalised=joystick_state_normalised
                )
            )

    def get_buttons(self):
        """Get just the current button state of the wiimote"""
        return self.wm.state['buttons']

    def get_nunchuk_buttons(self):
        """Get just the current button state of the wiimote nunchuk"""
        if 'nunchuk' not in self.get_state():
            return None
        return self.wm.state['nunchuk']['buttons']

    def get_classic_buttons(self):
        """Get just the current button state of the wiimote nunchuk"""
        if 'classic' not in self.get_state():
            return None
        return self.wm.state['classic']['buttons']

    def get_classic_joystick_state(self, left_stick):
        """Returns a dictionary containing the state
           of the nunchuk joystick in the form """
        if 'classic' not in self.get_state():
            return None
        else:
            if left_stick:
                joystick_state_raw = self.wm.state['classic']['l_stick']
                joystick_state_clipped = [
                    clip(channel,
                         *self.joystick_classic_l_range)
                    for channel
                    in joystick_state_raw
                ]
                joystick_state_normalised = [
                    interp(channel, self.joystick_classic_l_range, [-1, 1])
                    for channel
                    in joystick_state_raw
                ]
                return dict(
                    range=self.joystick_classic_l_range,
                    state=dict(
                        raw=joystick_state_raw,
                        clipped=joystick_state_clipped,
                        normalised=joystick_state_normalised
                    )
                )
            else:
                joystick_state_raw = self.wm.state['classic']['r_stick']
                joystick_state_clipped = [
                    clip(channel,
                         *self.joystick_classic_r_range)
                    for channel
                    in joystick_state_raw
                ]
                joystick_state_normalised = [
                    interp(channel, self.joystick_classic_r_range, [-1, 1])
                    for channel
                    in joystick_state_raw
                ]
                return dict(
                    range=self.joystick_classic_r_range,
                    state=dict(
                        raw=joystick_state_raw,
                        clipped=joystick_state_clipped,
                        normalised=joystick_state_normalised
                    )
                )
