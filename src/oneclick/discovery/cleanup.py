from datetime import datetime
from os import mkdir,getcwd,walk,remove,chmod,rmdir
from stat import S_IWUSR
from os.path import abspath,join
#from shutil import rmtree
from oneclick.discovery.sourceValidation import SourceValidation
from oneclick.config import Config
from cast_common.logger import Logger,INFO
from cast_common.util import create_folder
from tqdm import tqdm

from pandas import Series,DataFrame

import re 

#todo: review cleanup lists for aip and hl, do we need separate or can we keep it as one and run HL from AIP folder?

class cleanUpAIP(SourceValidation):

    def __init__(cls, config:Config, name = None, log_level:int=INFO):
        if name is None: 
            name = cls.__class__.__name__
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return "AIP"

    def run(cls,config:Config):
        cls._log.debug('Source Code cleanup is in progress')
        
        output_path = abspath(f'{config.oneclick_work}/LOGS/{config.project_name}')
        create_folder(output_path)

        dir = config.base
        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        
        exclusionFileList= abspath(f'{dir}\\scripts\\{cls.cleanup_file_prefix}deleteFileList.txt')
        with open(exclusionFileList) as f:
            files_list = f.read().splitlines()
            f.close()

        exclusionFolderList= abspath(f'{dir}\\scripts\\{cls.cleanup_file_prefix}deleteFolderList.txt')
        with open(exclusionFolderList) as f:
            folder_list = f.read().splitlines()
            f.close()

        apps= config.application
        cls._log.info(f'Running {cls.__class__.__name__} for all applications')
        found = True
        while found:
            found = False
            for app in tqdm(apps, desc='Processing apps'):
                create_folder(f'{output_path}\\{app}')
                base = f'{output_path}\\{app}\\{cls.cleanup_file_prefix}{config.project_name}_{app}'
                clean_up_log_file= f"{base}_deletedFiles_{file_suffix}.txt"
                clean_up_log_folder= f"{base}_deletedFolders_{file_suffix}.txt"

                app_folder = abspath(f'{config.work}\\{cls.cleanup_file_prefix}\\{config.project_name}\\{app}')
                cls._log.info(f'Reviewing {app} ({app_folder})')
                with open (clean_up_log_file, 'a+') as file1: 
                    with open (clean_up_log_folder, 'a+') as file2: 
                        s=''                            
                        folder_cnt=0
                        file_cnt=0
                        for subdir, dirs, files in tqdm(walk(app_folder), desc=f'Processing {app} files and folders'):
                                for dir in dirs:
                                    if cls.find_with_list(dir,folder_list):
                                        folder=join(subdir, dir)
                                        rmtree(folder)
                                        folder_cnt+=1
                                        log_it('folder',folder,file2)

                                for file in files:
                                    if cls.find_with_list(file,files_list):
                                        file=join(subdir, file)
                                        remove(file)
                                        file_cnt+=1
                                        log_it('file',file,file1)

                # cls._log.info(f'Reviewing {app} ({app_folder})')
                # with open (clean_up_log_file, 'a+') as file1: 
                #     with open (clean_up_log_folder, 'a+') as file2: 

                s=''                            
                folder_cnt=0
                file_cnt=0
                for subdir, dirs, files in walk(app_folder):
                        for dir in dirs:
                            if cls.find_with_list(dir,folder_list):
                                folder=join(subdir, dir)
                                rmtree(folder)
                                folder_cnt+=1
                                cls.cleanup_log.info(f'Folder: {folder}')

                        for file in files:
                            if cls.find_with_list(file,files_list):
                                file=join(subdir, file)
                                remove(file)
                                file_cnt+=1
                                cls.cleanup_log.info(f'Folder: {file}')

                cls._log.info(f'Removed {file_cnt} files and {folder_cnt} folders from {app_folder}')
        cls._log.debug('Source Code cleanup done')

    def find_with_list(cls,find_in:str,pattern:list):
        rslt = False
        for p in pattern:
            try:
                cls.cleanup_log.debug(f'matching: {p} in: {find_in}')
                if re.match(p,find_in):
                    rslt = True
                    break
            except re.error as ex:
                cls._log.warning(f'{ex.msg} for pattern {ex.pattern}')
            
        return rslt

def rmtree(top):
    for root, dirs, files in walk(top, topdown=False):
        for name in files:
            filename = join(root, name)
            chmod(filename, S_IWUSR)
            remove(filename)
        for name in dirs:
            rmdir(join(root, name))
    rmdir(top)    

class cleanUpHL(cleanUpAIP):
    def __init__(cls,config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return "HL"
