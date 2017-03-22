from numpy import interp, clip


class Servo_Controller():

    def __init__(self,
                 min=800,
                 mid=1300,
                 max=1800,
                 bReverse=False,
                 scale_factor=1.0):
        """ Standard constructor """
        self.servo_min = min
        self.servo_mid = mid
        self.servo_max = max
        self.servo_reversed = bReverse

        # Speed multiplier, expected in range [0.0, 1.0]
        self.scale_factor = clip(scale_factor, 0.0, 1.0)

    def micros(self, fSpeed):
        """ Map an abstract speed in [1, -1] to servo control microseconds. """

        # NOTE: input speed is multiplied by scale factor.
        # Used in RC mode to reduce overall speed and improve drivability.
        micros = 0
        if(self.servo_reversed):
            micros = interp(fSpeed * self.scale_factor,
                            [-1, 1],
                            [self.servo_max, self.servo_min])
        else:
            micros = interp(fSpeed * self.scale_factor,
                            [-1, 1],
                            [self.servo_min, self.servo_max])
        return int(micros)

    def set_scale_factor(self, scale_factor):
        # Speed multiplier, expected in range [0.0, 1.0]
        self.scale_factor = clip(scale_factor, 0.0, 1.0)

    def set_min(self, newmin):
        self.servo_min = newmin

    def set_max(self, newmax):
        self.servo_max = newmax

    def set_mid(self, newmid):
        self.servo_mid = newmid

    def set_reverse(self, new_rev):
        self.servo_reversed = new_rev

    def adjust_range(self, adjust_value):
        """ Increment or decrement entire range by a given value. """
        self.set_min(self.servo_min + adjust_value)
        self.set_max(self.servo_max + adjust_value)
        self.set_mid(self.servo_mid + adjust_value)
