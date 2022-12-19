from analysis.analysis import Analysis
from config import Config
from hlRestCall import HLRestCall

from os import mkdir
from os.path import exists,normpath

class Highlight(Analysis):

    def __init__(cls,config:Config, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)

        cls._rest = HLRestCall(config.hl_url,config.hl_user,config.hl_password,config.hl_instance)

        pass

    def run(cls, config:Config):
        #Arguments to pass in HighlightAutomation 
        wf = f'{config.base}/work/{config.project}'     

        for appl in config.application:
            appl_id = cls._rest.get_app_id(appl)
            if appl_id is None:
                raise ValueError(f'Application {appl} not found in Highlight for instance {cls._rest._hl_instance}')

            source_folder = f'{wf}/{appl}/HL'
            work_folder = f'{wf}/{appl}/HL-Work'

            if not exists(work_folder):
                mkdir (work_folder)

            jar_file_loc = normpath(f'{config.hl_jar_loc}\HighlightAutomation.jar')

            args = [jar_file_loc, 
                    '--sourceDir', f'\"{source_folder}\"', 
                    '--workingDir' , f'\"{work_folder}\"', 
                    '--companyId', config.hl_instance, 
                    '--applicationId', str(appl_id), 
                    '--perlInstallDir', f'\"{config.perlInstallDir}\"',
                    '--login', config.hl_user, 
                    '--password', config.hl_password, 
                    '--serverUrl', config.hl_url] # Any number of args to be passed to the jar file
            
            if not cls.jarWrapper(args):
                raise RuntimeError(f'Highlight analysis error!')

