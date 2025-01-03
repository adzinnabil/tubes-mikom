import cv2
import numpy as np

def callback():
    pass

def init_trackbars():
    """
    Membuat trackbars untuk mengatur batas bawah dan atas warna BGR.
    """
    cv2.namedWindow("bgr Trackbars")
    cv2.createTrackbar('LB', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('LG', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('LR', 'bgr Trackbars', 0, 255, callback)
    cv2.createTrackbar('UB', 'bgr Trackbars', 255, 255, callback)
    cv2.createTrackbar('UG', 'bgr Trackbars', 255, 255, callback)
    cv2.createTrackbar('UR', 'bgr Trackbars', 255, 255, callback)

def get_lower_bgr():
    """
    Mengambil nilai batas bawah warna BGR dari trackbars.
    """
    lower_blue = cv2.getTrackbarPos('LB', 'bgr Trackbars')
    lower_green = cv2.getTrackbarPos('LG', 'bgr Trackbars')
    lower_red = cv2.getTrackbarPos('LR', 'bgr Trackbars')
    return lower_blue, lower_green, lower_red

def get_upper_bgr():
    """
    Mengambil nilai batas atas warna BGR dari trackbars.
    """
    upper_blue = cv2.getTrackbarPos('UB', 'bgr Trackbars')
    upper_green = cv2.getTrackbarPos('UG', 'bgr Trackbars')
    upper_red = cv2.getTrackbarPos('UR', 'bgr Trackbars')
    return upper_blue, upper_green, upper_red

def main():
    # Inisialisasi kamera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camera.isOpened():
        print("Kamera gagal")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Frame gagal")
            break

        # Mendapatkan ukuran asli frame
        height, width, _ = frame.shape

        # Menghitung koordinat crop agar berada di tengah
        crop_width = 240
        crop_height = 240
        start_x = (width - crop_width) // 2
        start_y = (height - crop_height) // 2
        end_x = start_x + crop_width
        end_y = start_y + crop_height

        # Crop frame ke 240x240
        cropped_frame = frame[start_y:end_y, start_x:end_x]

        # Ambil batas bawah dan atas warna BGR dari trackbars
        low = get_lower_bgr()
        high = get_upper_bgr()

        # Threshold frame yang sudah di-crop
        thresh = cv2.inRange(cropped_frame, low, high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Menyimpan batas bawah dan atas warna ke file .npy
        lower = np.array([low])
        upper = np.array([high])
        np.save('red_low.npy', lower)
        np.save('red_high.npy', upper)

        # Menampilkan hasil crop dan threshold
        cv2.imshow("Cropped Frame", cropped_frame)
        cv2.imshow("Thresholded Frame", thresh)

        # Keluar dengan menekan 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    init_trackbars()
    main()
