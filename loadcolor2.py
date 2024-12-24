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
    colors = {
        # "biru": (np.load('/home/zin/oprec-roboticsas-2024/blue_low.npy'), np.load('/home/zin/oprec-roboticsas-2024/blue_high.npy')),
        "merah": (np.load('/home/zin/mikom/red_low.npy'), np.load('/home/zin/mikom/red_high.npy')),
        "hijau": (np.load('/home/zin/mikom/green_low.npy'), np.load('/home/zin/mikom/green_high.npy')),
    }

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("gagal")
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

        # Tekan 'q' untuk keluar
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
