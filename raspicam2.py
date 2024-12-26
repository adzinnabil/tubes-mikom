import cv2
import numpy as np
import picamera
import picamera.array

def main():
    with picamera.PiCamera() as camera:
        camera.resolution = (640,480)
        
        with picamera.array.PiRGBArray(camera) as output:
            while True:
                camera.capture(output, 'bgr', use_video_port=True)
                frame = output.array
                cv2.imshow("ini frame", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                output.truncate(0)  

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
