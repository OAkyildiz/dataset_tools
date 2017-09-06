import numpy as np
import cv2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()
file = args.file

if not file:
    file=1

cap = cv2.VideoCapture(file)
#'vtest.avi'
while(cap.isOpened()):
    ret, frame = cap.read()

    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
