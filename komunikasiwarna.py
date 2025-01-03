import cv2
import numpy as np
import serial
import time
import RPi.GPIO as GPIO

# Inisialisasi komunikasi serial dengan Arduino
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

def write_to_serial(value):
    """
    Fungsi untuk mengirim perintah ke Arduino melalui komunikasi serial.
    """
    arduino.write(bytes(value, 'utf-8'))
    time.sleep(0.05)
    response = arduino.readline().decode('utf-8').strip()
    print(f"Command sent: {value}, Response: {response}")

# GPIO setup untuk sensor ultrasonik
GPIO.setmode(GPIO.BCM)
TRIG = 24  # GPIO pin for TRIG
ECHO = 23  # GPIO pin for ECHO

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    """
    Fungsi untuk mengukur jarak dengan sensor ultrasonik.
    """
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # Tunggu sensor settle

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  # Bagi 2 untuk perjalanan pulang pergi

    return round(distance, 2)

# Variabel global
last_detected_time = 0
current_command = None
last_color = None

def detect_color(frame, colors):
    """
    Fungsi untuk mendeteksi warna dalam frame kamera.
    """
    detected_color = None

    for color_name, (low, high) in colors.items():
        thresh = cv2.inRange(frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, color_name, (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 2)
            detected_color = color_name

    return detected_color

def main():
    global last_detected_time, current_command, last_color

    colors = {
        "biru": (np.load('/home/mikom/tubes-mikom/blue_low.npy'), np.load('/home/mikom/tubes-mikom/blue_high.npy')),
        "merah": (np.load('/home/mikom/tubes-mikom/red_low.npy'), np.load('/home/mikom/tubes-mikom/red_high.npy')),
        "hijau": (np.load('/home/mikom/tubes-mikom/green_low.npy'), np.load('/home/mikom/tubes-mikom/green_high.npy')),
    }

    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        print("Gagal membuka kamera")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        # Deteksi warna dalam frame
        detected_color = detect_color(frame, colors)

        if detected_color:
            current_time = time.time()

            if detected_color == last_color:
                if current_time - last_detected_time >= 2:  # 2 detik
                    print(f"Warna terdeteksi selama 2 detik: {detected_color}")

                    if detected_color == "merah":
                        command = "1"
                    elif detected_color == "biru":
                        command = "2"
                    elif detected_color == "hijau":
                        command = "3"
                    else:
                        command = None

                    if command:
                        distance = measure_distance()
                        print(f"Jarak terdeteksi: {distance} cm")

                        if distance < 70:
                            write_to_serial(command)
                            current_command = command
            else:
                last_detected_time = current_time
                last_color = detected_color

        frameBlur = cv2.GaussianBlur(frame, (7, 7), 1)
        frameCanny = cv2.Canny(frameBlur, 50, 70)
        cv2.imshow("Hasilnya", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
