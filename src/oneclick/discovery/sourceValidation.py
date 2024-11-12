from oneclick.base import Base
from cast_common.logger import Logger
from json import dump
from oneclick.config import Config
from os.path import abspath

class SourceValidation(Base):
    _log=None

    def __init__(cls):
        # if SourceValidation._log is None:
        #     SourceValidation._log = Logger(name=log_name,level=log_level,file_name=config.log_filename)
        #     SourceValidation._log_level=log_level
        pass

    @property
    def required(cls):
        return True
    
    def get_title(cls) -> str:
        return cls.__class__.__name__

