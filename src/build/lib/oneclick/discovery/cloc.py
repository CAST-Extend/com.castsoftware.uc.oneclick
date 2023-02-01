from oneclick.config import Config
from cast_common.logger import Logger,INFO
from cast_common.util import run_process,format_table,check_process,create_folder
from oneclick.discovery.sourceValidation import SourceValidation 

from os import getcwd
from os.path import exists,abspath
from re import findall
from pandas import DataFrame,ExcelWriter


#TODO: Convert total line to formulas (d1-SHP)
#TODO: Format all numbers as integers not text (d1-SHP)
#TODO: Group tabs in pairs (before, after) then by application (d2)

class ClocPreCleanup(SourceValidation):
    writer = None
    
    def __init__(cls, config: Config, log_level:int=INFO, name = None):
        if name is None: 
            name = cls.__class__.__name__

        super().__init__(config,cls.__class__.__name__,log_level)

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
        return f'{cls.cloc_base}\\{cls.config.project_name}'

    @property
    def cloc_results(cls):
        return cls._df

    def _run_cloc(cls,cloc_project:str,work_folder:str,cloc_output:str):
        cloc_path=abspath(f'{getcwd()}\\scripts\\cloc-1.64.exe')
        args = [cloc_path,work_folder,"--report-file",cloc_output,"--quiet"]
        return run_process(args,False)

    def open_excel_writer(cls,config:Config):
        ClocPreCleanup.writer = ExcelWriter(abspath(f'{config.report}/{config.project_name}/{config.project_name}-cloc.xlsx'), engine='xlsxwriter')

    def run(cls,config:Config):
        cls.open_excel_writer(config)

        list_of_tech_file=abspath(f'{getcwd()}\\scripts\\ListOfTechnologies.csv')
        with open(list_of_tech_file) as f:
            tech_list = f.read().splitlines()
            f.close()

        process = {}
        for appl in config.application:
            cls._log.info(f'Running {config.project_name}/{appl}')
            cloc_output = abspath(f'{config.report}/{config.project_name}/{appl}-cloc-{cls.phase}.txt')
            work_folder = abspath(f'{config.work}/{appl}/AIP')

            #if the report is already out there - no need to continue
            if exists(cloc_output):
                process[appl]=None
                continue 

            process[appl] = cls._run_cloc(cls.cloc_project,work_folder,cloc_output)

        #has all cloc processing completed
        for p in process:
            cloc_output = abspath(f'{config.report}/{config.project_name}/{p}-cloc-{cls.phase}.txt')
            if not process[p] is None:
                cls._log.info(f'Checking results for {config.project_name}\{p}')
                ret,output = check_process(process[p],False)
                if ret != 0:
                    raise RuntimeError(f'Error running cloc on {cloc_output}')

            #reading cloc_output.txt file
            cls._log.info(f'Processing {cloc_output}')
            summary_list=[]   
            with open(cloc_output, 'r') as f:
                content = f.read()
                f.seek(0)
                summary_list= [line.rstrip('\n').lstrip() for line in f]
                #print(summary_list)
                f.close()

            #extracting required data from content of cloc_output.txt using python regex
            pattern='(\S{1,}|\w{1,}[:])\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
            statistics_list=findall(pattern,content)
            df = DataFrame(statistics_list,columns=['LANGUAGE','FILES','BLANK','COMMENT','CODE'])
            df['APPLICABLE']=df['LANGUAGE'].isin(tech_list)

            #converting column values into int from string
            df['FILES'] = df['FILES'].astype('int')
            df['BLANK'] = df['BLANK'].astype('int')
            df['COMMENT'] = df['COMMENT'].astype('int')
            df['CODE'] = df['CODE'].astype('int')

            format_table(ClocPreCleanup.writer,df,f'{cls.phase}-Cleanup({p})')
        return True



class ClocPostCleanup(ClocPreCleanup):

    def __init__(cls, config: Config, log_level:int=INFO, name = None):
        super().__init__(config,log_level,cls.__class__.__name__)

    def open_excel_writer(cls,config:Config):
        pass
    
    @property
    def phase(cls):
        return 'After'

    def run(cls,config:Config):
        super().run(config)
        ClocPreCleanup.writer.close()
