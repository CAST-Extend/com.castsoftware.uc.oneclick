from sourceValidation import SourceValidation 
from os import mkdir,getcwd
from os.path import dirname,exists

from subprocess import Popen,PIPE

import datetime

class ClocPreCleanup(SourceValidation):
    def __init__(cls, args, log_level:int):
        super().__init__(args,cls.__class__.__name__,log_level)

        # dateTimeObj=datetime.now()
        # cls._file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        cloc_base = f'{cls._args.baseFolder}\\cloc'    
        cls._output_path = f'{cloc_base}\\{cls._args.projectName}'    

        if not exists(cloc_base):
            mkdir(cloc_base)

        if not exists(cls._output_path):
            mkdir(cls._output_path)

        dir = getcwd()
        cls._cloc_path=f'{dir}\\scripts\\cloc-1.64.exe'
        cls._tec_list=f'{dir}\\scripts\\ListOfTechnologies.csv'

        if not exists(cls._cloc_path):
            raise ValueError(f'Cloc utility must be here: {cls._cloc_path}')
        if not exists(cls._tec_list):
            raise ValueError(f'Technology list must be here: {cls._tec_list}')
        pass


    @property
    def output_file(cls):
        return f'{cls._output_path}\\ClocPreCleanup_{cls._args.projectName}.txt'

    @property
    def output_xls(cls):
        return f'{cls._output_path}\\ClocPreCleanup_{cls._args.projectName}.xls'

    def run(cls):
        cloc_folder = f'{cls._args.baseFolder}\\work\\{cls._args.projectName}\\AIP' 

        p = Popen([cls._cloc_path,cloc_folder,"--quiet","--report-file",cls.output_file], shell=True, stdout = PIPE)
        stdout, stderr = p.communicate()
         
        pass

