import cv2
import pytz
import os
import sys
import time
import glob
import requests
from datetime import datetime, timedelta
from zipfile import ZipFile

bucket_url = 'https://j8wmps8gr0.execute-api.us-east-2.amazonaws.com/testing/upload'
timezone = pytz.timezone('America/Bogota')
fmt = '%Y-%m-%d_%H:%M:%S'
invoke_time = datetime.now().astimezone(timezone)
channel = int(sys.argv[1]) if len(sys.argv) > 1 else 0
mac = '00:11:22:AA:BB:CC'
root_dir = os.getcwd()


def capture(url, sample_time=300, ):
    print('recording')
    start_time = invoke_time.strftime(fmt)
    end_time = (invoke_time + timedelta(hours=1)).strftime(fmt)
    folder_name = f'{start_time}_{end_time}'
    os.makedirs(folder_name, exist_ok=True)
    os.chdir(f'./{folder_name}')
    cap = cv2.VideoCapture(url)
    # time.sleep(channel)
    start_time = datetime.now()
    current_time = start_time

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if datetime.now() >= current_time + timedelta(seconds=sample_time):
            current_time = datetime.now()
            img_name = f"channel{channel}_{current_time.astimezone(timezone).strftime(fmt)}.jpg"
            cv2.imwrite(img_name, frame)

        if datetime.now() >= start_time + timedelta(seconds=20):
            break

    cap.release()
    cv2.destroyAllWindows()
    return folder_name


def zipper(files, folder_name):
    if len(files) > 0:
        part = 1
        total_size = 0
        zip_file = ZipFile(f'{folder_name}_{part}.zip', 'w')
        for file in files:
            zip_file.write(file)
            total_size += os.path.getsize(file)
            if total_size >= 2000000:
                total_size = 0
                zip_file.close()
                part += 1
                zip_file = ZipFile(f'{folder_name}_{part}.zip', 'w')
                continue
        # for file in files:
        #     os.remove(file)
    else:
        print('No files to zip')


def upload(files, mac):
    for file in files:
        response = requests.get(f'{bucket_url}?name={file}&observer={mac}')
        signed_url = response.text
        print(f'uploading {file}')
        with open(file, "rb") as data:
            up = requests.put(signed_url.replace('/us-east-2/', '/us-east-1/'), data=data)

        if 200 <= up.status_code < 300:
            os.remove(file)
            print(f'{file} uploaded...')

        # f = open(file, 'rb')
        # data = f.read()
        # up = requests.put(signed_url.replace('/us-east-2/', '/us-east-1/'), data=data)


if __name__ == '__main__':
    img_dir = f'images/channel{channel}'
    full_path = os.path.join(root_dir, img_dir)
    os.makedirs(full_path, exist_ok=True)
    os.chdir(full_path)
    # url = 'rtsp://admin:vaico2020@192.168.1.117:554/Streaming/Channels/101'
    # url = '/home/becruza/Downloads/NVR_ch3_main_20200306150000_20200306160000.mp4'
    url = 'rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov'
    folder_name = capture(url, sample_time=1)
    files = glob.glob('*.jpg')
    zipper(files, folder_name)
    # print('Uploading...')
    # files = glob.glob('*.zip')
    # upload(files, mac)
