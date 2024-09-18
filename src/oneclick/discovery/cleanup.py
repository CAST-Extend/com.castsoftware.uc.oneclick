from datetime import datetime
from os import mkdir,getcwd,walk,remove,chmod,rmdir
from stat import S_IWUSR
from os.path import abspath,join
#from shutil import rmtree
from oneclick.discovery.sourceValidation import SourceValidation
from oneclick.config import Config
from cast_common.logger import Logger,INFO
from cast_common.util import create_folder

from pandas import Series,DataFrame

import re 

#todo: review cleanup lists for aip and hl, do we need separate or can we keep it as one and run HL from AIP folder?

class Cleanup(SourceValidation):

    def __init__(cls, config:Config, name = None, log_level:int=INFO):
        if name is None: 
            name = cls.__class__.__name__
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return ""

    def run(cls,config:Config):
        cls._log.debug('Source Code cleanup in progress')
        
        output_path = abspath(f'{config.logs}/{config.project_name}')

        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        
        exclusionFileList= abspath(f'{config.base}/scripts/{cls.cleanup_file_prefix}deleteFileList.txt')
        with open(exclusionFileList) as f:
            files_list = f.read().splitlines()

        exclusionFolderList= abspath(f'{config.base}/scripts/{cls.cleanup_file_prefix}deleteFolderList.txt')
        with open(exclusionFolderList) as f:
            folder_list = f.read().splitlines()

        apps= config.application
        # cls._log.info(f'Running {cls.__class__.__name__} for all applications')
        found = True
        while found:
            found = False
            for app in apps:
                log_folder=abspath(f'{output_path}/{app}/cleanup')
                create_folder(log_folder)

                cleanup_log_file= abspath(f"{log_folder}/{file_suffix}.log")
                cls.cleanup_log = Logger('File',level=cls._log_level,file_name=cleanup_log_file,console_output=False)
                cls.cleanup_log.info(f'{config.project_name}/{app}')
                # cls._log.info(f'Cleanup file log: {cleanup_log_file}')

                app_folder = abspath(f'{config.work}\\{config.project_name}\\{app}')

                # cls._log.info(f'Reviewing {app} ({app_folder})')
                # with open (clean_up_log_file, 'a+') as file1: 
                #     with open (clean_up_log_folder, 'a+') as file2: 

                s=''                            
                folder_cnt=0
                file_cnt=0

                cls.cleanup_log.info('Cleaning Folders')
                cls.log.info('Cleaning Folders')
                for subdir, dirs, files in walk(app_folder):
                        for dir in dirs:
                            cls.cleanup_log.info(f'{subdir}\\{dir}')
                            if cls.find_with_list(dir,folder_list):
                                folder=join(subdir, dir)
                                rmtree(folder)
                                folder_cnt+=1
                                cls.cleanup_log.info(f'Removing Folder: {folder}')

                cls.cleanup_log.info('Cleaning Files')
                cls.log.info('Cleaning Folders')
                for subdir, dirs, files in walk(app_folder):
                        for file in files:
                            cls.cleanup_log.info(f'{subdir}\\{dir}')
                            if cls.find_with_list(file,files_list):
                                file=join(subdir, file)
                                remove(file)
                                file_cnt+=1
                                cls.cleanup_log.info(f'Removing File: {file}')

                # cls._log.info(f'Removed {file_cnt} files and {folder_cnt} folders from {app_folder}')
                cls.log.info(f'Application {app}, removed {file_cnt} files and {folder_cnt} folders')               
                cls.log.info(f'Cleanup log: {cleanup_log_file}\n')
        cls._log.debug('Source Code cleanup done')

    def find_with_list(cls,find_in:str,pattern:list):
        rslt = False
        for p in pattern:
            try:
                if re.match(p,find_in):
                    rslt = True
                cls.cleanup_log.info(f'looking in {find_in} folder for {p} ({rslt})')
                if rslt:
                    break

            except re.error as ex:
                cls._log.warning(f'{ex.msg} for pattern {ex.pattern}')
            
        return rslt

    def get_title(cls) -> str:
        return "CLEANUP"

def rmtree(top):
    for root, dirs, files in walk(top, topdown=False):
        for name in files:
            filename = join(root, name)
            chmod(filename, S_IWUSR)
            remove(filename)
        for name in dirs:
            rmdir(join(root, name))
    rmdir(top)    

class cleanUpHL(Cleanup):
    def __init__(cls,config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return "HL"
    
    def get_title(cls) -> str:
        return "CLEANUP FOR CAST HIGHLIGHT"
