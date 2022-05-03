#File to test the image that is processed
from utils import *
import numpy as np
import cv2 as cv

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

fourcc = cv.VideoWriter_fourcc(*'MJPG')
out = cv.VideoWriter('output.avi', fourcc, 20.0, (640,  480))

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    out.write(frame)

    print("working")

    if cv.waitKey(1) == ord('q'):
        break

# When everything done, release the capture
cap.release()
out.release()
cv.destroyAllWindows()