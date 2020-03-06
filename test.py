import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == '__main__':
    # print()
    logger.info('Start')
    seconds = 5
    time.sleep(seconds)
    logger.info(f'{seconds} Seconds after...')
