import serial
import time
import core

class LineFollower:
    def __init__(self, core_module):
        """Class Constructor"""
        self.killed = False
        self.ser = serial.Serial(
            "/dev/ttyUSB0",
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            writeTimeout=0,
            timeout=10,
            rtscts=False,
            dsrdtr=False,
            xonxoff=False)

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """

        # Loop indefinitely, or until this thread is flagged as stopped.
        while not self.killed:
            # Send empty command to arduino
            command = "[]\n"
            print(command)
            self.ser.write(command)
            result = self.ser.readline()
            print(result)
            time.sleep(0.5)


if __name__ == "__main__":
    core = core.Core(None)
    line = LineFollower(core)
    try:
        line.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        core.set_neutral()
        if ser:
            ser.close()
        print("Quitting")

