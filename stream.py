import cv2
from datetime import datetime, timedelta
import pytz
import os
import sys


os.chdir('./images/')
cap = cv2.VideoCapture('rtsp://admin:vaico2020@192.168.1.117:554/Streaming/Channels/101')
timezone = pytz.timezone('America/Bogota')
fmt = '%Y-%m-%d %H:%M:%S'
start_time = datetime.now()
current_time = start_time
while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if datetime.now() >= current_time + timedelta(seconds=1):
        current_time = datetime.now()
        img_name = f"{sys.argv[1]}-->{current_time.astimezone(timezone).strftime(fmt)}.png"
        cv2.imwrite(img_name, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    elif datetime.now() >= start_time + timedelta(seconds=10):
        break

cap.release()
cv2.destroyAllWindows()