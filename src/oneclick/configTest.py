__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2024, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

from cast_common.logger import Logger,DEBUG, INFO, WARN, ERROR
from argparse import ArgumentParser
from os import listdir, getenv,getcwd
from os.path import abspath,exists,isfile, join
from argparse_formatter import FlexiFormatter,ParagraphFormatter
from json import load,dump

from inquirer import List,prompt,Text,password

from cast_common.util import create_folder, yes_no_input,folder_input,file_input,secret_input,url_input,string_input
from oneclick.exceptions import InvalidConfiguration,InvalidConfigNoBase
from enum import Enum,IntEnum

class Status(IntEnum):
    NOT_STARTED =                       0
    STAGED =                            10
    UNPACK_START =                      20
    UNPACK_END =                        25

    CLOC_PRE_CLEAN_START =              30
    CLOC_PRE_CLEAN_QUEUE =              32
    CLOC_PRE_CLEAN_RUNNING =            34
    CLOC_PRE_CLEAN_REPORT =             35
    CLOC_PRE_CLEAN_END =                36
    CLOC_PRE_CLEAN_ERROR =              38

    SOURCE_CLEAN_START =                40
    SOURCE_CLEAN_END =                  48

    CLOC_POST_CLEAN_START =             50
    CLOC_POST_CLEAN_QUEUE =             52
    CLOC_POST_CLEAN_REPORT =            35
    CLOC_POST_CLEAN_RUNNING =           54
    CLOC_POST_CLEAN_END =               56
    CLOC_POST_CLEAN_ERROR =             58

    SQL_DISCOVERY_START =               60
    SQL_DISCOVERY_END =                 68

    DISCOVERY_REPORT_START =            70
    DISCOVERY_REPORT_END =              78
    
    ANALYSIS_START =                    90
    ANALYSIS_QUEUE =                    92 
    ANALYSIS_END =                      95
    COMPLETED =                         100
    ERROR =                             999

    def __str__(self):    
        return str(self.value)

class Config():
    _config = None
    _config_file = None

    _base = None
    _log_base = None

    _log = None
    _log_level = None


    def command_line(self) -> ArgumentParser:
        parser = ArgumentParser(prog='OneClick',  formatter_class=lambda prog: FlexiFormatter(prog, width=99999, max_help_position=60))

        parser.add_argument('-b','--base', required=False, help='Base Folder Location',metavar='BASE_FOLDER')
        parser.add_argument('-p','--project', help='Name of the project')
        parser.add_argument('-s','--start', help='Starting step')
        parser.add_argument('-e','--end', help='Ending step')
        parser.add_argument('-g','--global_config',action='store_true',help='Update global configuration file')
        parser.add_argument('-d','--debug',action='store_true',help='Run in debug mode')
        parser.add_argument('-r','--reset',action='store_true',help='Rerun all applications')
        parser.add_argument('-q','--quiet',action='store_true',help='Run with no unnessary user intaction')

        parser.add_argument('--skipHighlight',action='store_true',help='Don\'t run Highlight Analysis')
        parser.add_argument('--skipMRI',action='store_true',help='Don\'t run MRI Analysis')

        # parser.add_argument('-rh','--runHighlight',action='store_true',default=True help='Run Highlight Analysis')
        # parser.add_argument('-rm','--runMRI',action='store_true',default=True help='Run MRI Analysis')

        return parser



