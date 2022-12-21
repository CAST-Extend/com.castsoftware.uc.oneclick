from config import Config
from logger import Logger
from logger import INFO
from sourceValidation import SourceValidation 

from os import getcwd
from re import findall
from pandas import DataFrame

from util import run_process,create_folder,format_table



class ClocPreCleanup(SourceValidation):
    def __init__(cls, config: Config, log_level:int=INFO, name = None):
        if name is None: 
            name = cls.__class__.__name__
        super().__init__(cls.__class__.__name__,log_level)
        cls.config = config
        cls._df = {}
        pass

    @property
    def phase(cls):
        return 'Before'

    @property
    def cloc_base(cls):
        return f'{cls.config.base}\\cloc' 
    @property
    def cloc_project(cls):
        return f'{cls.cloc_base}\\{cls.config.project}'

    @property
    def cloc_results(cls):
        return cls._df

    def _run_cloc(cls,cloc_project:str,work_folder:str,cloc_output:str):
        cloc_path=f'{getcwd()}\\scripts\\cloc-1.64.exe'
        args = [cloc_path,work_folder,"--report-file",cloc_output]
        return run_process(args)

    def run(cls,config:Config):
        create_folder(cls.cloc_base)
        create_folder(cls.cloc_project)

        list_of_tech_file=f'{getcwd()}\\scripts\\ListOfTechnologies.csv'
        with open(list_of_tech_file) as f:
            tech_list = f.read().splitlines()
            f.close()

        for appl in config.application:
            cls._log.info(f'Running {cls.phase} cloc for {config.project}\{appl}')
            cloc_output = f'{cls.cloc_project}\\cloc_{appl}_{cls.phase}.txt'
            work_folder = f'{config.base}\\work\\{config.project}\\{appl}\AIP'  

            ret,output = cls._run_cloc(cls.cloc_project,work_folder,cloc_output)
            if ret != 0:
                raise RuntimeError(f'Error running cloc on {work_folder}')

            #reading cloc_output.txt file
            summary_list=[]   
            with open(cloc_output, 'r') as f:
                content = f.read()
                f.seek(0)
                summary_list= [line.rstrip('\n').lstrip() for line in f]
                #print(summary_list)

            #extracting required data from content of cloc_output.txt using python regex
            pattern='(\S{1,}|\w{1,}[:])\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
            statistics_list=findall(pattern,content)
            df = DataFrame(statistics_list,columns=['LANGUAGE','FILES','BLANK','COMMENT','CODE'])
            df['APPLICABLE']=df['LANGUAGE'].isin(tech_list)
            cls._df[appl]=df
            
        return True

    def format_table(cls,writer):
        for key in cls.cloc_results:
            format_table(writer,cls.cloc_results[key],f'{cls.phase}-Cleanup({key})')

    def save_xlsx(cls,writer):
        pass




class ClocPostCleanup(ClocPreCleanup):

    def __init__(cls, config: Config, log_level:int=INFO, name = None):
        super().__init__(config,log_level,cls.__class__.__name__)

    @property
    def phase(cls):
        return 'After'
    
    def save_xlsx(cls,writer):
        writer.close()

