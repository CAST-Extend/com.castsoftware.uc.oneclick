__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2024, CAST Software"

from oneclick.configTest import Config,Status
from cast_common.logger import Logger,DEBUG, INFO, WARN, ERROR
from cast_common.util import create_folder
from oneclick.exceptions import InvalidConfigNoBase


from os.path import abspath,join

class Base():
    __config = None
    __log = None
    _progress = False

    def __init__(self, config:Config=None):
        if config is None and Base.__config:
            raise InvalidConfigNoBase()
        elif config is not None:
            Base.__config = config

        if self.log is None:       
            log_level = config.log_level
            log_folder = abspath(f'{config.base_log_folder}/{config.project_name}')
            create_folder(log_folder)
            self.log = Logger(self.__class__.__name__,log_level,file_name=abspath(f'{log_folder}/General.log'),console_output=False)

    @property
    def config(self):
        return Base.__config

    @property
    def log(self):
        return Base.__log    
    @log.setter
    def log(self, value):
        Base.__log = value

    @property
    def choose(self) -> bool:
        return True if self.config.debug else False
    
    @property
    def can_run(self) -> bool:
        return True
    
    process_cnt = 0
    process_txt = '\\|/-\\|/-'
    def show_progress(self,done=False,clear=False):
        config = self.config

        out = []

        header = f'------------------------ ------------------------ ---------- -------------- --------- --------- --------- --------- --------- --------- ---------'
        if clear:
            if Base._progress:
                for l in range(len(config.applist)+5):
                    line = ' '
                    out.append(f'{line:{len(header)}}\n')
        else:
            Base._progress=True
            line = f'{self.process_txt[self.process_cnt]} Running {self.name} for project: {config.project_name}'
            out.append(f'\r{line:<{len(header)}}\n')
            out.append(f'                                                                                  Removed                            SQL Discovery\n')
            out.append(f'Appl Name                Status                    Unpacked       LOC        Folders     Files   Tables   Functions   Procs     Views   Triggers\n')
            out.append(f'{header}\n')
            for app in config.applist:
                app_name = app['name']
                app_status = app['status']['aip']
                loc = app['loc'] if 'loc' in app else ''
                unpacked = app['unpacked'] if 'unpacked' in app else ''
                folders = app['deleted']['folders'] if 'deleted' in app else ''
                files = app['deleted']['files'] if 'deleted' in app else ''
                tables = app['sql']['tables'] if 'sql' in app else ''
                functions = app['sql']['functions'] if 'sql' in app else ''
                procedures = app['sql']['procedures'] if 'sql' in app else ''
                views = app['sql']['views'] if 'sql' in app else ''
                triggers = app['sql']['triggers'] if 'sql' in app else ''
                
                out.append(f'{app_name:<25}{Status(app_status).name.replace("_", " "):<25}{unpacked:>10}{loc:>15}{folders:>10}{files:>10}{tables:>10}{functions:>10}{procedures:>10}{views:>10}{triggers:>10}\n')

        if done:
            return ''.join(out)
        elif Base._progress:
            pass
            for l in range(len(config.applist)+5):
                out.append(f'\033[F')
            out.append('\r')
            self.process_cnt += 1
            if self.process_cnt == len(self.process_txt):
                self.process_cnt = 0
            out.append(f'\r\033[?25l')
            return ''.join(out)
        else:
            return ''.join(out)        
