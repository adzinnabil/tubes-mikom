from picamera2 import Picamera2
import cv2

# Initialize the Picamera2 instance
camera = Picamera2()

# Configure the camera
camera.configure(camera.create_preview_configuration())

# Start the camera
camera.start()

# Open a preview window
print("Press 'q' to quit the preview.")
while True:
    # Capture an image as a NumPy array
    frame = camera.capture_array()

    # Display the frame using OpenCV
    cv2.imshow("Raspberry Pi Camera Preview", frame)

    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the camera
camera.stop()

# Close all OpenCV windows
cv2.destroyAllWindows()
