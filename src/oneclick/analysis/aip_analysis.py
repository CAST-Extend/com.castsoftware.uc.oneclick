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
        for appl in config.application:

            #has thi spplication already been run?
            aip_status = config.application[appl]['aip']
            if aip_status == '' or aip_status.startswith('Error'):
                #add a new appication in AIP Console
                cls._log.info(f'Running analysis for {config.project_name}\{appl}')
                
                args = [abspath(f'{config.java_home}/bin/java.exe'),
                        '-jar',config.console_cli,
                        'add',
                        '-n',appl,
                        '-f', f'{config.project_name}/{appl}/AIP',
                        '-s',config.console_url,
                        '--apikey',config.console_key,
                        '--verbose' , 'false',
                        '--auto-create','--blueprint'
                        '--node-name',config.node
                        ]
                cls._log.debug(dumps(args, indent=2))

                if len(config.node) > 0:
                    args = args + ['--node-name',config.node]
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
        
        


        