import core
import time


class rc:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core_module = core_module
        self.ticks = 0

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """

        # Loop indefinitely, or until this thread is flagged as stopped.
        while not self.killed:
            # While in RC mode, get joystick states and pass speeds to motors.
            try:
                l_joystick_state = \
                    self.wiimote.get_classic_joystick_state(True)
                r_joystick_state = \
                    self.wiimote.get_classic_joystick_state(False)
            except:
                print("Failed to get Joystick")

            # Annotate joystick states to screen
            if l_joystick_state:
                print("l_joystick_state: {}".format(l_joystick_state))
            if r_joystick_state:
                print("r_joystick_state: {}".format(r_joystick_state))

            # Grab normalised x,y / steering,throttle
            # from left and right joysticks.
            l_joystick_pos = l_joystick_state['state']['normalised']
            l_throttle, l_steering = l_joystick_pos
            r_joystick_pos = r_joystick_state['state']['normalised']
            r_throttle, r_steering = r_joystick_pos

            self.core_module.throttle(self.l_throttle, self.r_throttle)
            print ("Motors %f, %f" % (self.l_throttle, self.r_throttle))

            # Sleep between loops to allow other stuff to
            # happen and not over burden Pi and Arduino.
            time.sleep(0.5)


if __name__ == "__main__":
    core = core.Core()
    rc = rc(core)
    try:
        rc.run_auto()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        rc.stop()
        core.set_neutral()
        print("Quitting")
