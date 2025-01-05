import cv2
import numpy as np
import serial  
import RPi.GPIO as GPIO  
import time


TRIG = 24
ECHO = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

   
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def main(cam, arduino):

    lebar_crop = 640 
    tinggi_crop = 480

    detected_color_start_time = None  
    last_detected_color = None  

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

        detected_color = None  

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
                
                detected_color = color_name  
        distance = get_distance()

        if detected_color == last_detected_color:
            if detected_color_start_time is None:
                detected_color_start_time = time.time()
            elif time.time() - detected_color_start_time >= 2:  
                if distance < 70:  
                    if detected_color == "Red":
                        arduino.write(b'1')
                    elif detected_color == "Blue":
                        arduino.write(b'2')
                    elif detected_color == "Green":
                        arduino.write(b'3')
                detected_color_start_time = None  
        else:
            detected_color_start_time = None  
            last_detected_color = detected_color

        if arduino.in_waiting > 0:
            response = arduino.readline().decode('utf-8').strip()
            print(f"Response from Arduino: {response}")

        cv2.imshow('cropped_frame', cropped_frame)  
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    GPIO.cleanup() 

if __name__ == '__main__':

    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    arduino_port = '/dev/ttyUSB0'  
    baud_rate = 9600 
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    main(cam, arduino)  