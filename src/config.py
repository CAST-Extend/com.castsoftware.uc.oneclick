"""
    Read and validate configuration file
"""
from logging import DEBUG, INFO, WARN, ERROR, info, warn, error
from logger import Logger
from json import load
from argparse import ArgumentParser
from json import JSONDecodeError,dump

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config():
    log = None
    log_translate = {} 
    def __init__(self, config='config.json',log_level: int=INFO):
        self.log = Logger(self.__class__.__name__,log_level)

        #do all required fields contain data
        try:
            with open(config, 'rb') as config_file:
                self._config = load(config_file)
                config_file.close()

            self._config_file = config

            if 'rest' not in self._config:
                raise ValueError(f"Required field 'rest' is missing from config.json")

            for v in ['AIP','highlight']:
                if v not in self._config['rest']:
                    raise ValueError(f"Required field '{v}' is missing from config.json")

            self._rest_settings(self._config['rest']['AIP'])
            self._rest_settings(self._config['rest']['highlight'])
            if 'instance' not in self._config['rest']['highlight']:
                raise ValueError(f"Required field 'instance' is missing from config.json")

            if 'setting' not in self._config:
                self._config['setting']={}
            if 'application' not in self._config:
                self._config['application']=[]
            

        except JSONDecodeError as e:
            msg = str(e)
            self.error('Configuration file must be in a JSON format')
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
        with open(self._config_file, "w") as f:
            dump(self._config, f,indent=4)
            f.close()

    @property
    def highlight(self):
        return self.rest['highlight']
    @property
    def hl_active(self):
        return self.highlight['Active']

    @property
    def hl_url(self):
        return self.highlight['URL'] 
    @hl_url.setter
    def hl_url(self,value):
        self.highlight['URL']=value
        self._save()

    @property
    def hl_user(self):
        return self.highlight['user']  
    @hl_user.setter
    def hl_user(self,value):
        self.highlight['user']=value
        self._save()

    @property
    def hl_password(self):
        return self.highlight['password']   
    @hl_password.setter
    def hl_password(self,value):
        self.highlight['password']=value
        self._save()

    @property
    def hl_instance(self):
        return self.highlight['instance']   
    @hl_instance.setter
    def hl_instance(self,value):
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

    @property
    def project(self):
        return self._config['project']
    @project.setter
    def project(self,value):
        self._config['project']=value
        self._save()

    @property
    def application(self):
        return self._config['application']
    @application.setter
    def application(self,value):
        self._config['application']=value
        self._save()

    @property
    def base(self):
        return self._config['base']
    @base.setter
    def base(self,value):
        self._config['base']=value
        self._save()

    @property
    def reset(self):
        return self._config['setting']['restart']
    @reset.setter
    def reset(self,value):
        if value is None:
            self._config['setting']['restart']=False
        else:
            self._config['setting']['restart']=value
        self._save()

    @property
    def java_home(self):
        return self.settings['java_home']

    @property
    def rest(self):
        return self._config['rest']

    @property
    def aip_active(self):
        return self.rest['AIP']['Active']

    @property
    def aip_url(self):
        return self.rest['AIP']['URL']

    @property
    def aip_user(self):
        return self.rest['AIP']['user']

    @property
    def aip_password(self):
        return self.rest['AIP']['password']

    @property
    def aip_key(self):
        return self.rest['AIP']['api_key']

    @property
    def aip_cli(self):
        return self.rest['AIP']['aip_cli']

    @property
    def node_name(self):
        return self.rest['AIP']['node_name']    