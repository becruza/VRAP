import cv2
import pytz
import os
import sys
import time
import glob
from datetime import datetime, timedelta
from zipfile import ZipFile

timezone = pytz.timezone('America/Bogota')
fmt = '%Y-%m-%d_%H:%M:%S'
invoke_time = datetime.now().astimezone(timezone)
channel = int(sys.argv[1])


def capture(url, sample_time=300):
    start_time = invoke_time.strftime(fmt)
    end_time = (invoke_time + timedelta(hours=1)).strftime(fmt)
    folder_name = f'{start_time}_{end_time}'
    print(folder_name)
    os.system(f'mkdir {folder_name}')
    os.chdir(f'./{folder_name}')
    cap = cv2.VideoCapture(url)
    time.sleep(channel)
    start_time = datetime.now()
    current_time = start_time
    while True:
        ret, frame = cap.read()
        # cv2.imshow('frame', frame)
        if not ret:
            break
        if datetime.now() >= current_time + timedelta(seconds=sample_time):
            current_time = datetime.now()
            img_name = f"{channel}->{current_time.astimezone(timezone).strftime(fmt)}.jpg"
            cv2.imwrite(img_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # elif datetime.now() >= start_time + timedelta(hours=1):
        #     break
        elif datetime.now() >= start_time + timedelta(seconds=5):
            break

    cap.release()
    cv2.destroyAllWindows()

    return folder_name


def zipper(files, folder_name):
    if files is None:
        print('No files to zip')
    else:
        part = 1
        while len(files) > 0:
            with ZipFile(f'{folder_name}_{part}.zip', 'w') as zip_obj:
                # Add multiple files to the zip
                total_size = 0
                for file in files:
                    if total_size >= 2000000:
                        break
                    zip_obj.write(file)
                    total_size += os.path.getsize(file)
                    files.pop(0)

            part += 1


# def upload():


if __name__ == '__main__':
    os.system(f'mkdir images/{channel}')
    os.chdir(f'./images/{channel}')
    # url = 'rtsp://admin:vaico2020@192.168.1.117:554/Streaming/Channels/101'
    url = '/home/vaico/Downloads/mp4/NVR_ch2_main_20200309080000_20200309090000.mp4'
    folder_name = capture(url, sample_time=1)
    # folder_name = '2020-03-11_16:36:08_2020-03-11_17:36:08'
    # os.chdir(f'./{folder_name}')
    # print(os.getcwd())
    # files = glob.glob(f'{os.getcwd()}/*.jpg')
    # files = os.listdir(os.getcwd())
    files = glob.glob('*.jpg')
    zipper(files, folder_name)