#    def __init__(self,parser:ArgumentParser,default_args={},log_level: int=INFO):
    def __init__(self):

        Config._config = {}
        parser = self.command_line()
        args = parser.parse_args()

        Config._args = args
        base_config_name=None
        if not args.base is None:
            self.base = args.base
        if len(self.base)==0 or self.base is None:
            self.base = getcwd()
            # if not self.quiet:
            #     self.base = folder_input('Where is OneClick installed',folder=self.base,file='oneclick.bat')
            #     if not exists(self.base):
            #         raise InvalidConfiguration('Base configuration file found, please run setup')
            #make sure the configuration folder is there
                

        # load the default configuration, if exists
        base_config_name = abspath(f'{self.base}/.oneclick/config.json'.lstrip().rstrip())
        create_folder('\\'.join(base_config_name.split('\\')[:-1]))
        if exists(base_config_name):
            save_base=self.base
            with open(base_config_name, 'rb') as config_file:
                Config._config = load(config_file)
            self.base=save_base
            if args.global_config or \
               not self.check_list(self.settings,['work','java','cloc','profiler']) or \
               not self.check_list(self.highlight,['cli','agent']) or \
               not self.check_list(self.console, ['cli','URL', 'user', 'token']) :
                self.setup_default_config(False)
        else:
            self.quiet=False #global configuration file does not exist, we need to be sure quiet mode is not on
            self.setup_default_config()
            pass

        Config._log_level = DEBUG if args.debug else INFO
        Config.base_log_folder = abspath(f'{self.base}/logs')
        create_folder(self.base_log_folder)
        Config.log = Logger(self.__class__.__name__,DEBUG if args.debug else INFO,file_name=abspath(f'{self.base_log_folder}/General.log'))
        self.log.debug(self.report())

        #get the project name
        project_name = Config._config_file = None
        if not args.project is None:
            project_name = args.project.lstrip().rstrip()
        if project_name is None or len(project_name) == 0:

            dir_ = abspath(f'{self.base}/.oneclick')
            proj_cnt = len([name for name in listdir(dir_) if isfile(join(dir_, name))])
            if proj_cnt > 1:
                choices=[name.replace('.json','') for name in listdir(dir_) if isfile(join(dir_, name)) and name != 'config.json']
                choices.insert(0,'New Project')
                questions = [
                    List(
                        'project',
                        message="Which project do you want to work on?", 
                        choices=choices
                        )
                ]
                answers = prompt(questions)
                project_name = answers['project']
                if project_name == 'New Project':
                    questions = [
                        Text('project', message="What is the name of this project?")
                    ]
                    while True:
                        answers = prompt(questions)
                        project_name = answers['project']
                        project_config = abspath(f'{dir_}/{project_name}.json')
                        if not exists(project_config):
                            break
                        else:
                            if yes_no_input(f'Project {project_name} already exists, run it',default_value=False):
                                break
                            pass
                Config._config_file = abspath(f'{self.base}/.oneclick/{project_name}.json')
                pass
            else:
                project_name = string_input('What is the name of the project')
        
        Config._config_file = abspath(f'{self.base}/.oneclick/{project_name}.json')
        if exists(Config._config_file):
            with open(Config._config_file, 'rb') as config_file:
                Config._config = load(config_file)
        else:
            self.project_name = project_name

        self.merge_from_global()
        if not self.quiet and \
           not self.check_list(self.highlight,['URL','user','password','instance']) and \
           yes_no_input('Upload Highlight analysis results to the dashboard',default_value=True): 
            self.get_highlight_access_info()
        pass

    def merge_from_global(self):
        global_config_name = abspath(f'{self.base}/.oneclick/config.json'.lstrip().rstrip())
        global_data = None
        with open(global_config_name, 'rb') as config_file:
            global_data = load(config_file)

        self.copy_data(global_data['settings'], self.data['settings'])
        self.copy_data(global_data['rest']['highlight'], self.data['rest']['highlight'])
        self.copy_data(global_data['rest']['console'], self.data['rest']['console'])
        self.copy_data(global_data['rest']['dashboard'], self.data['rest']['dashboard'])

    def copy_data(self, gdata,pdata):
        """
        copy from gdata to pdata where gdata has a value and a change has been made to gdata

        Args:
            gdata (_type_): source dictionary 
            pdata (_type_): destination dictionary 
        """
        global_keys = set(gdata.keys())
        project_keys = set(pdata.keys())
        shared_keys = global_keys.intersection(project_keys)

        modified = False
        for key in shared_keys:
            if gdata is not None and len(gdata[key]) and pdata[key] != gdata[key]:
                pdata[key] = gdata[key]
                modified = True

        if modified:
            self._save()    
        pass


    def setup_default_config(self,first=True):
        if not self.update_global and self.quiet:
            return 
        
        msg = ''
        if first:
            msg = 'This is the first time you are running OneClick, we need to set up some default configuration.'
        else:
            msg = 'Detected some missing configuration information, rerunning setup now.'
        print (
"""
Global Configuration
--------------------
{msg}

OneClick is organized into two distinct components: the base and the work folders. The base 
encompasses all executable files and configuration data, while the work folder houses the 
source code to be analyzed, as well as all logging, analysis results and reports. Although this 
division is not mandatory, it facilitates usage over a network connection. Notably, the base 
and work folders can also reside in the same location.

""".format(msg=msg)
        )

        Config._config_file = abspath(f'{self.base}/.oneClick/config.json')
        # if exists(self._config_file):
        #     with open(self._config_file, 'rb') as config_file:
        #         Config._config = load(config_file)

        scripts_folder = abspath(f'{self.base}/scripts')

        #work folder
        if self.update_global or not self.quiet:
            self.work = folder_input('Work folder location',folder=self.work,create=True) 
            create_folder(self.deliver_folder)
            create_folder(self.stage_folder)
            create_folder(self.report_folder)
            create_folder(self.highlight_folder)

            #java home
            self.java_home = folder_input("Java installation folder location",getenv('JAVA_HOME'),'bin/java.exe')
            #cloc executable location
            self.cloc = file_input("CLOC installation folder location", scripts_folder, 'cloc*.exe')
            #profiler executable location
            self.profiler = folder_input("Profiler installation folder location",self.profiler,'CAST-Profiler.exe')

            print ('')

        #highlight rest api information
        if first or not (self.highlight and self.check_list(self.highlight,['cli','agent','perl','URL','user','password','instance'])):
            if yes_no_input('Is OneClick being used to run Highlight analysis?'):
                self.hl_cli = folder_input('Highlight Automation Command location',self.hl_cli,'HighlightAutomation.jar',True)
                self.hl_agent = folder_input('Highlight Code Reader location',self.hl_agent,'nw.exe',True)
                agent_no_file = self.hl_agent.rsplit("\\",1)[0]
                # self.hl_perl = abspath(f'{agent_no_file}/strawberry')
                # self.hl_analysis = abspath(f'{self.hl_cli}/strawberry/perl')

                if yes_no_input('Upload results to highlight dashboard',default_value=True):
                    self.get_highlight_access_info()
                    pass
                print ('')
        
        #console automation information
        if first or not (self.console and self.check_list(self.console,['cli','URL','user','token'])):
            if yes_no_input('Is OneClick being used to run MRI analysis?'):
                self.console_cli = folder_input('MRI Automation Command Line interface location', self.console_cli, 'aip-console-tools-cli.jar', True)
                self.console_url = url_input('AIP Console URL', self.console_url)
                self.console_user = string_input('AIP Console User ID', self.console_user)
                self.console_token = secret_input('AIP Console Token',self.console_token)
                print ('')
            else:
                self._save()
        pass


        """
        collect dashboard information
            check if the console information is there, if not no MRI analysis 
            will be run so there is no need to add dashboard
        """
        if self.console and first and not (self.quiet and self.dashboard):
            questions = [
                Text('url', message="What is the URL of the CAST Dashboard"),
                Text('user','What is the user id'),
                password('user','What is the password'),
            ]
            answers = prompt(questions)
            self.dashboard_url = answers['url']
            self.dashboard_user = answers['user']
            self.dashboard_password = answers['password']   
            pass
        else:
            self.dashboard
            self._save()

        pass

    def get_highlight_access_info(self):
        self.hl_url = url_input('Highlight URL',self.hl_url)
        self.hl_user = string_input('Highlight user name',self.hl_user)
        self.hl_password = secret_input('Highlight password')
        self.hl_instance = string_input('Highlight instance id',self.hl_instance)
        pass

    def report(self,is_config=False):
        """
        Report the current configuration
        """
        rpt_base =  ''
        if self.debug:
            rpt_base = rpt_base + \
