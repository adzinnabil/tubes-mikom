import cv2
import numpy as np
import serial
import time


arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=9600, timeout=.1)

def write_to_serial(value):
    arduino.write(bytes(value, 'utf-8'))
    time.sleep(0.05)
    response = arduino.readline().decode('utf-8').strip()
    print(f"Command sent: {value}, Response: {response}")


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

    
    if detected_color and current_time - last_detected[detected_color] >= 2:
        command = None
        if detected_color == "merah":
            command = "1"  # Maju
        elif detected_color == "biru":
            command = "2"  # Kanan
        elif detected_color == "hijau":
            command = "3"  # Mundur
        
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

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        detect_color(frame, colors)
        frameBlur = cv2.GaussianBlur(frame, (7, 7), 1) 
        frameCanny = cv2.Canny(frameBlur, 50, 70)
        cv2.imshow("Hasilnya", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
