import cv2
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

def main():
    # Open the camera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        print("Kamera gagal")
        return

    while True:
        ret, frame = camera.read()

        if not ret:
            print("Frame gagal")
            break

        # Mendapatkan ukuran asli frame
        height, width, _ = frame.shape

        # Menghitung koordinat crop agar berada di tengah
        crop_width = 240
        crop_height = 240
        start_x = (width - crop_width) // 2
        start_y = (height - crop_height) // 2
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Crop frame ke 240x240
        cropped_frame = frame[start_y:end_y, start_x:end_x]

        # Menampilkan frame yang sudah di-crop
        cv2.imshow("Cropped Frame", cropped_frame)

        # Mengukur jarak dengan sensor ultrasonik
        dist = measure_distance()
        print(f"Distance: {dist} cm")

        # Keluar dengan menekan 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

if __name__ == "__main__":
    main()
