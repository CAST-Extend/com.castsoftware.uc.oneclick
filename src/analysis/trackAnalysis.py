from logging import Logger
from logger import INFO
from config import Config
from analysis.analysis import Analysis,Process
from subprocess import TimeoutExpired
from time import sleep
#from util import find_in_list

class TrackAnalysis(Analysis):
    def __init__(cls, post_aip_opertion, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        cls._post_aip = post_aip_opertion
        pass

    def run(cls, config:Config):

        while True:
            cls._log.info(f'Checking {len(cls._pid)} processes ...')
            for p in cls._pid:
                just_completed=False
                process = p.process
                if p.status is None or p.status == "Running":
                    if process is not None and process.poll() is None:
                        #process is running
                        p.status = "Running"
                        try:
                            # line = process.stdout.readline(timeout=1)
                            # line = line.rstrip('\n')
                            # if len(line.strip(' ')) > 0:
                            #     p.log.append(line)

                            stdout, stderr = process.communicate(timeout=1)
                            for line in stdout.split('\n'):
                                p.log.append(line)

                        except TimeoutExpired:
                            pass 
                        pass
                    else:
                        just_completed=True
                        if process is None:
                            if p.operation == 'AIP':
                                p.status = config.application[p.name]['aip']
                            else:
                                p.status = config.application[p.name]['hl']
                        else:
                            stdout, stderr = process.communicate()
                            for line in stdout.split('\n'):
                                #if len(find_in_list(line,p.log))==0:
                                p.log.append(line)
                            if process.returncode == 0:
                                p.status = 'OK'
                            else:
                                p.status = f'Error: {process.returncode}'

                            if p.operation == 'AIP':
                                config.application[p.name]['aip'] = p.status
                            else:
                                config.application[p.name]['hl'] = p.status
                            config._save()
                            

                cls._log.info(f"{p.operation} analysis for {config.project_name}\{p.name}: {p.status}")
                if just_completed == True:
                    for line in p.log:
                        print(f'\t{line}')

                    if p.status=='OK' and  p.operation == 'AIP':
                        cls._log.info('Running post analsis jobs...')
                        for proc in cls._post_aip:
                            if proc.__class__.__name__ not in config.application[p.name] or \
                                config.application[p.name][proc.__class__.__name__] != 'OK':

                                cls._log.info(f'******************* {proc.__class__.__name__} *******************************')
                                proc.run(p.name)
                                
                                config.application[p.name][proc.__class__.__name__]='OK'
                                config._save()


            running = False
            for p in cls._pid:
                if p.status=='Running':
                    running = True
                    break 
            if not running:
                cls._log.info(f'All processing complete')
                error = False
                for p in cls._pid:
                    cls._log.info(f"{p.operation} for {config.project_name}\{p.name}: {p.status}")
                    if "OK" not in p.status:
                        error = True
                break
            sleep(60)
        return error


        #     status,output = check_process(process[appl])
        #     if status != 0:
        #         cls._log.error(f'Error analyzing {appl}')
        #         error = True
        # if error:
        #     # TODO: add more desriptive error message
        #     raise RuntimeError ("")

