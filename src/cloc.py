from sourceValidation import SourceValidation 
from os import mkdir,getcwd,remove
from os.path import dirname,exists
from config import Config
from pandas import DataFrame
from re import findall
from xlwt import Workbook,easyxf
from subprocess import Popen,PIPE

class ClocPreCleanup(SourceValidation):
    def __init__(cls,workbook:Workbook,log_level:int):
        super().__init__(cls.__class__.__name__,log_level)

        cls._workbook = workbook

        pass


    @property
    def phase(cls):
        return 'Before'

    def run(cls,config:Config):
        cloc_base = f'{config.base}\\cloc'    
        if not exists(cloc_base):
            mkdir(cloc_base)

        cloc_project = f'{cloc_base}\\{config.project}'
        if not exists(cloc_project):
            mkdir(cloc_project)

        dir = getcwd()
        cloc_path=f'{dir}\\scripts\\cloc-1.64.exe'
        list_of_tech_file=f'{dir}\\scripts\\ListOfTechnologies.csv'

        cls._workbook_name = f'{cloc_project}\\cloc_{config.project}.xls'

        for appl in config.application:
            cls._log.info(f'Running {cls.phase} cloc for {config.project}\{appl}')
            cloc_output = f'{cloc_project}\\cloc_{appl}_{cls.phase}.txt'
            work_folder = f'{config.base}\\work\\{config.project}\\{appl}'  

            p = Popen([cloc_path,work_folder,"--quiet","--report-file",cloc_output], shell=True, stdout = PIPE)
            stdout, stderr = p.communicate()

            #reading cloc_output.txt file
            summary_list=[]   
            with open(cloc_output, 'r') as f:
                content = f.read()
                f.seek(0)
                summary_list= [line.rstrip('\n').lstrip() for line in f]
                #print(summary_list)

            su_list=[]
            for i in summary_list:
                if i.__contains__('http'):
                    break
                else:
                    su_list.append(i)
            #print(su_list)

            #extracting required data from content of cloc_output.txt using python regex
            pattern='(\S{1,}|\w{1,}[:])\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
            statistics_list=findall(pattern,content)
            statistics_list.insert(0,('LANGUAGE','FILES','BLANK','COMMENT','CODE','APPLICABLE'))

            for i in range(len(statistics_list)):
                statistics_list[i]=list(statistics_list[i])   

            #extracting supported technologies from ListOfTechnologies.csv file into sup_tech list
            sup_tech = []
            with open(list_of_tech_file, 'r') as f:   
                sup_tech = f.readlines()
                sup_tech = [line.rstrip(',YES\n').lower() for line in sup_tech if line.__contains__(',YES') ]
                f.close()

            #if technology present in sup_tech list then mark it as YES otherwise Mark is as NO
            for i in range(1,len(statistics_list)-1):
                if statistics_list[i][0].lower() in sup_tech:
                    statistics_list[i].append('YES')
                else:
                    statistics_list[i].append('NO')

            su_sheet = cls._workbook.add_sheet(f'{appl}-Summary-{cls.phase}-Cleanup')
            su_list.insert(0,f'Cloc Summary {cls.phase} CleanUP')
            #write value into excel sheet one by one
            style = easyxf('pattern: pattern solid, fore_colour light_green;'
                              'font: colour black, bold True;')
            for i in range(len(su_list)):
                if i==0:
                    su_sheet.write(i, 0, su_list[i],style) 
                else:
                    su_sheet.write(i, 0, su_list[i])
            
            sheet = cls._workbook.add_sheet(f'{appl}-Stats-{cls.phase}-Cleanup')
            #write value into excel sheet one by one
            for i in range(len(statistics_list)):
                for j in range(len(statistics_list[i])):
                    if i==0:
                        sheet.write(i, j, statistics_list[i][j],style)
                    else:
                        sheet.write(i, j, statistics_list[i][j])
            pass

        cls.save_workbook()

        pass

    # def save_workbook(cls):
    #     pass

    def save_workbook(cls):
        pass


class ClocPostCleanup(ClocPreCleanup):
    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    @property
    def phase(cls):
        return 'After'

    def save_workbook(cls):
        if exists(cls._workbook_name):
            remove(cls._workbook_name)
        cls._workbook.save(cls._workbook_name)
