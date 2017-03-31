import serial
import time
import core
from numpy import interp, clip


class LineFollower:
    def __init__(self, core_module, oled):
        """Class Constructor"""
        self.core = core_module
        self.oled = oled
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

        # Rough calibration values
        self.black = 512
        self.white = 3000
        self.weights = [-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5];

    def show_sensor_readout(self, line_sensor):
        """ Show motor/aux config on OLED display """
        if self.oled is not None:
            # Format the speed to 2dp
            if len(line_sensor) == 8:
                message = ("{}, "
                           "{}, "
                           "{}, "
                           "{}, "
                           "{}, "
                           "{}, "
                           "{}, "
                           "{}").format(
                    line_sensor[0],
                    line_sensor[1],
                    line_sensor[2],
                    line_sensor[3],
                    line_sensor[4],
                    line_sensor[5],
                    line_sensor[6],
                    line_sensor[7]
                )

                self.oled.cls()  # Clear Screen
                self.oled.canvas.text((10, 10), message, fill=1)
                # Now show the mesasge on the screen
                self.oled.display()

    def stop(self):
        """Simple method to stop the RC loop"""
        self.killed = True

    def run(self):
        """ Main Challenge method. Has to exist and is the
            start point for the threaded challenge. """
        nTicksSinceLastMenuUpdate = -1
        nTicksBetweenMenuUpdates = 10  # 10*0.05 seconds = every half second

        # Loop indefinitely, or until this thread is flagged as stopped.
        while not self.killed:
            # Send empty command to arduino to invoke a 'read'
            command = "[]\n"
            self.ser.write(command)
            # Read line from arduino
            result_str = self.ser.readline()
            print(result_str)

            # read sensor values as string from arduino.
            sensor_values = result_str.split(',')
            # Convert list of strings to list of ints

            if len(sensor_values) != 8:
                sensor_values = [-1,-1,-1,-1,-1,-1,-1,-1]

            sensor_values = map(int, sensor_values)
            print("Sensor values:")
            print sensor_values

            deviation = algorithm(sensor_values)
            print("Deviation is %d" % deviation)
            # pause for brief time.
            time.sleep(0.05)

            # Show sensor readout periodically.
            if (nTicksSinceLastMenuUpdate == -1 or
               nTicksSinceLastMenuUpdate >= nTicksBetweenMenuUpdates):
                self.show_sensor_readout(sensor_values)
                nTicksSinceLastMenuUpdate = 0
            else:
                nTicksSinceLastMenuUpdate = nTicksSinceLastMenuUpdate + 1

        if self.ser:
            self.ser.close()

    def algorithm(sensor_values):
        average_position = 0

        # Turn light values (3000 for white, 500 for black) into a simple weight 0-1
        # So one completely black sensor would return that sensor position
        calibrated_sensor_values = map(weight_sensor, sensor_values)

        # For each 
        for i in range(0,9):
            average_position += self.weights[i] * calibrated_sensor_values[i]

        return average_position

    def weight_sensor(value):
        return numpy.interp(value, [white, black], [0, 1])



if __name__ == "__main__":
    core = core.Core(None)
    line = LineFollower(core)
    try:
        line.run()
    except (KeyboardInterrupt) as e:
        # except (Exception, KeyboardInterrupt) as e:
        # Stop any active threads before leaving
        core.set_neutral()
        if line.ser:
            line.ser.close()
        print("Quitting")