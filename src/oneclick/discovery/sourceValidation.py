from logger import Logger
from json import dump
from config import Config
from os.path import abspath

class SourceValidation:

    def __init__(cls,config:Config,log_name:str,log_level:int):
        log_file = abspath(f'{config.logs}/{config.project_name}/source-code-discovery.log')
        cls._log = Logger(name=log_name,level=log_level,file_name=log_file)
        pass

    @property
    def required(cls):
        return True

