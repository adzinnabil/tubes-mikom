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
    return lower_blue,lower_red,lower_green

def get_upper_bgr():
    upper_blue = cv2.getTrackbarPos('UB', 'bgr Trackbars')
    upper_green = cv2.getTrackbarPos('UG', 'bgr Trackbars')
    upper_red = cv2.getTrackbarPos('UR', 'bgr Trackbars')
    return upper_blue,upper_green,upper_red

def main(cam):
    while True:
        ret, frame = cam.read()
        # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # low = (146,111,0)
        # high = (255,255,0)
        low = get_lower_bgr()
        high = get_upper_bgr()

        thresh = cv2.inRange (frame,low,high)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,kernel)

        lower = np.array([low])
        upper = np.array([high])

        np.save('coba_low.npy', lower)
        np.save('coba2_high.npy', upper)

        contour,_ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contour:
            largest_contour = max(contour, key =cv2.contourArea)

            x,y,w,h =cv2.boundingRect(largest_contour)
            cv2.rectangle(frame,(x, y), (w+x, h+y), (255,0,0),2)
            cv2.putText(frame,"blue",(x+(w//2)-10, y+(h//2)-10),cv2.FONT_HERSHEY_COMPLEX, 0.7 , (0,0,0), 2 )

        # cv2.imshow("hsv", hsv)
        cv2.imshow("thresh", thresh)
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    init_trackbars()
<<<<<<< HEAD
    camera = cv2.VideoCapture(5)
    main(camera)
=======
    camera = cv2.VideoCapture(1)
    main(camera)
>>>>>>> 851f70dfa5b9faaf82749c57b889f95ba3e86ddd
