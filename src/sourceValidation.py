from logger import Logger


class SourceValidation:

    def __init__(cls,log_name:str,log_level:int):
        cls._log = Logger(log_name,log_level)
        pass

