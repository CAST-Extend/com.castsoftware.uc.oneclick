from cast_common.logger import Logger,INFO
from oneclick.config import Config
from cast_common.util import run_process
from subprocess import Popen


class Analysis():

    _pid = []

    def __init__(cls,log_name:str,log_level:int):
        cls._log = Logger(log_name,log_level)
        pass

    @property
    def log(cls):
        return cls._log

    def track_process(cls,process:Popen,operation:str,name:str):
        cls._pid.append(Process(process,operation,name))
        pass

    def check_process(cls,pid:int)->Popen:
        info = cls._pid[str(pid)]
        process = info['process']
        return process.poll()
    
    def get_title(cls) -> str:
        return cls.__class__.__name__


class Process():
    def __init__(cls,process:Popen,operation:str,name:str):
        cls._process = process
        cls._operation = operation
        cls._name = name
        cls._status = None
        cls._log = []

    @property
    def process(cls):
        return cls._process

    @property
    def operation(cls):
        return cls._operation

    @property
    def name(cls):
        return cls._name

    @property
    def status(cls):
        return cls._status
    @status.setter
    def status(cls,value):
        cls._status = value

    @property
    def log(cls):
        return cls._log
