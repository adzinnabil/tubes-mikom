import cv2
import numpy as np
import serial
import time
import RPi.GPIO as GPIO

TRIG = 24
ECHO = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.1)

    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()

    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def send_command(command, arduino):
    arduino.write(command.encode())
    time.sleep(0.1)

def read_command_from_arduino(arduino):
    if arduino.in_waiting > 0:
        command = arduino.readline().decode('utf-8').strip()
        print(f"Command diterima dari Arduino: {command}")
        return command
    return None

def main(cam, arduino):
    lebar_crop = 640
    tinggi_crop = 480

    last_detection_time = None
    detected_color = None

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame")
            break

        frame_height, frame_width, _ = frame.shape

        x_start = (frame_width - lebar_crop) // 2
        x_end = x_start + lebar_crop
        y_start = (frame_height - tinggi_crop) // 2
        y_end = y_start + tinggi_crop

        cropped_frame = frame[y_start:y_end, x_start:x_end]

        hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)

        green_low = np.load('/home/mikom/tubes-mikom/hsvgreen_low.npy')
        green_high = np.load('/home/mikom/tubes-mikom/hsvgreen_high.npy')
        red_low = np.load('/home/mikom/tubes-mikom/hsvred_low.npy')
        red_high = np.load('/home/mikom/tubes-mikom/hsvred_high.npy')
        blue_low = np.load('/home/mikom/tubes-mikom/hsvblue_low.npy')
        blue_high = np.load('/home/mikom/tubes-mikom/hsvblue_high.npy')

        colors = {
            "Green": (green_low, green_high),
            "Red": (red_low, red_high),
            "Blue": (blue_low, blue_high)
        }

        detected_color_in_this_frame = None

        for color_name, (low, high) in colors.items():
            thresh = cv2.inRange(hsv, low, high)

            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

            contour, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contour:
                largest_contour = max(contour, key=cv2.contourArea)

                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.putText(cropped_frame, color_name, (x + w // 2, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                detected_color_in_this_frame = color_name
                last_detection_time = time.time()

        if detected_color_in_this_frame is None:
            detected_color = None

        distance = get_distance()
        print(f"Jarak: {distance} cm")

        if detected_color_in_this_frame is not None and last_detection_time is not None:
            if time.time() - last_detection_time >= 1:
                if distance < 70:
                    if detected_color_in_this_frame != detected_color:
                        detected_color = detected_color_in_this_frame
                        if detected_color == "Red":
                            send_command('1', arduino)
                        elif detected_color == "Blue":
                            send_command('2', arduino)
                        elif detected_color == "Green":
                            send_command('3', arduino)

        command_from_arduino = read_command_from_arduino(arduino)
        if command_from_arduino:
            print(f"Melakukan aksi berdasarkan command dari Arduino: {command_from_arduino}")

        cv2.imshow('cropped_frame', cropped_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)

    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)

    main(cam, arduino)


