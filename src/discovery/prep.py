from logger import Logger
from os import mkdir,walk,listdir
from os.path import exists
from shutil import copytree,rmtree

from sourceValidation import SourceValidation 
from config import Config

class Prepare(SourceValidation):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        pass

    def run(cls,config:Config):
        cls._log.info('Running environment preparation step')
        deliver_folder = f'{config.base}\\deliver\\{config.project}'        
        work_folder = f'{config.base}\\work\\{config.project}'        

        """is the minimal enviroment configured
            base
            |-deliver
              |-project
                |-application 1
                |-application 2
                |-application ...
        """
        cls._log.info('Creating destination folder structure')
        if not exists(deliver_folder):
            raise ValueError(f'{deliver_folder} does not exist')
        if not exists(work_folder):
            mkdir (work_folder)


        #scan delivery folder for application folders
        dir=[]
        for (dirpath,dirnames,filenames) in walk(deliver_folder,topdown=False):
            dir.extend(dirnames)
        config.application=dirnames

        """create the application folders under 'work'
            base
            |-work
              |-project
                |-application 1
                  |-AIP
                  |-HL
                |-application 2
                  |-AIP
                  |-HL
                |-application ...

        """
        for folder in dir:
            name = f'{work_folder}\\{folder}'
            _mkdir (name)

        #Finally copy the contents of deliver to work
        cls._log.info('Copying deliver to work')
        for folder in dir:
            src_name = f'{deliver_folder}\\{folder}'
            dst_name = f'{work_folder}\\{folder}'
            dst_aip_name = f'{dst_name}\\AIP'
            dst_hl_name = f'{dst_name}\\HL'

            if config.reset:
                if exists (dst_name):
                    cls._log.info(f'-reset flag set, {dst_name} destination before copy')
                    rmtree(dst_name)

            if not exists(dst_aip_name):
                cls._log.info(f'Copy from {src_name} to {dst_aip_name}')
                copytree(src_name,dst_aip_name)
            if not exists(dst_hl_name):
                cls._log.info(f'Copy from {src_name} to {dst_hl_name}')
                copytree(src_name,dst_hl_name)

        cls._log.info('Environment preparation step complete')

        return True



def _mkdir(folder:str):
    if not exists(folder):
        mkdir(folder)