"""
     ***********************************************************************************************
                          R U N N I N G  I N   D E B U G   M O D E
     ***********************************************************************************************
"""            

        rpt_base = rpt_base +  \
"""
    OneClick Configuration
    ----------------------
    Base Folder: {self.base}
    General Settings:
        Work Folder: {self.work}
        Java Home: {self.java_home}
        CLOC: {self.cloc}
        Profiler: {self.profiler}
    REST Configuration
        Highlight:
            CLI: {self.hl_cli}
            Agent: {self.hl_agent}
            URL: {self.hl_url}
            User: {self.hl_user}
            Instance: {self.hl_instance}
            password: {hl_password}
        Console:
            AIP Console CLI: {self.console_cli}
            URL: {self.console_url}
            User: {self.console_user}
            Token: {console_token}
        Dashboard:
            URL: {self.dashboard_url}
            User: {self.dashboard_user}
            Password: {dashboard_password}
    """.format(self=self,
               hl_password=('Password Set' if len(self.hl_password) else 'Password Not Set'),
               console_token=('Password Set' if len(self.console_token) else 'Password Not Set'),
               dashboard_password=('Password Set' if len(self.dashboard_password) else 'Password Not Set')
        )

        if is_config:
            return rpt_base
        rpt_apps = self.application_report()

        rpt_final = """
========================================================================================================================
    """
        rpt_txt = rpt_base + rpt_apps + rpt_final
        return rpt_txt

    def application_report(self):
        rpt_apps = f" Project: {self.project_name}"
        if len(self.applist) == 0:
            rpt_apps = rpt_apps + "\tNo Applications"
        else:
            rpt_apps = rpt_apps + '\n Appl Name\tHighlight\t                 MRI\t\t\t\tMRI Security    MRI Blue Print\n'
            rpt_apps = rpt_apps + ' ----------\t-------------------------------\t------------------------------- --------------- ------------------\n'
            for app in self.applist:
                # app['status']['aip']=app['status']['highlight']=Status.NOT_STARTED
                rpt_apps = rpt_apps + f" {app['name']:<15}\t{Status(app['status']['highlight']).name.replace('_',' '):<25}\t{Status(app['status']['aip']).name.replace('_',' '):<25}\t{app['security']}\t\t{app['blueprint']}\n"
        return rpt_apps        

    def _get(self,base,key,default=''):
        if key not in base:
            base[key] = default  
        return base[key]        

    def _set_value(self,base,key,value,default=''):
        base[key] = self._get(base,key,default)
        if value is not None:
            base[key]=value
            return True
        else:
            return False

    def check_list(self, node, chk_lst):
        chk = True
        for item in chk_lst:
            if item not in node or node[item]=='':
                chk = False
                break
        return chk
    
    def _set_active(self,node,chk_lst):
        node['Active']=self.check_list(node, chk_lst)

    def _save(self):
        if Config._config_file is None: raise InvalidConfiguration('No config file')
        create_folder(abspath(f'{self.base}/.oneClick'))
        with open(Config._config_file, "w") as f:
            dump(Config._config, f,indent=4)

    @property
    def data(self):
        return Config._config

    """
        Argument Properties
    """
    @property
    def quiet(self):
        return Config._args.quiet 
    @quiet.setter
    def quiet(self, value):
        Config._args.quiet = value
    @property
    def start(self):
        return Config._args.start 
    @start.setter
    def start(self, value):
        Config._args.start = value

    @property
    def end(self):
        return Config._args.end 
    @end.setter
    def end(self, value):
        Config._args.end = value

    @property
    def debug(self):
        return Config._args.debug
    @property
    def update_global(self):
        return Config._args.global_config

    @property
    def reset(self):
        return Config._args.reset 


    @property 
    def deliver_folder(self): return abspath(f'{self.work}/DELIVER')
    @property 
    def stage_folder(self): return abspath(f'{self.work}/STAGED')
    @property 
    def report_folder(self): return abspath(f'{self.work}/REPORT')
    @property 
    def highlight_folder(self): return abspath(f'{self.work}/HIGHLIGHT')
    @property 
    def log_folder(self): return abspath(f'{self.base}/LOGS')
    @property 
    def scripts_folder(self): return abspath(f'{self.base}/SCRIPTS')

    @property
    def base(self):
        return self._get(Config._config,'base')
    @base.setter
    def base(self,value):
        self._set_value(Config._config,'base',value)
        
    @property
    def base_log_folder(self):
        return self._get(Config._config,'base.log.folder')
    @base_log_folder.setter
    def base_log_folder(self, value):
        self._set_value(Config._config, 'base.log.folder', value)

    @property
    def work(self):
        return self._get(self.settings,'work')
    @work.setter
    def work(self, value):
        self._set_value(self.settings, 'work', value)
        self._save()

    @property
    def log(self) -> Logger:
        return Config._log
    @property
    def log_level(self):
        return Config._log_level
    
    @property
    def settings(self):
       return self._get(Config._config,'settings',{})

    @property
    def java_home(self) -> str:
        return self._get(self.settings,'java','')
    @java_home.setter
    def java_home(self,value):
        self._set_value(self.settings, 'java', value)
        self._save()

    @property
    def cloc(self) -> str:
        return self._get(self.settings,'cloc','')
    @cloc.setter
    def cloc(self, value):
        self._set_value(self.settings, 'cloc', value)
        self._save()

    @property
    def profiler(self) -> str:
        return self._get(self.settings, 'profiler', '')
    @profiler.setter
    def profiler(self, value):
        self._set_value(self.settings, 'profiler', value)
        self._save()

    @property
    def rest(self):
       return self._get(Config._config,'rest',{})

    @property
    def highlight(self):
       return self._get(self.rest,'highlight',{})

    @property
    def hl_cli(self) -> str:
        return self._get(self.highlight,'cli','')
    @hl_cli.setter
    def hl_cli(self, value):
        self._set_value(self.highlight, 'cli', value)
        # self._set_hl_active()
        self._save()
        
    @property
    def hl_agent(self) -> str:
        return self._get(self.highlight,'agent','')
    @hl_agent.setter
    def hl_agent(self, value):
        self._set_value(self.highlight, 'agent', value)
        self._save()
    # @property
    # def hl_analizer_folder(self) -> str:
    #     agent = abspath(self._get(self.highlight, 'agent', ''))
    #     agent = agent.rsplit("\\", 1)[0]
    #     return abspath(f'{agent}/perl')

    # @property
    # def hl_perl(self) -> str:
    #     return abspath(f"{self._get(self.highlight,'perl','')}/perl")
    # @hl_perl.setter
    # def hl_perl(self, value):
    #     self._set_value(self.highlight, 'perl', value)
    #     self._save()

    @property
    def hl_user(self) -> str:
        return self._get(self.highlight, 'user', '')
    @hl_user.setter
    def hl_user(self, value):
        self._set_value(self.highlight, 'user', value)
        self._save()

    @property
    def hl_url(self) -> str:
        return self._get(self.highlight, 'URL', '')
    @hl_url.setter
    def hl_url(self, value):
        self._set_value(self.highlight, 'URL', value)
        self._save()

    @property
    def hl_password(self) -> str:
        return self._get(self.highlight, 'password', '')
    @hl_password.setter
    def hl_password(self, value):
        self._set_value(self.highlight, 'password', value)
        self._save()

    @property
    def highlight_active(self):
        self.check_list(self.highlight,['hl_cli','hl_agent','hl_perl','URL','hl_user','hl_instance'])

    @property
    def hl_instance(self) -> str:
        return self._get(self.highlight, 'instance', '')
    @hl_instance.setter
    def hl_instance(self, value):
        self._set_value(self.highlight, 'instance', value)
        self._save()

    @property
    def console(self):
       return self._get(self.rest, 'console', {})

    @property
    def console_cli(self) -> str:
        return self._get(self.console, 'cli', '')
    @console_cli.setter
    def console_cli(self, value):
        self._set_value(self.console, 'cli', value)
        self._save()

    @property
    def console_url(self) -> str:
        return self._get(self.console, 'URL', '')
    @console_url.setter
    def console_url(self, value):
        self._set_value(self.console, 'URL', value)
        self._save()

    @property
    def console_token(self) -> str:
        return self._get(self.console, 'token', '')
    @console_token.setter
    def console_token(self, value):
        self._set_value(self.console, 'token', value)
        self._save()

    @property
    def console_user(self) -> str:
        return self._get(self.console, 'user', '')  
    @console_user.setter
    def console_user(self, value):
        self._set_value(self.console, 'user', value)
        self._save()

    @property
    def dashboard(self):
       return self._get(self.rest, 'dashboard', {})

    @property
    def dashboard_url(self) -> str:
        return self._get(self.dashboard, 'URL', '')
    @dashboard_url.setter
    def dashboard_url(self, value):
        self._set_value(self.dashboard, 'URL', value)
        self._save()

    @property
    def dashboard_user(self) -> str:
        return self._get(self.dashboard, 'user', '')
    @dashboard_url.setter
    def dashboard_user(self, value):
        self._set_value(self.dashboard, 'user', value)
        self._save()

    @property
    def dashboard_password(self) -> str:
        return self._get(self.dashboard, 'password', '')
    @dashboard_url.setter
    def dashboard_password(self, value):
        self._set_value(self.dashboard, 'password', value)
        self._save()

    @property
    def enable_security_assessment(self) -> bool:
        return self._get(self.console, 'enable_security_assessment', True)
    @enable_security_assessment.setter
    def enable_security_assessment(self, value):
        self._set_value(self.console, 'enable_security_assessment', value)
        self._save()

    @property
    def project(self):
       return self._get(Config._config, 'project', {})
    
    @property
    def project_name(self):
       return self._get(self.project,'name')
    @project_name.setter
    def project_name(self, value):
        self._set_value(self.project,'name', value)
        self._save()

    @property
    def is_hl_active(self) -> bool:
        return self.highlight['Active']
    
    @property
    def applist(self) -> List:
       return self._get(self.project, 'applist', [])

    def add_app(self, app_name,security,blueprint):
        if app_name not in self.applist:
            new_app = App(app_name)
            new_app.security = security
            new_app.blueprint = blueprint
            self.applist.append(new_app)
            # self._set_value(self.applist, app_name, new_app)
            self._save()  # save the config after adding an app
            return new_app
        else:
            return self._applist[app_name]

    def remove_app(self, app_name):
        if app_name in self._applist:
            del self._applist[app_name]
            self._save()  
            return True
        return False

