from os import mkdir
from os.path import exists,abspath,join
from subprocess import Popen,PIPE,CalledProcessError

import sys



def resource_path(relative_path):
    "get the absolute path to resource, works for dev and for PyInstaller"
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath('.')
    return join(base_path, relative_path)

def create_folder(folder):
    if not exists(folder):
        mkdir(folder)

def run_process(args):
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        print(line)
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += str(stdout).split('\n')
    if stderr != b'':
        ret += str(stderr).split('\n')
    return ret
