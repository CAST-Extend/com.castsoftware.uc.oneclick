from oneclick.analysis.analysis import Analysis
from oneclick.analysis.trackAnalysis import TrackAnalysis
from oneclick.config import Config
from cast_common.logger import INFO
from cast_common.util import run_process
from json import dumps
from os.path import abspath


class AIPAnalysis(Analysis):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass
    
    def run(cls, config:Config):
        if not config.is_aip_active:
            cls._log.warning('AIP active flag is set to false, skipping analysis')
            return 

        for appl in config.application:

            #has thi spplication already been run?
            aip_status = config.application[appl]['aip']
            if aip_status == '' or aip_status.startswith('Error'):
                #add a new appication in AIP Console
                cls._log.info(f'Running analysis for {config.project_name}\{appl}')

                java_home = config.java_home
                if len(java_home) > 0:
                    java_home = f'{java_home}/bin/'
                
                args = [f'{java_home}java.exe',
                        '-jar',config.console_cli,
                        'add',
                        '-n',appl,
                        '-f', f'AIP/{config.project_name}/{appl}',
                        '-s',config.console_url,
                        '--apikey',config.console_key,
                        '--verbose' , 'false',
                        '--auto-create','--blueprint'
                        '--node-name',config.console_node,
                        '--enable-security-assessment', config.enable_security_assessment,
                        '--blueprint', config.enable_security_assessment
                        ]
                cls._log.debug(dumps(args, indent=2))

                try:
                    process = run_process(args,wait=False)
                except FileNotFoundError as e:
                    cls._log.error(f'Unable to launch analysis process {e}')
                    cls._log.error(args)
                    return e.errno
            else:
                cls._log.info(f'{appl} has already been successfully analyized, skipping step')
                process = None

            cls.track_process(process,"AIP",appl)
        return 0

        TrackAnalysis(INFO).run(config)
        
        


        