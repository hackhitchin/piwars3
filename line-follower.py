import serial
import time

ser = serial.Serial(
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

try:
    while(True):
        # Send empty command to arduino
        command = "[]\n"
        print(command)
        ser.write(command)
        result = ser.readline()
        print(result)
        time.sleep(0.5)
except:
    if ser:
        ser.close()

