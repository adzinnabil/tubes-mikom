import cv2
import numpy as np

def main(cam):

    lebar_crop = 640 
    tinggi_crop = 480

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
        
        green_low = np.load('/home/mikom/tubes-mikom/hsvgreen_low.npy')
        green_high = np.load('/home/mikom/tubes-mikom/hsvgreen_high.npy')
        red_low = np.load('/home/mikom/tubes-mikom/hsvred_low.npy')
        red_high = np.load('/home/mikom/tubes-mikom/hsvred_high.npy')
        blue_low = np.load('/home/mikom/tubes-mikom/hsvblue_low.npy')
        blue_high = np.load('/home/mikom/tubes-mikom/hsvblue_high.npy')

        colors = {
            "Green": (green_low, green_high),
            "Red": (red_low, red_high),
            "Blue": (blue_low, blue_high)
        }

        for color_name, (low, high) in colors.items():
            thresh = cv2.inRange(hsv, low, high)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            contour, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contour:
                largest_contour = max(contour, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(cropped_frame, color_name, (x + w // 2, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow('cropped_frame', cropped_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
    main(cam)
