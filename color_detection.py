import cv2
import numpy as np

def load_color_ranges():
    green_low = np.load('/home/mikom/tubes-mikom/hsvgreen_low.npy')
    green_high = np.load('/home/mikom/tubes-mikom/hsvgreen_high.npy')
    red_low = np.load('/home/mikom/tubes-mikom/hsvred_low.npy')
    red_high = np.load('/home/mikom/tubes-mikom/hsvred_high.npy')
    blue_low = np.load('/home/mikom/tubes-mikom/hsvblue_low.npy')
    blue_high = np.load('/home/mikom/tubes-mikom/hsvblue_high.npy')

    return {
        "Green": (green_low, green_high),
        "Red": (red_low, red_high),
        "Blue": (blue_low, blue_high)
    }

def detect_color(hsv_frame, colors):
    detected_color = None
    for color_name, (low, high) in colors.items():
        thresh = cv2.inRange(hsv_frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contour, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contour:
            largest_contour = max(contour, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            return color_name, (x, y, w, h)
    return None, None
