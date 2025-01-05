import cv2
import numpy as np
import serial
import time
import RPi.GPIO as GPIO

# Inisialisasi komunikasi serial dengan Arduino
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

command =""

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
    # Pastikan TRIG dalam keadaan low
    GPIO.output(TRIG, False)
    time.sleep(0.1)  # Tunggu sensor settle
    
    # Kirim pulsa 10us ke TRIG
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    # Tunggu ECHO high
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    # Tunggu ECHO low
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    # Hitung durasi pulsa
    pulse_duration = pulse_end - pulse_start
    
    # Hitung jarak (kecepatan suara = 34300 cm/s)
    distance = pulse_duration * 34300 / 2  # Bagi 2 untuk perjalanan pulang pergi
    
    return round(distance, 2)

# Variabel global
last_detected_time = 0
current_command = None

def detect_color(frame, colors, detection_duration=1):
    global last_detected_time
    detected_color = None
    current_time = time.time()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for color_name, (low, high) in colors.items():
        thresh = cv2.inRange(hsv, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, color_name, (x + (w // 2) - 10, y + (h // 2) - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 2)
            detected_color = color_name

    if detected_color:
        if current_time - last_detected_time >= detection_duration:
            if detected_color == "merah":
                command = "1"
            elif detected_color == "biru":
                command = "2"
            elif detected_color == "hijau":
                command = "3"

            distance = measure_distance()
            print(f"Jarak terdeteksi: {distance} cm")

            if distance < 70:
                write_to_serial(command)

        last_detected_time = current_time
    else:
        current_command = None

def main():
    # Memuat batas bawah dan atas warna dari file
    green_low = np.load('/home/mikom/tubes-mikom/hsvgreen_low.npy')
    green_high = np.load('/home/mikom/tubes-mikom/hsvgreen_high.npy')
    red_low = np.load('/home/mikom/tubes-mikom/hsvred_low.npy')
    red_high = np.load('/home/mikom/tubes-mikom/hsvred_high.npy')
    blue_low = np.load('/home/mikom/tubes-mikom/hsvblue_low.npy')
    blue_high = np.load('/home/mikom/tubes-mikom/hsvblue_high.npy')

    # Warna-warna yang akan dideteksi
    colors = {
        "Green": (green_low, green_high),
        "Red": (red_low, red_high),
        "Blue": (blue_low, blue_high)
    }

    # Inisialisasi kamera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        print("Gagal membuka kamera")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        # Mendapatkan ukuran asli frame
        height, width, _ = frame.shape

        # Menghitung koordinat crop agar berada di tengah
        crop_width = 480
        crop_height = 480
        start_x = (width - crop_width) // 2
        start_y = (height - crop_height) // 2
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Crop frame ke 240x240
        cropped_frame = frame[start_y:end_y, start_x:end_x]

        # Menampilkan frame yang sudah di-crop
        cv2.imshow("Cropped Frame", cropped_frame)

        # Deteksi warna dalam frame yang sudah di-crop
        detect_color(cropped_frame, colors)

        # Tekan 'q' untuk keluar dari loop
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Lepaskan kamera dan tutup jendela
    camera.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()



