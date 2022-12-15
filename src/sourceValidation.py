from logger import Logger
from json import dump

class SourceValidation:

    def __init__(cls,log_name:str,log_level:int):
        cls._log = Logger(log_name,log_level)
        pass

    @property
    def required(cls):
        return True