class App(dict):
    def __init__(self, name):
        self.name = name
        self['status'] = {'highlight': Status.NOT_STARTED, 'aip': Status.NOT_STARTED}

    @property
    def name(self):
        if 'name' not in self: return None
        return self['name']
    @name.setter
    def name(self, value):
        self['name'] = value

    @property
    def status(self):
        return self['status']

    @property
    def highlight(self):
        return self.status['highlight']
    @highlight.setter
    def highlight(self, value:Status):
        if not isinstance(value, Status):
            raise ValueError("Status must be a Status enum")
        self.status['highlight'] = value
        self.log.info(f'Highlight status set to {value.value}')

    @property
    def aip(self):
        return self.status['aip']
    @aip.setter
    def aip(self, value:Status):
        if not isinstance(value, Status):
            raise ValueError("Status must be a Status enum")
        self.status['aip'] = value
        self.log.info(f'CAST Imaging status set to {value.value}')

    @property
    def is_security(self) ->bool:
        return self['security']
    @is_security.setter
    def security(self, value:bool):
        if type(value) is not bool: raise ValueError("Security must be a boolean")
        self['security'] = value
    
    @property
    def is_blueprint(self) -> bool:
        return self['blueprint']
    @is_blueprint.setter
    def blueprint(self, value: bool):
        if type(value) is not bool: raise ValueError("Blueprint must be a boolean")
        self['blueprint'] = value


