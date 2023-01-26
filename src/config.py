"""
    Read and validate configuration file
"""
from logging import DEBUG, INFO, WARN, ERROR, info, warn, error
from logger import Logger
from json import load
from argparse import ArgumentParser
from json import JSONDecodeError,dump
from os.path import abspath,exists
from util import create_folder

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config():
    log = None
    log_translate = {} 
    def __init__(self,base_folder:str,project_name,config='config.json',log_level: int=INFO):
        self.log = Logger(self.__class__.__name__,log_level)

        #do all required fields contain data
        try:
            config_loc = abspath(f'{base_folder}/.oneclick/{project_name}.json')
            if not exists(config_loc):
                self._config_file=abspath('./config.json')
            else:
                self._config_file=config_loc
            with open(abspath(self._config_file), 'rb') as config_file:
                self._config = load(config_file)
                config_file.close()

            self.base = base_folder
            self.project = project_name

            if 'rest' not in self._config:
                raise ValueError(f"Required field 'rest' is missing from config.json")

            for v in ['AIP','Highlight','AIPConsole']:
                if v not in self._config['rest']:
                    raise ValueError(f"Required field '{v}' is missing from config.json")

            self._rest_settings(self.aip)#  config['rest']['AIP'])
            self._rest_settings(self.highlight)# _config['rest']['highlight'])
            if 'instance' not in self.highlight: #_config['rest']['highlight']:
                raise ValueError(f"Required field 'instance' is missing from config.json")

            if 'setting' not in self._config:
                self._config['setting']={}

            self._config_file = config_loc
            self._save()


        except JSONDecodeError as e:
            msg = str(e)
            self.log.error(f'Configuration file {self._config_file} must be in a JSON format {msg}')
            exit()

        except ValueError as e:
            msg = str(e)
            self.log.error(msg)
            exit()

    def _rest_settings(self,dict):
        for v in ["Active","URL","user","password"]:
            if v not in dict:
                raise ValueError(f"Required field '{v}' is missing from config.json")

    def _save(self):
        create_folder(abspath(f'{self.base}/.oneClick'))
        with open(self._config_file, "w") as f:
            dump(self._config, f,indent=4)
            f.close()

    """ **************** Highlight entries ************************ """
    @property
    def highlight(self):
        return self.rest['Highlight']
    @property
    def hl_active(self):
        return self.highlight['Active']

    @property
    def hl_url(self):
        return self.highlight['URL'] 
    @hl_url.setter
    def hl_url(self,value):
        if value is not None:
            self.highlight['URL']=value
            self._save()

    @property
    def hl_user(self):
        return self.highlight['user']  
    @hl_user.setter
    def hl_user(self,value):
        if value is not None:
            self.highlight['user']=value
            self._save()

    @property
    def hl_password(self):
        return self.highlight['password']   
    @hl_password.setter
    def hl_password(self,value):
        if value is not None:
            self.highlight['password']=value
            self._save()

    @property
    def hl_instance(self):
        return self.highlight['instance']   
    @hl_instance.setter
    def hl_instance(self,value):
        if value is not None:
            self.highlight['instance']=value
            self._save()

    @property
    def hl_cli(self):
        return self.highlight['cli']

    @property
    def perlInstallDir(self):
        return self.highlight['perlInstallDir']

    @property
    def analyzerDir(self):
        return self.highlight['analyzerDir']

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

        elif value != self.project_name:
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
        return f'{self.base}\\STAGED\\{self.project_name}'
    @property
    def report(self):
        return f'{self.base}\\REPORT'
    @property
    def logs(self):
        return f'{self.base}\\LOGS'

    """ **************** Setting related entries ************************ """
    @property 
    def setting(self):
        return self._config['setting']

    @property
    def from_email_addrs(self):
        return self.setting['from-email-addrs']

    @property
    def from_email_passwd(self):
        return self.setting['from-email-passwd']

    @property
    def to_email_addrs(self):
        return self.setting['to-email-addrs']

    @property
    def email_body(self):
        return self.setting['email-body']     

    @property
    def email_subject(self):
        return self.setting['email-subject'] 

    @property
    def arg_template(self):
        return self.setting['arg-template']

    @property
    def base(self):
        return self.setting['base']
    @base.setter
    def base(self,value):
        if value is not None:
            self.setting['base']=value
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
        return self.setting['java_home']

    """ **************** AIP REST related entries ************************ """
    @property
    def rest(self):
        return self._config['rest']

    @property
    def aip(self):
        return self.rest['AIP']

    @property
    def aip_active(self)->bool:
        return self.aip['Active']

    @property
    def aip_url(self):
        return self.aip['URL']
    @aip_url.setter
    def aip_url(self,value):
        if value is not None:
            self.aip['URL']=value
            self._save()
            
    @property
    def aip_user(self):
        return self.aip['user']
    @aip_user.setter
    def aip_user(self,value):
        if value is not None:
            self.aip['user']=value
            self._save()

    @property
    def aip_password(self):
        return self.aip['password']
    @aip_password.setter
    def aip_password(self,value):
        if value is not None:
            self.aip['password']=value
            self._save()

    """ **************** Console REST related entries ************************ """
    @property
    def console(self):
        return self.rest['AIPConsole']

    def cosole_active(self)->bool:
        return self.console['Active']

    @property
    def console_url(self)->str:
        return self.console['URL']
    @console_url.setter
    def console_url(self,value):
        if value is not None:
            self.console['URL']=value
            self._save()

    @property
    def console_key(self)->str:
        return self.console['API_Key']
    @console_key.setter
    def console_key(self,value):
        if value is not None:
            self.console['API_Key']=value
            self._save()

    @property
    def aip_cli(self):
        return self.console['cli']

    @property
    def node_name(self):
        if self.console['node'] is None or len(self.console['node'])==0:
            return 'local'
        return self.console['node']   

    """ **************** Action Plan related entries ************************ """
    @property
    def database(self):
        return self._config['Database']['database']
    @database.setter
    def database(self,value):
        if value is not None:
            self._config['Database']['database']=value
            self._save()

    @property
    def user(self):
        return self._config['Database']['user']
    @user.setter
    def user(self,value):
        if value is not None:
            self._config['Database']['user']=value
            self._save()

    @property
    def password(self):
        return self._config['Database']['password']
    @password.setter
    def password(self,value):
        if value is not None:
            self._config['Database']['password']=value
            self._save()
    
    @property
    def host(self):
        return self._config['Database']['host']
    @host.setter
    def host(self,value):
        if value is not None:
            self._config['Database']['host']=value
            self._save()
    
    @property
    def port(self):
        return self._config['Database']['port']
    @port.setter
    def port(self,value):
        if value is not None:
            self._config['Database']['port']=value
            self._save()
    
    # @property
    # def template(self):
    #     return self._config['template']