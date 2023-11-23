import cv2

# Open the default camera (0 represents the default camera)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Get and print default camera parameters
frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
brightness = cap.get(cv2.CAP_PROP_BRIGHTNESS)
contrast = cap.get(cv2.CAP_PROP_CONTRAST)
saturation = cap.get(cv2.CAP_PROP_SATURATION)
exposure = cap.get(cv2.CAP_PROP_EXPOSURE)

print(f"Default Frame Width: {frame_width}")
print(f"Default Frame Height: {frame_height}")
print(f"Default Brightness: {brightness}")
print(f"Default Contrast: {contrast}")
print(f"Default Saturation: {saturation}")
print(f"Default Exposure: {exposure}")

# Release the camera
cap.release()