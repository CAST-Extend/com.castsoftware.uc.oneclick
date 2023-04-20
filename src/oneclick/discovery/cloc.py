from oneclick.config import Config
from cast_common.logger import Logger,INFO
from cast_common.util import run_process,check_process,format_table,create_folder
from oneclick.discovery.sourceValidation import SourceValidation 
from time import sleep

from os import getcwd
from os.path import exists,abspath,getsize
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

    def _run_cloc(cls,work_folder:str,cloc_output:str,cloc_output_ignored:str):
        cloc_path=abspath(f'{getcwd()}\\scripts\\{cls.config.cloc_version}')
        args = [cloc_path,work_folder,"--report-file",cloc_output,"--ignored",cloc_output_ignored,"--quiet"]
        proc = run_process(args,False)

        sleep(10)
        if proc.poll() is not None and exists(cloc_output):
            return 'DONE'
        else:
            return proc

    def open_excel_writer(cls,config:Config):
        ClocPreCleanup.writer = ExcelWriter(abspath(f'{config.report}/{config.project_name}/{config.project_name}-cloc.xlsx'), engine='xlsxwriter')

    def run(cls,config:Config):
        cls.open_excel_writer(config)

        list_of_tech_file=abspath(f'{getcwd()}\\scripts\\ListOfTechnologies.csv')
        with open(list_of_tech_file) as f:
            tech_list = f.read().splitlines()
            f.close()

        process = {}
        cloc_run=False
        for appl in config.application:
            cls._log.info(f'Running {config.project_name}/{appl}')
            create_folder(f'{config.report}/{config.project_name}/{appl}')
            cloc_output = abspath(f'{config.report}/{config.project_name}/{appl}/{appl}-cloc-{cls.phase}.txt')
            cloc_output_ignored = abspath(f'{config.report}/{config.project_name}/{appl}/{appl}-cloc-ignored-{cls.phase}.txt')
            work_folder = abspath(f'{config.work}/AIP/{config.project_name}/{appl}')

            #if the report is already out there - no need to continue
            if exists(cloc_output):
                process[appl]=None
                continue 
            cloc_run=True
            process[appl] = cls._run_cloc(work_folder,cloc_output,cloc_output_ignored)

        #has all cloc processing completed
        all_done=False
        while (not all_done):
            all_done=True
            for p in process:
                if process[p]=='DONE':
                    continue
                all_done=False
                cloc_output = abspath(f'{config.report}/{config.project_name}/{p}/{p}-cloc-{cls.phase}.txt')
                cloc_output_ignored = abspath(f'{config.report}/{config.project_name}/{p}/{p}-cloc-ignored-{cls.phase}.txt')
                if not process[p] is None:
                    cls._log.info(f'Checking results for {config.project_name}/{p}')
                    try:
                        ret,output = check_process(process[p],False)
                        if ret != 0 and not exists(cloc_output) and getsize(cloc_output) == 0:
                            cls._log.error(f'Error running cloc on {cloc_output} ({ret})')
                    except IOError:
                        if not exists(cloc_output) and getsize(cloc_output) == 0:
                            cls._log.error(f'Error running cloc on {cloc_output} ({ret})')

                if exists(cloc_output):
                    process[p]='DONE'
            if cloc_run:
                sleep(60)

        for appl in config.application:
            #reading cloc_output.txt file
            cloc_output = abspath(f'{config.report}/{config.project_name}/{appl}/{appl}-cloc-{cls.phase}.txt')
            cloc_output_ignored = abspath(f'{config.report}/{config.project_name}/{appl}/{appl}-cloc-ignored-{cls.phase}.txt') 
            cls._log.info(f'Processing {cloc_output}')
            summary_list=[]   
            with open(cloc_output, 'r') as f:
                content = f.read()
                f.seek(0)
                summary_list= [line.rstrip('\n').lstrip() for line in f]
                #print(summary_list)

            #extracting required data from content of cloc_output.txt using python regex
            pattern='(\S{1,}|\w{1,}[:])\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
            statistics_list=findall(pattern,content)
            statistics_list= statistics_list[:-1]
            
            with open(cloc_output_ignored, 'r') as fp:
                lines = len(fp.readlines())
            statistics_list.append(('Unknown Files',lines,'0','0','0'))

            df = DataFrame(statistics_list,columns=['LANGUAGE','FILES','BLANK','COMMENT','CODE'])

            #making technolgy check as case sensitive
            def all_lower(my_list):
                return list(map(lambda x: x.lower(), my_list))
            tech_list = all_lower(tech_list)
            df['APPLICABLE']=df['LANGUAGE'].str.lower().isin(tech_list)

            #converting column values into int from string
            df['FILES'] = df['FILES'].astype('int')
            df['BLANK'] = df['BLANK'].astype('int')
            df['COMMENT'] = df['COMMENT'].astype('int')
            df['CODE'] = df['CODE'].astype('int')

            #converting total line to formulas
            # total_files='=SUBTOTAL(109,[FILES])'
            # total_blank='=SUBTOTAL(109,[BLANK])'
            # total_comment='=SUBTOTAL(109,[COMMENT])'
            # total_code='=SUBTOTAL(9,E2:E'+str(len(df['FILES'])+1)+')'
            
            #converting total line to formulas
#            df.loc[len(df.index)] = [' ', total_files, total_blank, total_comment, total_code, ' ']

            format_table(ClocPreCleanup.writer,df,f'{cls.phase}({appl})')
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
        pass



        