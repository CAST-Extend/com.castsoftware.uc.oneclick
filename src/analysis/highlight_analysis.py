from analysis.analysis import Analysis
from subprocess import Popen,PIPE
from config import Config
from hlRestCall import HLRestCall
from util import run_process,create_folder

import sys

class HLAnalysis(Analysis):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    def run(cls, config:Config):
        rest = HLRestCall(config.hl_url,config.hl_user,config.hl_password,config.hl_instance)

        try:
            process = {}
            for appl in config.application:
                hl_status = config.application[appl]['hl']
                if hl_status == '' or hl_status.startswith('Error'):

                    cls._log.info(f'Running Highlight analysis for {config.project_name}\{appl}')
                    app_id = rest.get_app_id(appl)
                    hl_work_folder = f'{config.base}\\work\\{config.project_name}\\{appl}'

                    create_folder(f'{hl_work_folder}\\HL-WORK')

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
                    proc = run_process(args,wait=False)
                else:
                    proc = None

                cls.track_process(proc,"Highlight",appl)



            # error = False
            # for appl in process:
            #     cls._log.info(f'Tracking Highlight analysis for {config.project_name}\{appl}')
            #     status,output = check_process(process[appl])
            #     if status != 0:
            #         cls._log.error(f'Error analyzing {appl}')
            #         error = True
            # if error:
            #     # TODO: add more desriptive error message
            #     raise RuntimeError ("")
        except KeyError as e:
            msg = str(e)
            if 'application not found:' in msg:
                cls._log.error(msg)
                sys.exit(1)