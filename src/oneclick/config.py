"""
    Read and validate configuration file
"""
from cast_common.logger import Logger,DEBUG, INFO, WARN, ERROR
from cast_common.util import create_folder
from json import load
from argparse import ArgumentParser
from json import JSONDecodeError,dump
from os.path import abspath,exists,dirname
from os import getcwd

from argparse import ArgumentParser
from oneclick.exceptions import NoConfigFound,InvalidConfiguration,InvalidConfigNoBase

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config():
    log = None
    log_translate = {} 

    def __init__(self,parser:ArgumentParser,default_args={},log_level: int=INFO):
        self.log = Logger(self.__class__.__name__,log_level)

        args = parser.parse_args()

        if not exists(abspath(args.baseFolder)):
            raise InvalidConfigNoBase(f'Base folder must exist: {args.baseFolder}')

        base_config=abspath(f'{args.baseFolder}/.oneclick/config.json')
        if not exists(base_config) and args.command == 'run':
            raise NoConfigFound('Base configuration file found, please run with the "config" option')


        if args.command == 'config':
            if not exists(base_config):
                self._config={}
                self._config_file=base_config
                self.base = args.baseFolder
            else: 
                if args.projectName is None:
                    self._config_file = abspath(f'{args.baseFolder}/.oneclick/config.json')
                else:
                    self._config_file = abspath(f'{args.baseFolder}/.oneclick/{args.projectName}.json')

                with open(abspath(self._config_file), 'rb') as config_file:
                    self._config = load(config_file)
            try:       
                if args.java_home is None:
                    self.java_home = ''
                else:
                    self.java_home = args.java_home

                if args.cloc_version is not None: self.cloc_version = args.cloc_version

                #Dashboard
                if args.aipURL is not None: self.aip_url = args.aipURL
                if args.aipPassword is not None: self.aip_password = args.aipPassword
                if args.aipUser is not None: self.aip_user = args.aipUser

                #Highlight
                if self.check_default(args.hlURL,self.hl_url,default_args['hlURL']):
                    self.hl_url = f'{args.hlURL}/WS2'
                if args.hlUser is not None: self.hl_user = args.hlUser
                if args.hlPassword is not None: self.hl_password = args.hlPassword
                if args.hlInstance is not None: self.hl_instance = args.hlInstance
                if self.check_default(args.hlCLI,self.hl_cli,default_args['hlCLI']):
                    self.hl_cli = args.hlCLI

                self.perl_install_dir = abspath(f'{args.hlAgent}/strawberry/perl')
                self.analyzer_dir = abspath(f'{args.hlAgent}/perl')

                #AIPConsole
                if args.consoleURL is not None: self.console_url = args.consoleURL
                if args.consoleKey is not None: self.console_key = args.consoleKey
                if args.consoleCLI is not None: self.console_cli = args.consoleCLI
                if args.enable_security_assessment is not None: self.enable_security_assessment = args.enable_security_assessment
                if args.blueprint is not None: self.blueprint = args.blueprint

                #Database
                if args.dbHost is not None: self.db_host = args.dbHost
                if args.dbPort is not None: self.db_port = args.dbPort
                if self.check_default(args.dbUser,self.db_user,default_args['dbUser']):
                    self.db_user = args.dbUser
                if self.check_default(args.dbPassword,self.db_password,default_args['dbPassword']):
                    self.db_password = args.dbPassword
                if self.check_default(args.dbDatabase,self.db_database,default_args['dbDatabase']):
                    self.db_database = args.dbDatabase

                #settings
                if self.check_default(args.cloc_version,self.cloc_version,default_args['cloc_version']):
                    self.cloc_version = args.cloc_version
        
            except AttributeError as e:
                self.log.debug(str(e))
            return

        #do all required fields contain data
        if args.command == 'run':
            try:
                self._config={}
                self._config_file = abspath(f'{args.baseFolder}/.oneclick/{args.projectName}.json')
                if exists(self._config_file):
                    with open(abspath(self._config_file), 'rb') as config_file:
                        self._config = load(config_file)
                else:
                    with open(base_config) as config_file:
                        self._config = load(config_file)

                self.base=args.baseFolder
                self.project = args.projectName
                self.company_name = args.companyName

                self.start=args.start
                self.start=args.end

                # Run for MRI
                if self.is_console_active == False:
                    if yes_no_input('Run MRI analysis for all applications?'):
                        while not self.is_console_active:
                            if len(self.console_url) == 0:
                                self.console_url=url_input('Missing console URL:',self.console_url)
                            else:
                                self.console_url=self.console_url
                            if len(self.console_key) == 0:
                                self.console_key=secret_input('Missing console KEY:',self.console_key)
                            if len(self.console_cli) == 0:
                                folder_input('\t"AIP Console automation tools" location',dirname(self.console_cli),"aip-console-tools-cli.jar",True)
                    else:
                        self._set_console_active=False                                

                if self.is_hl_active == False:                
                    if yes_no_input('Run Highlight analysis for all applications?'):
                        while not self.is_hl_active:
                            if len(self.hl_url) == 0:
                                self.hl_url=url_input('Missing Highlight URL',self.hl_url)
                            if len(self.hl_user) == 0:
                                self.hl_user=string_input('Missing Highlight User ID',self.hl_user)
                            if len(self.hl_password) == 0:
                                self.hl_password=secret_input('Missing Highlight Password',self.hl_password)
                            if len(self.hl_instance) == 0:
                                self.hl_instance=string_input('Missing Highlight Instance ID',self.hl_instance)
                            else:
                                self.hl_instance=self.hl_instance

                self.log.info(f'Run MRI analysis: {self.is_aip_active}')
                self.log.info(f'Run Highlight analysis: {self.is_hl_active}')
                self._save()

            except JSONDecodeError as e:
                msg = str(e)
                self.log.error(f'Configuration file {self._config_file} must be in a JSON format {msg}')
                exit()

            except ValueError as e:
                msg = str(e)
                self.log.error(msg)
                exit()

    def validate_for_run(self):
        if self.cloc_version == '':
            raise InvalidConfiguration('Missing CLOC executable name')
        exec = abspath(f'{self.base}\\scripts\\{self.cloc_version}')
        if not exists(exec):
            raise InvalidConfiguration(f'CLOC executable not found: {exec}')
        if not self.is_console_active and not self.is_hl_active:
            raise InvalidConfiguration('Both Hightlight and AIP configureations are incomplete, at least one must be')


    def check_default(self,arg_value,cfg_value,default_value) -> bool:
        rtn =  False
        if arg_value is not None: 
            if (cfg_value is None or cfg_value=='') or arg_value != default_value:
                rtn =  True
        return rtn


    def clean_creds(self,value):
        if type(value) is dict:
            for skey, svalue in value.items():  
                if skey=='password' or skey=='user':
                    value[skey]='*******************'
                else:
                    self.clean_creds(svalue)
        return

    def _if_set(self,target,param):
        if param is not None:
            target[0]=param

    def _save(self):
        create_folder(abspath(f'{self.base}/.oneClick'))
        with open(self._config_file, "w") as f:
            dump(self._config, f,indent=4)

    def _set_rest_settings(self,dict):
        for v in ["Active","URL","user","password"]:
            if v not in dict:
                raise ValueError(f"Required field '{v}' is missing from config.json")
    @property
    def rest(self):
        return self._get(self._config,'rest',{})

    def _set_active(self,node,chk_lst):
        chk = True
        for item in chk_lst:
            if item not in node or node[item]=='':
                chk = False
                break
        node['Active']=chk

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

    """ **************** Highlight entries ************************ """
    @property
    def highlight(self):
        if 'Highlight' not in self.rest:
            self.rest['Highlight']={}
            self.highlight['Active']=False
        return self.rest['Highlight']
    @property
    def is_hl_active(self):
        return self.highlight['Active']

    def _set_hl_active(self):
        self._set_active(self.highlight,['URL','cli','perlInstallDir','analyzerDir','user','password','instance'])

    @property
    def hl_url(self):
        return self._get(self.highlight,'URL')
    @hl_url.setter
    def hl_url(self,value):
        if self._set_value(self.highlight,'URL',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_user(self):
        return self._get(self.highlight,'user')
    @hl_user.setter
    def hl_user(self,value):
        if self._set_value(self.highlight,'user',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_password(self):
        return self._get(self.highlight,'password')
    @hl_password.setter
    def hl_password(self,value):
        if self._set_value(self.highlight,'password',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_instance(self):
        return self._get(self.highlight,'instance')
    @hl_instance.setter
    def hl_instance(self,value):
        if self._set_value(self.highlight,'instance',value):
            self._set_hl_active()
            self._save()

    @property
    def hl_cli(self):
        return self._get(self.highlight,'cli')
    @hl_cli.setter
    def hl_cli(self,value):
        if self._set_value(self.highlight,'cli',value):
            self._set_hl_active()
            self._save()

    @property
    def perl_install_dir(self):
        return self._get(self.highlight,'perlInstallDir')
    @perl_install_dir.setter
    def perl_install_dir(self,value):
        if self._set_value(self.highlight,'perlInstallDir',value):
            self._set_hl_active()
            self._save()

    @property
    def analyzer_dir(self):
        return self._get(self.highlight,'analyzerDir')
    @analyzer_dir.setter
    def analyzer_dir(self,value):
        if self._set_value(self.highlight,'analyzerDir',value):
            self._set_hl_active()
            self._save()

    @property
    def is_hl_config_valid(self)->bool:
        if not self.is_hl_active:
            self.log.warning('Highlight analysis is inactive')            
            return True

        is_ok=True
        msg=[]
        if len(self.hl_cli) == 0:
            msg.append('hl_cli')
        if len(self.perlInstallDir) == 0:
            msg.append('perlInstallDir')
        if len(self.analyzerDir) == 0:
            msg.append('analyzerDir')
       
        if len(msg) > 0:
            fmt_msg=', '.join(msg)
            self.log.error(f'Invalid Highlight configuration, missing {fmt_msg} fields')
            is_ok=False

        return is_ok

    """ **************** AIP REST related entries ************************ """
    def _set_aip_active(self,key,value,default=''):
        if self._set_value(self.aip,key,value,default):
            self._set_active(self.aip,['URL','user','password'])
        self._save()

    @property
    def aip(self):
        return self._get(self.rest,'AIP',{})

    @property
    def is_aip_active(self)->bool:
        return self._get(self.aip,'Active',False)

    @property
    def aip_url(self):
        return self._get(self.aip,'URL')
    @aip_url.setter
    def aip_url(self,value):
        self._set_aip_active('URL',value,'')
            
    @property
    def aip_user(self):
        return self._get(self.aip,'user')
    @aip_user.setter
    def aip_user(self,value):
        self._set_aip_active('user',value,'')

    @property
    def aip_password(self):
        return self._get(self.aip,'password')
    @aip_password.setter
    def aip_password(self,value):
        self._set_aip_active('password',value,'')

    """ **************** Console REST related entries ************************ """
    def _set_console_active(self,key,value,default=''):
        if self._set_value(self.console,key,value,default):
            self._set_active(self.console,['URL','API_Key','cli'])
            self._save()

    @property
    def is_console_active(self)->bool:
        return self._get(self.console,'Active',False)

    @property
    def console(self):
        return self._get(self.rest,'AIPConsole',{})

    @property
    def console_url(self)->str:
        return self._get(self.console,'URL')
    @console_url.setter
    def console_url(self,value):
        self._set_console_active('URL',value,'')

    @property
    def console_key(self)->str:
        return self._get(self.console,'API_Key')
    @console_key.setter
    def console_key(self,value):
        self._set_console_active('API_Key',value,'')

    @property
    def console_cli(self):
        return self._get(self.console,'cli')
    @console_cli.setter
    def console_cli(self,value):
        self._set_console_active('cli',value,'')

    @property
    def console_node(self):
        return self._get(self.console,'node')
    @console_node.setter
    def console_node(self,value):
        self._set_console_active('node',value,'')

    @property
    def enable_security_assessment(self):
        return self._get(self.console,'enable-security-assessment')
    @enable_security_assessment.setter
    def enable_security_assessment(self,value):
        self._set_console_active('enable-security-assessment',value,'')

    @property
    def blueprint(self):
        return self._get(self.console,'blueprint')
    @blueprint.setter
    def blueprint(self,value):
        self._set_console_active('blueprint',value,'')

    @property
    def is_console_config_valid(self)->bool:
        if not self.is_console_active:
            self.log.warning('MRI analysis is inactive')            
            return True
        is_ok=True
        msg=[]
        if len(self.console_url) == 0:
            msg.append('URL')
        if len(self.console_key) == 0:
            msg.append('API_Key')
        if len(self.console_cli) == 0:
            msg.append('Console CLI')
       
        if len(msg) > 0:
            fmt_msg=', '.join(msg)
            self.log.error(f'Invalid MRI configuration, missing {fmt_msg} fields')
            is_ok=False

        return is_ok


    """ **************** Action Plan related entries ************************ """
    def _set_database_active(self,key,value,default=''):
        if self._set_value(self.db,key,value,default):
            self._set_active(self.db,['database','user','password','host','port'])
            self._save()

    @property
    def is_db_active(self)->bool:
        return self.db['Active']

    @property
    def db(self):
        return self._get(self._config,'Database',{})

    @property
    def db_database(self):
        return self._get(self.db,'database')
    @db_database.setter
    def db_database(self,value):
        self._set_database_active('database',value,'')

    @property
    def db_user(self):
        return self._get(self.db,'user')
    @db_user.setter
    def db_user(self,value):
        self._set_database_active('user',value,'')

    @property
    def db_password(self):
        return self._get(self.db,'password')
    @db_password.setter
    def db_password(self,value):
        self._set_database_active('password',value,'')
    
    @property
    def db_host(self):
        return self._get(self.db,'host')
    @db_host.setter
    def db_host(self,value):
        self._set_database_active('host',value,'')
    
    @property
    def db_port(self):
        return self._get(self.db,'port')
    @db_port.setter
    def db_port(self,value):
        self._set_database_active('port',value,'')



    """ **************** Project related entries ************************ """
    @property
    def project(self):
        return self._config['project']
    @project.setter
    def project(self,value):
        if type(value) is not str:
            raise ValueError(f'Expecting a the project name, got {type(value)}')

        self.log.info(f'New project: {value}')
        if 'project' not in self._config:
            self._config['project']={}
            self._config['project']['name']=value
            self._config['project']['application']={}

        elif value.lower() != self.project_name.lower():
            raise ValueError("Can't rename a project")

    @property
    def project_name(self):
        return self.project['name']

    @property
    def company_name(self):
        return self.project['company_name']
    @company_name.setter
    def company_name(self,value):
        if value is not None:
            self.project['company_name']=value
            self._save()

    """ **************** Application related entries ************************ """
    @property
    def application(self):
        return self.project['application']
    @application.setter
    def application(self,value:list):
        if type(value) is not list:
            raise ValueError(f'Expecting a list of application names, got {type(value)}')

        update = False
        for appl_name in value:
            if appl_name in self.application.keys():
                pass
            else:
                self.project['application'][appl_name]={'aip':'','hl':''}
                update = True


        # self._config['application']=value
        if update:
            self._save()

    @application.deleter
    def application(self):
        self.project['application']={}

    @property
    def deliver(self):
        return f'{self.base}\\deliver\\{self.project_name}'
    @property
    def work(self):
        return f'{self.base}\\STAGED'
    @property
    def report(self):
        return f'{self.base}\\REPORT'
    @property
    def logs(self):
        return f'{self.base}\\LOGS'
    @property
    def oneclick_work(self):
        return f'{self.base}\\ONECLICK_WORK'

    """ **************** Email related entries ************************ """
    @property 
    def email(self):
        return self._config['email']
    @property
    def from_email_addrs(self):
        return self.email['from']

    @property
    def from_email_passwd(self):
        return self.email['password']

    @property
    def to_email_addrs(self):
        return self.email['to']

    @property
    def email_body(self):
        return self.email['body']     

    @property
    def email_subject(self):
        return self.email['subject'] 

    """ **************** Setting related entries ************************ """
    @property 
    def setting(self):
        return self._get(self._config,'setting',{})        

    @property
    def arg_template(self):
        return self._get(self.setting,'arg-template')

    @property
    def base(self):
        return self._get(self.setting,'base','')
    @base.setter
    def base(self,value):
        if value is not None:
            self.setting['base']=value
            self._save()

    @property
    def cloc_version(self):
        return self._get(self.setting,'cloc_version')
    @cloc_version.setter
    def cloc_version(self,value):
        if self._set_value(self.setting,'cloc_version',value):
            self._save()

    # @property
    # def reset(self):
    #     return self.setting['reset']
    # @reset.setter
    # def reset(self,value):
    #     if value is None:
    #         self.setting['reset']=False
    #     else:
    #         self.setting['reset']=value
    #     self._save()

    @property
    def java_home(self):
        return self._get(self.setting,'java-home')
    @java_home.setter
    def java_home(self,value):
        if self._set_value(self.setting,'java-home',value,''):
            self._save()


def yes_no_input(prompt:str,default_value=True) -> bool:
    while True:
        if default_value:
            default_value='Y'
        else:
            default_value='N'

        val = input(f'{prompt} [{default_value}]?').upper()
        if len(val) == 0: val = default_value

        if val in ['Y','YES']:
            return True
        elif val in ['N','NO']:
            return False
        else:
            print ('Expecting a Y[es] or N[o] response. ',end='')

def folder_input(prompt:str,folder:str='',file:str=None,combine:bool=False) -> str:
    if combine:
        folder=folder.replace(file,'')

    while True:
        i = input(f'{prompt} [{abspath(folder)}]: ')
        if len(i)==0:
            folder = abspath(folder)
        else:
            folder = abspath(i)
        if exists(folder):
            if file is not None:
                if exists(abspath(f'{folder}/{file}')):
                    break
                else:
                    print (f'{folder} folder does not contain {file}, please try again')
                    continue
            else:
                break
        print (f'{folder} not found, please try again')

    if combine:
        folder = abspath(f'{folder}/{file}')
    return folder

def string_input(prompt:str,default_value=""):
    while True:
        if len(default_value)>0:
            i = input(f'{prompt} [{default_value}]: ')
        else:
            i = input(f'{prompt}: ')

        if len(i)==0:
            if len(default_value) == 0:
                print('Input required, please try again')
                continue
            else:
                i = default_value
        return i            

def secret_input(prompt:str,default_value=""):
    while True:
        if len(default_value)>0:
            i = input(f'{prompt} ***********: ')
        else:
            i = input(f'{prompt}: ')

        if len(i)==0:
            if len(default_value) == 0:
                print('Input required, please try again')
                continue
            else:
                i = default_value
        return i            

def url_input(prompt:str,url):
    val = URLValidator()
    while True:
        i = input(f'{prompt} [{url}]: ')
        if len(i)>0:
            url = i
        try:
            val(url)
            return url
        except ValidationError as e:
            print ("Bad URL, please try again")      


#        def _set_value(self,base,key,value,default=''):


    
    # @property
    # def template(self):
    #     return self._config['template']