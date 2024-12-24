import cv2
import numpy as np
import serial
import time
import RPi.GPIO as GPIO  # Untuk sensor ultrasonik pada Raspberry Pi

# Inisialisasi serial
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

# Konfigurasi pin sensor ultrasonik
TRIG_PIN = 23
ECHO_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def write_to_serial(value):
    arduino.write(bytes(value, 'utf-8'))
    time.sleep(0.05)
    response = arduino.readline().decode('utf-8').strip()
    print(f"Command sent: {value}, Response: {response}")

# Fungsi untuk membaca jarak dari sensor ultrasonik
def read_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.05)
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Konversi ke cm
    return round(distance, 2)

# Variabel untuk mencatat status deteksi
last_detected = {"merah": 0, "biru": 0, "hijau": 0}
current_command = None

def detect_color(frame, colors):
    global last_detected, current_command
    current_time = time.time()
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
            last_detected[color_name] = current_time

    # Periksa jarak dengan sensor ultrasonik
    distance = read_distance()
    print(f"Jarak: {distance} cm")

    # Periksa apakah warna tetap terdeteksi selama 2 detik dan dalam jarak tertentu
    if detected_color and current_time - last_detected[detected_color] >= 2 and distance <= 20:
        command = None
        if detected_color == "merah":
            command = "1"  # Maju
        elif detected_color == "biru":
            command = "2"  # Kanan
        elif detected_color == "hijau":
            command = "3"  # Mundur
        
        # Kirim perintah hanya jika berbeda dari perintah terakhir
        if command and command != current_command:
            write_to_serial(command)
            current_command = command

def main():
    colors = {
        # "biru": (np.load('/home/zin/oprec-roboticsas-2024/blue_low.npy'), np.load('/home/zin/oprec-roboticsas-2024/blue_high.npy')),
        "merah": (np.load('/home/zin/mikom/red_low.npy'), np.load('/home/zin/mikom/red_high.npy')),
        "hijau": (np.load('/home/zin/mikom/green_low.npy'), np.load('/home/zin/mikom/green_high.npy')),
    }

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Gagal membuka kamera")
        return

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Gagal membaca frame dari kamera")
                break

            detect_color(frame, colors)
            frameBlur = cv2.GaussianBlur(frame, (7, 7), 1) 
            frameCanny = cv2.Canny(frameBlur, 50, 70)
            cv2.imshow("Hasilnya", frame)

            # Tekan 'q' untuk keluar
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()  # Pastikan GPIO di-reset

if __name__ == "__main__":
    main()
