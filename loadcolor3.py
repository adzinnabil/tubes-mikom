import cv2
import numpy as np

def detect_color(frame, colors):
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

def main():
    # Load saved color ranges
    colors = {
        "biru": (np.load('/home/mikom/tubes-mikom/blue_low.npy'), np.load('/home/mikom/tubes-mikom/blue_high.npy')),
        "merah": (np.load('/home/mikom/tubes-mikom/red_low.npy'), np.load('/home/mikom/tubes-mikom/red_high.npy')),
        "hijau": (np.load('/home/mikom/tubes-mikom/green_low.npy'), np.load('/home/mikom/tubes-mikom/green_high.npy')),
    }

    # Initialize camera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        print("Gagal membuka kamera")
        return

    # Crop dimensions
    lebar_crop = 400
    tinggi_crop = 360

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Gagal membaca frame dari kamera")
            break

        # Get frame dimensions
        frame_height, frame_width, _ = frame.shape

        # Crop frame to center
        x_start = (frame_width - lebar_crop) // 2
        x_end = x_start + lebar_crop
        y_start = (frame_height - tinggi_crop) // 2
        y_end = y_start + tinggi_crop
        cropped_frame = frame[y_start:y_end, x_start:x_end]

        # Detect colors in cropped frame
        detect_color(cropped_frame, colors)

        # Optional: Apply Gaussian Blur and Canny Edge Detection
        frame_blur = cv2.GaussianBlur(cropped_frame, (7, 7), 1)
        frame_canny = cv2.Canny(frame_blur, 50, 70)

        # Display frames
        cv2.imshow("Hasil Cropped Frame", cropped_frame)
        cv2.imshow("Gaussian Blur", frame_blur)
        cv2.imshow("Canny Edges", frame_canny)

        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
