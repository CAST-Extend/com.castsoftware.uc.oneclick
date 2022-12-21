from analysis.analysis import Analysis
from subprocess import Popen,PIPE
from config import Config
from hlRestCall import HLRestCall
from util import run_process


class Highlight(Analysis):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    

    def run(cls, config:Config):
        rest = HLRestCall(config.hl_url,config.hl_user,config.hl_password,config.hl_instance)

        for appl in config.application:
            cls._log.info(f'Running Highlight analysis for {config.project}\{appl}')
            app_id = rest.get_app_id(appl)
            hl_work_folder = f'{config.base}\\work\\{config.project}\\{appl}'
            if app_id is None:
                raise ValueError(f'Application id not found for {app_id} in instance {config.hl_password}')
            args = [f'{config.java_home}\\bin\\java.exe',
                    '-jar',config.hl_cli,
                    '--sourceDir', f'{hl_work_folder}\\HL',
                    '--workingDir' , f'{hl_work_folder}\\HL-WORK',
                    '--companyId', str(config.hl_instance),
                    '--analyzerDir',config.analyzerDir,
                    '--perlInstallDir',config.perlInstallDir,
                    '--applicationId', str(app_id),
                    '--login',config.hl_user,
                    '--password',config.hl_password]
            status,output = run_process(args)        
            if status != 0:
                raise RuntimeError ("")

