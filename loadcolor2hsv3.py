import cv2
import numpy as np

def main(cam):
    # Ukuran crop
    lebar_crop = 640 
    tinggi_crop = 480

    while True:
        ret, frame = cam.read()  # Membaca frame dari kamera
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

        # Konversi frame yang di-crop ke HSV
        hsv = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
        
        # Memuat batas bawah dan atas warna dari file
        green_low = np.load('/home/mikom/tubes-mikom/hsvgreen_low.npy')
        green_high = np.load('/home/mikom/tubes-mikom/hsvgreen_high.npy')
        red_low = np.load('/home/mikom/tubes-mikom/hsvred_low.npy')
        red_high = np.load('/home/mikom/tubes-mikom/hsvred_high.npy')
        blue_low = np.load('/home/mikom/tubes-mikom/hsvblue_low.npy')
        blue_high = np.load('/home/mikom/tubes-mikom/hsvblue_high.npy')

        # Warna-warna yang akan dideteksi
        colors = {
            "Green": (green_low, green_high),
            "Red": (red_low, red_high),
            "Blue": (blue_low, blue_high)
        }

        for color_name, (low, high) in colors.items():
            thresh = cv2.inRange(hsv, low, high)  # Membuat mask berdasarkan rentang warna
            
            # Membuat kernel berbentuk elips dengan ukuran 5x5 untuk morfologi
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            
            # Melakukan operasi morfologi (open) untuk menghilangkan noise
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Menemukan kontur pada gambar biner
            contour, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contour:  # Mengecek apakah ada kontur yang ditemukan
                largest_contour = max(contour, key=cv2.contourArea)  # Memilih kontur terbesar berdasarkan area

                # Membuat kotak pembatas (bounding box) di sekitar kontur terbesar
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(cropped_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Menggambar kotak di frame

                # Menambahkan teks di tengah kotak pembatas
                cv2.putText(cropped_frame, color_name, (x + w // 2, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Menampilkan hasil deteksi dalam beberapa jendela
        cv2.imshow('cropped_frame', cropped_frame)  # Menampilkan frame yang di-crop dengan kotak pembatas
        
        # Menunggu tombol 'q' untuk keluar dari program
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

# Entry point dari program
if __name__ == '__main__':
    cam = cv2.VideoCapture(0,cv2.CAP_V4L2)  # Membuka kamera default (index 0)
    main(cam)  # Memanggil fungsi utama
