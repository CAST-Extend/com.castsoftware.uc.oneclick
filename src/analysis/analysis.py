from logger import Logger
from subprocess import Popen,PIPE

class Analysis:
    def __init__(cls,log_name:str,log_level:int):
        cls._log = Logger(log_name,log_level)
        pass

    def jarWrapper(cls,args):
        cmd = ['java', '-jar'] + args

        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
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

