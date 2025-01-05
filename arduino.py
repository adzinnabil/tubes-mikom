import serial

def initialize_arduino(port='/dev/ttyUSB0', baud_rate=9600):
    return serial.Serial(port, baud_rate, timeout=1)

def send_command(arduino, command):
    arduino.write(command)

def read_response(arduino):
    if arduino.in_waiting > 0:
        return arduino.readline().decode('utf-8').strip()
    return None
