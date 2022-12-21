from sourceValidation import SourceValidation
from logger import INFO
from config import Config
from util import run_process

class aipAnalysis(SourceValidation):

    def __init__(cls, name = None, log_level:int=INFO):
        if name is None: 
            name = cls.__class__.__name__
        super().__init__(cls.__class__.__name__,log_level)
    
    def run(cls, config:Config):
        for appl in config.application:
            #add a new appication in AIP Console
            cls._log.info(f'Creating new application {config.project}\{appl}')
            aip_work_folder = f'{config.base}\\work\\{config.project}\\{appl}'
            
            args = [f'{config.java_home}\\bin\\java.exe',
                    '-jar',config.aip_cli,
                    'new',
                    '-n',f'{appl}',
                    '-s',config.aip_url,
                    '--apikey=',config.aip_key,
                    '--verbose=' , 'false',
                    '--no-version-history=' , 'false'
                    ]
            status,output = run_process(args)        
            if status != 0:
                raise RuntimeError ("")

            #Run Analysis
            cls._log.info(f'Running AIP analysis for {config.project}\{appl}')
            aip_work_folder = f'{config.base}\\work\\{config.project}\\{appl}'
            
            args = [f'{config.java_home}\\bin\\java.exe',
                    '-jar',config.aip_cli,
                    'add',
                    '--apikey=',config.aip_key,
                    '-n',f'{appl}',
                    '-f', f'{aip_work_folder}\\AIP',
                    '-s',config.aip_url,
                    '--verbose' , 'false'
                    ]
            status,output = run_process(args)        
            if status != 0:
                raise RuntimeError ("")