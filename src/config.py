"""
    Read and validate configuration file
"""
from logging import DEBUG, INFO, WARN, ERROR, info, warn, error
from logger import Logger
from json import load
from argparse import ArgumentParser
from json import JSONDecodeError

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config():
    log = None
    log_translate = {} 
    def __init__(self, config):
        #super().__init__("Config")

        #do all required fields contain data
        try:
            with open(config, 'rb') as config_file:
                self._config = load(config_file)

            if 'rest' not in self._config:
                raise ValueError(f"Required field 'rest' is missing from config.json")

            for v in ['AIP','Highlight']:
                if v not in self._config['rest']:
                    raise ValueError(f"Required field '{v}' is missing from config.json")

            self._rest_settings(self._config['rest']['AIP'])
            self._rest_settings(self._config['rest']['Highlight'])
            if 'instance' not in self._config['rest']['Highlight']:
                raise ValueError(f"Required field 'instance' is missing from config.json")

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
    def hl_active(self):
        return self.rest['Highlight']['Active']

    @property
    def hl_url(self):
        return self.rest['Highlight']['URL']

    @property
    def hl_user(self):
        return self.rest['Highlight']['user']

    @property
    def hl_password(self):
        return self.rest['Highlight']['password']

    @property
    def hl_instance(self):
        return self.rest['Highlight']['instance']
