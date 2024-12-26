import cv2

camera_index = 1
cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Webcam tidak dapat diakses!")
    exit()

print("Tekan 'q' untuk keluar.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Gagal membaca frame!")
        break

    cv2.imshow("Webcam Preview", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
