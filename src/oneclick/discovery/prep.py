from cast_common.logger import Logger
from cast_common.util import create_folder
from os import mkdir,walk
from os.path import exists,abspath
from shutil import copytree,rmtree
from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config

class Prepare(SourceValidation):

    def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)
        pass

    def run(cls,config:Config):
        cls._log.info('')
        cls._log.info('****************** Source Code Validation Log *********************')
        cls._log.info(f'Running {cls.__class__.__name__} for all applications')

        """is the minimal enviroment configured
            base
            |-.oneClick
            |-deliver
              |-project
                |-application 1
                |-application 2
                |-application ...
        """
        cls._log.info('Creating destination folder structure')
        if not exists(config.deliver):
            raise ValueError(f'{config.deliver} does not exist')

        #scan delivery folder for application folders
        dir=[]
        for (dirpath,dirnames,filenames) in walk(config.deliver,topdown=False):
            p = abspath(dirpath).replace(abspath(config.deliver),'')
            dir.append(p)
#            dir.extend(dirpath)
        config.application=dirnames

        #Finally copy the contents of deliver to work
        cls._log.info('Copying deliver to work')

        for folder in dir:
            src_name = abspath(f'{config.deliver}{folder}')
            dst_aip_name = abspath(f'{config.work}\\AIP')
            dst_hl_name = abspath(f'{config.work}\\HL')
            create_folder(dst_aip_name)
            create_folder(dst_hl_name)

            # create_folder(abspath(f'{config.output}/{folder}'))
            # create_folder(abspath(f'{config.output}/{folder}/REPORT'))
            # create_folder(abspath(f'{config.output}/{folder}/CLOC'))


            dst_aip_project=f'{dst_aip_name}\\{config.project_name}'
            dst_hl_project=f'{dst_hl_name}\\{config.project_name}'
            create_folder(dst_aip_project)
            create_folder(dst_hl_project)

            dst_aip_app=f'{dst_aip_project}\\{folder}'
            dst_hl_app=f'{dst_hl_project}\\{folder}'

            #create_folder(f'{dst_name}\\SQLReport')

            if not exists(dst_aip_app):
                cls._log.info(f'Copy from {src_name} to {dst_aip_app}')
                copytree(src_name,dst_aip_app)
            if not exists(dst_hl_app):
                cls._log.info(f'Copy from {src_name} to {dst_hl_app}')
                copytree(src_name,dst_hl_app)

        cls._log.info('Environment preparation step complete')

        return True
