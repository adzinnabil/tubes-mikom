import cv2
import numpy as np

def callback():
    pass

def init_trackbars():
    cv2.namedWindow("bgr Trackbars")

    cv2.createTrackbar('LB', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('LG', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('LR', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('UB', 'bgr Trackbars', 255, 255, callback)
    cv2.createTrackbar('UG', 'bgr Trackbars', 255, 255, callback)
    cv2.createTrackbar('UR', 'bgr Trackbars', 255, 255, callback)

def get_lower_bgr():
    return (
        cv2.getTrackbarPos('LB', 'bgr Trackbars'),
        cv2.getTrackbarPos('LG', 'bgr Trackbars'),
        cv2.getTrackbarPos('LR', 'bgr Trackbars')
    )

def get_upper_bgr():
    return (
        cv2.getTrackbarPos('UB', 'bgr Trackbars'),
        cv2.getTrackbarPos('UG', 'bgr Trackbars'),
        cv2.getTrackbarPos('UR', 'bgr Trackbars')
    )

def main(cam):
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Error: Gagal membaca frame!")
            break

        low = get_lower_bgr()
        high = get_upper_bgr()

        thresh = cv2.inRange(frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        lower = np.array([low])
        upper = np.array([high])

        np.save('green_low.npy', lower)
        np.save('green_high.npy', upper)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("thresh", thresh)
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    init_trackbars()
    camera_index = 0
    camera = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)
    
    if not camera.isOpened():
        print("Error: Webcam tidak dapat diakses!")
        exit()

    main(camera)
    camera.release()
    cv2.destroyAllWindows()
