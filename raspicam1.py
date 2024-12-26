import cv2

def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("kamera gagal")
        return

    while True:
        ret, frame = camera.read()
        if not ret:
            print("frame gagal")
            break

        cv2.imshow("ini frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
