# Import triangula module to interact with SixAxis
import core
import time
# import sounds


class TitoLogo:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run_auto(self):
        self.core.enable_motors(True)
        """Read a sensor and set motor speeds accordingly"""
        while not self.killed:
            prox = self.core.read_sensor()

            # sensor measures distance to left wall
            # so lower sensor value means more left motor needed
            self.leftspeed = (20 - prox) / 20.0
            self.rightspeed = (prox) / 20.0

            self.core.throttle(self.leftspeed, self.rightspeed)

            print ("Motors %f, %f" % (self.leftspeed, self.rightspeed))

            time.sleep(0.5)


if __name__ == "__main__":
    core = core.Core()
    tito_logo = TitoLogo(core)
    try:
        tito_logo.run_auto()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        tito_logo.stop()
        core.stop()
        print("Quitting")
