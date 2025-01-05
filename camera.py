import cv2

def initialize_camera():
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    return cam

def release_camera(cam):
    cam.release()
    cv2.destroyAllWindows()
