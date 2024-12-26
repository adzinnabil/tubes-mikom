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
    lower_blue = cv2.getTrackbarPos('LB', 'bgr Trackbars')
    lower_green = cv2.getTrackbarPos('LG', 'bgr Trackbars')
    lower_red = cv2.getTrackbarPos('LR', 'bgr Trackbars')
    return lower_blue, lower_green, lower_red

def get_upper_bgr():
    upper_blue = cv2.getTrackbarPos('UB', 'bgr Trackbars')
    upper_green = cv2.getTrackbarPos('UG', 'bgr Trackbars')
    upper_red = cv2.getTrackbarPos('UR', 'bgr Trackbars')
    return upper_blue, upper_green, upper_red

def main(cam):
    # Ukuran crop
    lebar_crop = 400
    tinggi_crop = 360

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame")
            break

        # Resolusi asli frame
        frame_height, frame_width, _ = frame.shape

        # Koordinat crop di tengah
        x_start = (frame_width - lebar_crop) //4
        x_end = x_start + lebar_crop
        y_start = (frame_height - tinggi_crop) // 4
        y_end = y_start + tinggi_crop

        # Crop frame
        cropped_frame = frame[y_start:y_end, x_start:x_end]

        # Get lower and upper BGR values
        low = get_lower_bgr()
        high = get_upper_bgr()

        # Threshold the cropped frame
        thresh = cv2.inRange(cropped_frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Save lower and upper bounds to .npy files
        lower = np.array([low])
        upper = np.array([high])
        np.save('green_low.npy', lower)
        np.save('green_high.npy', upper)

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
    camera = cv2.VideoCapture(0,cv2.CAP_V4L2)  # Use default camera
    main(camera)
