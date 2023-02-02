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
            dir.extend(dirnames)
        config.application=dirnames

        """create the application folders under 'work'
            base
            |-DELIVER
            |-STAGE
            | |-project
            |   +-application 1
            |   |  +-AIP
            |   |  +-HL
            |   |  +-HL-WORK
            |   +-application 2
            |      +-AIP
            |      +-HL
            |      +-HL-WORK
            |-REPORT
            |     +-application 1
            |     | +-CLOC
            |     | +-ARG
            |     +-application 2
            |       +CLOC
            |       +-ARG
            |-LOGS
            | +-project
            |   +-application 1
            |   +-application 2
        """
        #Finally copy the contents of deliver to work
        cls._log.info('Copying deliver to work')

        for folder in dir:
            src_name = f'{config.deliver}\\{folder}'
            dst_name = f'{config.work}\\{folder}'
            dst_aip_name = f'{dst_name}\\AIP'
            dst_hl_name = f'{dst_name}\\HL'

            # create_folder(abspath(f'{config.output}/{folder}'))
            # create_folder(abspath(f'{config.output}/{folder}/REPORT'))
            # create_folder(abspath(f'{config.output}/{folder}/CLOC'))

            create_folder(dst_name)
#            create_folder(f'{dst_name}\\SQLReport')

            if not exists(dst_aip_name):
                cls._log.info(f'Copy from {src_name} to {dst_aip_name}')
                copytree(src_name,dst_aip_name)
            if not exists(dst_hl_name):
                cls._log.info(f'Copy from {src_name} to {dst_hl_name}')
                copytree(src_name,dst_hl_name)

        cls._log.info('Environment preparation step complete')

        return True
