from logger import Logger
from logging import DEBUG, INFO, WARN, ERROR
from config import Config
from argConfig import ARGConfig
from convert import GeneratePPT 
from util import create_folder
from json import dump
from os.path import abspath

from subprocess import call

class RunARG():
    def __init__(cls,config:Config, log_level:int=INFO,log_name:str=None):
        if log_name is None:
            log_name = cls.__class__.__name__
            
        cls._log = Logger(log_name,log_level)
        cls._config = config
        pass

    def run(cls,config:Config,appl_name:str=None,operation:str=None) -> bool:
        if appl_name is None:
            appl_name = 'FULL'
        
        cfg = {}
        cfg['company']=config.company_name
        cfg['project']=config.project['name']
        cfg['template']=abspath(config.arg_template)
        cfg['output']=abspath(f'{config.output}/REPORT/{appl_name}')
        cfg['cause']=abspath(f'{config.base}/scripts/cause.json')

        application=[]
        if appl_name == 'FULL':
            for appl in config.application:
                application.append({"aip":appl,"highlight":appl,"title":appl})
        else: 
            application.append({"aip":appl_name,"highlight":appl_name,"title":appl_name})
        cfg['application']=application

        cfg['rest'] = config.rest

        create_folder(f'{config.work}/arg')
        create_folder(cfg['output'])

        arg_cfg_file = f'{config.output}/REPORT/{appl_name}/config.json'
        with open(arg_cfg_file, "w") as f:
            dump(cfg,f,indent=4)
            f.close()

        GeneratePPT(ARGConfig(arg_cfg_file)).save_ppt()
        pass

class  RunARGAIP(RunARG):
    def __init__(cls, config:Config, log_level:int) -> None:
        super().__init__(config,log_level,cls.__class__.__name__)

    def run(cls,appl_name:str) -> None:
        super().run(cls._config,appl_name,'AIP')

