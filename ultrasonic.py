import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
TRIG = 23  # GPIO pin for TRIG
ECHO = 24  # GPIO pin for ECHO

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Ensure TRIG is low
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # Wait for sensor to settle
    
    # Send a 10us pulse to TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # Wait for ECHO to go high
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    # Wait for ECHO to go low
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start
    
    # Calculate distance (speed of sound = 34300 cm/s)
    distance = pulse_duration * 34300 / 2  # Divide by 2 for round trip
    
    return round(distance, 2)

try:
    while True:
        dist = measure_distance()
        print(f"Distance: {dist} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()
