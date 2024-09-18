from cast_common.logger import Logger
from cast_common.util import create_folder
from os import mkdir,walk,listdir
from os.path import exists,abspath,isdir
from shutil import copytree,rmtree
from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config
from oneclick.exceptions import InvalidConfiguration

from tqdm import tqdm

class Prepare(SourceValidation):

    def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)
        pass

    def run(cls,config:Config):
        no_of_apps = len(config.application)

        cls._log.info(f'Executing analysis for project {config.project_name}')
        cls.log.info(f'    With {no_of_apps} application(s).')

        if config.start == 'Discovery':
            discovery_flag = True
        else:
            discovery_flag = False

        cls.log.info(f'    Source Code Unzip, Cleanup and Discovery - {discovery_flag}')
        cls.log.info(f'    Run MRI analysis: {config.is_aip_active}')
        cls.log.info(f'    Run Highlight analysis: {config.is_hl_active}')
 
        """is the minimal enviroment configured
            base
            |-.oneClick
            |-deliver
              |-project
                |-application 1
                |-application 2
                |-application ...
        """
        cls.log.info('Creating destination folder structure')
        if not exists(config.deliver):
            raise ValueError(f'{config.deliver} does not exist')

        #scan delivery folder for application folders
        dir=[]
        deliver = abspath(config.deliver)
        dirnames = listdir(deliver) 

        # for (dirpath,dirnames,filenames) in walk(deliver,topdown=False):
        #     level = dirpath.replace(deliver,'')
        #     dir.extend(dirnames)
        #config.application.clear()
        config.application=dirnames

        #Finally copy the contents of deliver to work
        cls.log.info('Copy all files in deliver to staging')

        # for folder in tqdm(dirnames,desc='Preparing applications'):
        dst_project=f'{config.work}\\{config.project_name}'
        create_folder(dst_project)

        for folder in dirnames:

            src_name = abspath(f'{config.deliver}\\{folder}')
            dst_app=f'{dst_project}\\{folder}'
            cls.log.info(f'    From {src_name} to {dst_app}')

            if isdir (src_name):
                if not exists(dst_app):
                    copytree(src_name,dst_app)
            else: # the project can only contain application folders, no files allowed
                raise InvalidConfiguration(f'No applications found in project {config.project_name}')

        cls.log.info(f'Environment preparation complete for project {config.project_name}')

        return True

    def get_title(cls) -> str:
        return "PREPARE"