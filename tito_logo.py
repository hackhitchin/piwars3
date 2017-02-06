# Import triangula module to interact with SixAxis
import drivetrain
import time
# import sounds

class rc:
    def __init__(self, drive):
        """Class Constructor"""
        self.killed = False
        self.drive = drive
        self.ticks = 0

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run_auto(self):
        i = 0
        speed_ratio = 0.1
        self.drive.enable_motors(True)
        """Read a sensor and set motor speeds accordingly"""
        while not self.killed:
            prox = self.drive.read_sensor()
            
            # sensor measures distance to left wall
            # so lower sensor value means more left motor needed
            self.leftspeed = (20 - prox)/20.0
            self.rightspeed = (prox)/20.0
            
            self.drive.throttle(self.leftspeed, self.rightspeed)
            
            print ("Motors %f, %f" % (self.leftspeed, self.rightspeed) )
            
            time.sleep(0.5)
            

if __name__ == "__main__":
    drive = drivetrain.DriveTrain()
    rc = rc(drive)
    try:
        rc.run_auto()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        rc.stop()
        drive.stop()
        print("Quitting")
