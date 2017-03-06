import core
import time

class Logo:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.core = core_module
        self.ticks = 0
        self.tick_time = 0.1 # How many seconds per control loop
        self.time_limit = 100 # How many seconds to run for


    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        print("Start run")
        ls = 0
        rs = 0
        speed_mod = 0.2

        """Read a sensor and set motor speeds accordingly"""
        self.core.enable_motors(True)

        tick_limit = self.time_limit / self.tick_time

        while not self.killed and self.ticks < tick_limit:
            self.core.throttle(0, 0)
            user_input = raw_input("Command?")
            for letter in user_input:
                if (letter == "q"):
                    self.killed = 1
                    ls = 0
                    rs = 0
                elif (letter == "f"):
                    ls = speed_mod
                    rs = speed_mod
                elif(letter == "b"):
                    ls = 0 - speed_mod
                    rs = 0 - speed_mod
                elif(letter == "l"):
                    ls = 0 - speed_mod
                    rs = speed_mod
                elif(letter == "r"):
                    ls = speed_mod
                    rs = 0 - speed_mod
                elif(letter == "s"):
                    ls = 0
                    rs = 0
                self.core.throttle(ls, rs)
                print("Motors %f, %f" % (ls, rs))
                if not self.killed:
                    time.sleep(0.1)


if __name__ == "__main__":
    print("derp")
    core = core.Core()
    logo = Logo(core)
    try:
        logo.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        logo.stop()
        core.stop()
        print("Quitting")        
