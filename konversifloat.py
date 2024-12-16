import serial
import time

arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

def write_read(x):
    float_value = float(ord(x))  
    arduino.write(bytes(str(float_value), 'utf-8'))  
    time.sleep(0.05) 
    data = arduino.readline()  
    return data

while True:
    for i in range(26):
        char = chr(97 + i)  
        value = write_read(char)  
        print(value)  
        time.sleep(1)  #
