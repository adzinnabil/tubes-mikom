import cv2
import time
from camera import initialize_camera, release_camera
from arduino import initialize_arduino, send_command, read_response
from distance_sensor import setup_distance_sensor, cleanup_distance_sensor, get_distance
from color_detection import load_color_ranges, detect_color

def main():
    cam = initialize_camera()
    arduino = initialize_arduino()
    setup_distance_sensor()

    colors = load_color_ranges()

    lebar_crop = 640
    tinggi_crop = 480

    detected_color_start_time = None
    last_detected_color = None

    try:
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

            detected_color, bounding_box = detect_color(hsv, colors)

            if bounding_box:
                x, y, w, h = bounding_box
                cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(cropped_frame, detected_color, (x + w // 2, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            distance = get_distance()

            if detected_color == last_detected_color:
                if detected_color_start_time is None:
                    detected_color_start_time = time.time()
                elif time.time() - detected_color_start_time >= 2:
                    if distance < 70:
                        if detected_color == "Red":
                            send_command(arduino, b'1')
                        elif detected_color == "Blue":
                            send_command(arduino, b'2')
                        elif detected_color == "Green":
                            send_command(arduino, b'3')
                    detected_color_start_time = None
            else:
                detected_color_start_time = None
                last_detected_color = detected_color

            response = read_response(arduino)
            if response:
                print(f"Response from Arduino: {response}")

            cv2.imshow('cropped_frame', cropped_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        release_camera(cam)
        cleanup_distance_sensor()

if __name__ == '__main__':
    main()
