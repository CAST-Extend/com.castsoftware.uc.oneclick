from oneclick.configTest import Config,Status
from oneclick.analysis.analysis import Analysis
from oneclick.discovery.cleanup import Cleanup
from cast_common.hlRestCall import HLRestCall
from cast_common.util import run_process,create_folder,check_process
from subprocess import Popen,PIPE

from os.path import abspath
from os.path import exists

class RunAnalysis(Analysis):
    _running = 0
    _max = 2
    _process = {}
    _output = {}

    @property
    def max(cls):
        return RunAnalysis._max
    @property
    def running(cls):
        return RunAnalysis._running
    @running.setter
    def running(cls,value):
        RunAnalysis._running = value

    @property
    def process(cls):
        return RunAnalysis._process

    @property
    def output(cls) -> dict:
        return RunAnalysis._output

    def __init__(cls):
        # RunAnalysis._max = 2
        # RunAnalysis._running = 0
        pass

    def run(self):

        

        config = self.config
        while True:
            done = True
            for appl in config.applist:
                print (self.show_progress())
                app_name = appl['name']
                app_status = Status(self.status(appl))
                if app_status < Status.SOURCE_CLEAN_END:
                    config.log.info(f'Analysis cannot run, please run "{Cleanup.name}" step first')
                    continue
                if app_status >= Status.ANALYSIS_END:
                    continue
                done = False

                if self.can_run(appl):
                    self.log.info(f'Running {self.name} for {config.project_name}\{app_name}')

                    proc = self.run_analysis(appl)
                    if proc == 'DONE':
                        app_status = self.status(appl, Status.ANALYSIS_END)
                        pass
                    else:
                        app_status = self.status(appl, Status.ANALYSIS_START)
                        self.running += 1
                        self.process[app_name] = proc
                        self.output[app_name] = []
                        pass
                    print(self.show_progress())
                elif app_status == Status.ANALYSIS_START:
                    #get the process results
                    if (app_name in self.process):
                        if (self.process[app_name].poll() is None):
                            #process is still running, collect some output
                            out_ary = self.output[app_name]
                            line = self.process[app_name].stdout.readline()
                            if line and len(line) > 0:
                                out_ary.append(line)
                            pass
                        else:
                            #process is done, mark it complete and read any remaining lines 
                            app_status = self.status(appl, Status.ANALYSIS_END)
                            self.running -= 1
                            try:    
                                out_ary = self.output[app_name]
                                while True:
                                    line = self.process[app_name].stdout.readline()
                                    if line and len(line) > 0:
                                        out_ary.append(line)
                                    elif not line:
                                        break
                                
                            except IOError as ex:
                                if str(ex) == 'read of closed file':
                                    config.log.debug(f'Process already closed {app_name}')
                            pass
                else:
                    app_status = self.status(appl, Status.ANALYSIS_QUEUE)
                    pass
            if done:
                break

        print (self.show_progress(done=True))
        return True


    process_cnt = 0
    process_txt = '\\|/-\\|/-'
    def show_progress(self,done=False,clear=False):
        config = self.config
        out = []

        header = f'------------------------ ------------------------ ----------------------------------------------------------------------------------------------------'
        if clear:
            for l in range(len(config.applist)+5):
                line = ' '
                out.append(f'{line:{len(header)}}\n')
        else:
            line = f'{self.process_txt[self.process_cnt]} Running {self.name} for project: {config.project_name}'
            out.append(f'\r{line:<{len(header)}}\n')
            out.append(f'Appl Name                Status\n')
            out.append(f'{header}\n')
            for app in config.applist:
                app_status = self.status(app)
                app_name = app['name']
                last_line = self.output[app_name][-1].replace('\n','').replace('\t','') if app_name in self.output and len(self.output[app_name])>0 else ''
                last_line = last_line[:100].ljust(100)
                out.append(f'{app_name:<25}{Status(app_status).name.replace("_", " "):<25}{last_line}\n')

        if not done:
            for l in range(len(config.applist)+4):
                out.append(f'\033[F')
            out.append('\r')
            self.process_cnt += 1
            if self.process_cnt == len(self.process_txt):
                self.process_cnt = 0
            out.append(f'\r\033[?25l')
        return ''.join(out)

    def can_run(self, appl):
        app_status = self.status(appl)
        app_name = appl['name']

        if self.running >= self.max:
            # too many analysis running
            return False

        if app_status in [Status.ANALYSIS_START, Status.ANALYSIS_QUEUE] and app_name not in self.process:
            return True
        return False


class RunHighlight(RunAnalysis):

    def __init__(cls):
        # RunHighlight.__running = 0
        # RunHighlight.__max = 2
        
        cls._df = {}
        config = cls.config
        cls.rest = HLRestCall(hl_base_url=config.hl_url,hl_user=config.hl_user,hl_pswd=config.hl_password,hl_instance=config.hl_instance)
        pass

    @property
    def choose(cls) -> bool:
        return True
    @property
    def name(cls) -> str:
        return 'RunHighlight'


    # @property
    # def running(cls):
    #     return RunHighlight.__running
    # @running.setter
    # def running(value):
    #     RunHighlight.__running = value

    # @property
    # def max(cls):
    #     return RunHighlight.__max

    def status(cls,appl,new_status=None):
        if new_status is not None:
            appl['status']['highlight'] = new_status
            cls.config._save()
        return appl['status']['highlight']

    def run_analysis(cls, appl):
        config = cls.config
        app_name = appl['name']

        hl_source_folder = abspath(f'{config.stage_folder}/{config.project_name}\\{app_name}')
        hl_working_folder = abspath(f'{config.highlight_folder}/{config.project_name}/HL_ANALYSIS_RESULT/{app_name}')
        create_folder(hl_working_folder)
        java_home = config.java_home
        if len(java_home) > 0:
            java_home = f'{java_home}'

        do_upload=True
        url = config.hl_url.rsplit('/',1)[0]
        
        app_id = None
        if len(url) == 0 or len(config.hl_user) == 0 or len(config.hl_password) == 0:
            cls.log.info(f'Highlight URL not defined, skipping analysis upload for {app_name}')
            do_upload = False
        else:
            app_id = cls.rest.get_app_id(app_name)


        if app_id is None and do_upload:
            config.log.info(f'Application not found in Highlight, Creating Application {app_name}...')
            resp_code = cls.rest.create_an_app(config.hl_instance, app_name)
            if resp_code == 200:
                config.log.info(f'Application {app_name} successfuly created inside Highlight.')
                app_id = cls.rest.get_app_id(app_name)
            else:
                config.log.error(f'Error creating Application {app_name} inside Highlight due to some error!') 

        hl_cli_folder = abspath(config.hl_cli.rsplit('\\',1)[0])


        args = [abspath(f'{config.base}/scripts/runHighlight.bat'),
                abspath(f'{config.java_home}/bin/java.exe'),
                hl_cli_folder,
                hl_source_folder,
                hl_working_folder,
                config.hl_url,
                str(config.hl_instance),
                str(app_id),
                config.hl_user,
                config.hl_password]

        try:
            proc = run_process(args,wait=False)
            return proc
            pass

        except FileNotFoundError as e:
            cls.log.error(f'Unable to launch analysis process {e}')
            cls.log.error(args)
            return e.errno

        return 'DONE'
