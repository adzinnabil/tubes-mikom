import cv2


cap = cv2.VideoCapture(0) 
while True:
    ret, frame = cap.read()
    if not ret:
        break
    x_start = 760
    y_start = 240
    x_end = 1160
    y_end = 600

    cropped_frame = frame[y_start:y_end, x_start:x_end]

    cv2.imshow('frame crop', cropped_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
