from cast_common.logger import Logger
from json import dump
from oneclick.config import Config
from os.path import abspath

class SourceValidation:

    def __init__(cls,config:Config,log_name:str,log_level:int):
#        log_file = abspath(f'{config.oneclick_work}/{config.project_name}/LOGS/source-code-discovery.log')       
        cls._log = Logger(name=log_name,level=log_level,file_name=config.log_filename)
        pass

    @property
    def required(cls):
        return True

