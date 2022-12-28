from logger import Logger
from os import mkdir,walk,listdir
from os.path import exists
from shutil import copytree,rmtree

from discovery.sourceValidation import SourceValidation 
from config import Config
from util import create_folder

class Prepare(SourceValidation):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    def run(cls,config:Config):
        cls._log.debug('Running environment preparation step')

        if config.reset:
          del config.application

        """is the minimal enviroment configured
            base
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
            |-work
              |-project
                |-application 1
                  |-Cloc
                  |-AIP
                  |-HL
                |-application 2
                  |-Cloc
                  |-AIP
                  |-HL
                |-application ...

        """
        if config.reset:
            if exists (config.work):
                cls._log.info(f'-reset flag set, {config.work} destination before copy')
                rmtree(config.work)

        #Finally copy the contents of deliver to work
        cls._log.info('Copying deliver to work')
        create_folder(f'{config.base}\\work')
        create_folder(config.work)
        for folder in dir:
            src_name = f'{config.deliver}\\{folder}'
            dst_name = f'{config.work}\\{folder}'
            dst_aip_name = f'{dst_name}\\AIP'
            dst_hl_name = f'{dst_name}\\HL'

            create_folder(dst_name)
            create_folder(f'{dst_name}\\CLOC')
            create_folder(f'{dst_name}\\SQLReport')

            if not exists(dst_aip_name):
                cls._log.info(f'Copy from {src_name} to {dst_aip_name}')
                copytree(src_name,dst_aip_name)
            if not exists(dst_hl_name):
                cls._log.info(f'Copy from {src_name} to {dst_hl_name}')
                copytree(src_name,dst_hl_name)

        cls._log.info('Environment preparation step complete')

        return True
