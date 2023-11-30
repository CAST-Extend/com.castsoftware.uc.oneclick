from oneclick.analysis.analysis import Analysis
from subprocess import Popen,PIPE
from oneclick.config import Config
from cast_common.hlRestCall import HLRestCall
from cast_common.util import run_process,create_folder
from os.path import abspath

import sys

class HLAnalysis(Analysis):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    def run(cls, config:Config):
        if not config.is_hl_active:
            cls._log.warning('Highlight configuration is incomplete, analysis will not run')
            return 0
        
        rest = HLRestCall(hl_base_url=config.hl_url,hl_user=config.hl_user,hl_pswd=config.hl_password,hl_instance=config.hl_instance)

        try:
            process = {}
            for appl in config.application:
                hl_status = config.application[appl]['hl']
                if hl_status == '' or hl_status.startswith('Error'):

                    cls._log.info(f'Running Highlight analysis for {config.project_name}\{appl}')
                    app_id = rest.get_app_id(appl)
                    if app_id is None:
                        cls._log.info(f'Application {appl} not found in Highlight, Creating Application {appl}...')
                        resp_code = rest.create_an_app(config.hl_instance, appl)
                        if resp_code == 200:
                            cls._log.info(f'Application {appl} created inside Highlight.')
                            app_id = rest.get_app_id(appl)
                        else:
                            cls._log.info(f'Not able to Application {appl} inside Highlight due to some error!')                       

                    hl_sourceDir = f'{config.base}\\STAGED\\HL\\{config.project_name}\\{appl}'
                    hl_workingDir = f'{config.oneclick_work}\\{config.project_name}\\HL_ANALYSIS_RESULT\\{appl}'
                    create_folder(f'{config.oneclick_work}\\{config.project_name}\\HL_ANALYSIS_RESULT')
                    create_folder(hl_workingDir)
                    java_home = config.java_home
                    if len(java_home) > 0:
                        java_home = f'{java_home}'

                    args = [abspath(f'{config.java_home}/bin/java.exe'),
                            '-jar',config.hl_cli,
                            '--sourceDir', hl_sourceDir,
                            '--workingDir' , hl_workingDir,
                            '--companyId', str(config.hl_instance),
                            '--analyzerDir',config.analyzer_dir,
                            '--perlInstallDir',config.perl_install_dir,
                            '--applicationId', str(app_id),
                            '--serverUrl', config.hl_url.rsplit('/',1)[0],
                            '--login',config.hl_user,
                            '--password',config.hl_password]
                    try:
                        proc = run_process(args,wait=False)
                    except FileNotFoundError as e:
                        cls._log.error(f'Unable to launch analysis process {e}')
                        cls._log.error(args)
                        return e.errno
                else:
                    proc = None

                cls.track_process(proc,"Highlight",appl)
            return 0


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