from cast_common.logger import Logger
from json import dump
from oneclick.config import Config
from os.path import abspath

class SourceValidation:
    _log=None

    def __init__(cls,config:Config,log_name:str,log_level:int):
        if SourceValidation._log is None:
            SourceValidation._log = Logger(name=log_name,level=log_level,file_name=config.log_filename)
            SourceValidation._log_level=log_level
        pass

    @property
    def log(cls):
        return SourceValidation._log

    @property
    def required(cls):
        return True
    
    def get_title(cls) -> str:
        return cls.__class__.__name__

