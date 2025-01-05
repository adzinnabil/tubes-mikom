import cv2
import numpy as np

def callback():
    pass

def init_trackbars():
    cv2.namedWindow("HSV Trackbars")
    cv2.createTrackbar('LH', 'HSV Trackbars', 0, 179, callback)  # Hue range [0, 179]
    cv2.createTrackbar('LS', 'HSV Trackbars', 0, 255, callback)  # Saturation range [0, 255]
    cv2.createTrackbar('LV', 'HSV Trackbars', 0, 255, callback)  # Value range [0, 255]
    cv2.createTrackbar('UH', 'HSV Trackbars', 179, 179, callback)
    cv2.createTrackbar('US', 'HSV Trackbars', 255, 255, callback)
    cv2.createTrackbar('UV', 'HSV Trackbars', 255, 255, callback)

def get_lower_hsv():
    lower_hue = cv2.getTrackbarPos('LH', 'HSV Trackbars')
    lower_saturation = cv2.getTrackbarPos('LS', 'HSV Trackbars')
    lower_value = cv2.getTrackbarPos('LV', 'HSV Trackbars')
    return lower_hue, lower_saturation, lower_value

def get_upper_hsv():
    upper_hue = cv2.getTrackbarPos('UH', 'HSV Trackbars')
    upper_saturation = cv2.getTrackbarPos('US', 'HSV Trackbars')
    upper_value = cv2.getTrackbarPos('UV', 'HSV Trackbars')
    return upper_hue, upper_saturation, upper_value

def main(cam):
    # Ukuran crop
    lebar_crop = 640 
    tinggi_crop = 480

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Resolusi asli frame
        frame_height, frame_width, _ = frame.shape

        # Koordinat crop di tengah
        x_start = (frame_width - lebar_crop) // 2
        x_end = x_start + lebar_crop
        y_start = (frame_height - tinggi_crop) // 2
        y_end = y_start + tinggi_crop

        cropped_frame = frame[y_start:y_end, x_start:x_end]

        # Convert cropped frame to HSV
        hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)

        # Get lower and upper HSV values
        low = get_lower_hsv()
        high = get_upper_hsv()

        # Threshold the cropped frame in HSV
        thresh = cv2.inRange(hsv_frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Save lower and upper bounds to .npy files
        lower = np.array([low])
        upper = np.array([high])
        np.save('hsvgreen_low.npy', lower)
        np.save('hsvgreen_high.npy', upper)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Display results
        cv2.imshow("thresh", thresh)
        cv2.imshow("cropped_frame", cropped_frame)

        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    init_trackbars()
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)  # Use default camera
    main(camera)
