import os
import tempfile
import glob
from pathlib import Path
from shutil import copy
import sys
import time

root_dir = os.getcwd()
repo = 'https://github.com/becruza/Testing'
# pid = sys.argv[1]

if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as tmp:
        os.system(f'git clone {repo} {tmp}')
        requeriments = f'{tmp}/requirements.txt'
        req = Path(requeriments)
        if req.exists():
            os.system(f'pip install -r {requeriments}')
        files = glob.glob(f'{tmp}/*')
        for file in files:
            copy(file, f'{root_dir}')
