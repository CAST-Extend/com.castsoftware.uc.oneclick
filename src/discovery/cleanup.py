from datetime import datetime
from os import mkdir,getcwd,walk,remove
from os.path import abspath,join
from shutil import rmtree
from discovery.sourceValidation import SourceValidation
from config import Config
from logger import INFO
from util import create_folder

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
        
        output_path = f'{config.logs}'    
        create_folder(output_path)

        dir = getcwd()
        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        
        exclusionFileList= f'{dir}\\scripts\\{cls.cleanup_file_prefix}deleteFileList.txt'
        with open(exclusionFileList) as f:
            files_list = f.read().splitlines()
            f.close()

        exclusionFolderList= f'{dir}\\scripts\\{cls.cleanup_file_prefix}deleteFolderList.txt'
        with open(exclusionFolderList) as f:
            folder_list = f.read().splitlines()
            f.close()

        apps= config.application
        cls._log.info(f'Running {cls.__class__.__name__} for all applications')
        found = True
        while found:
            found = False
            for app in apps:
                clean_up_log_file= f"{output_path}\\{cls.cleanup_file_prefix}{config.project_name}_{app}_deletedFiles_{file_suffix}.txt"
                clean_up_log_folder= f"{output_path}\\{cls.cleanup_file_prefix}{config.project_name}_{app}_deletedFolders_{file_suffix}.txt"

                app_folder = f'{config.work}\\{app}\\{cls.cleanup_file_prefix}'

                with open (clean_up_log_folder, 'a+') as file2: 
                    s=''
                        
                    count=0
                    for subdir, dirs, files in walk(app_folder):
                            for dir in dirs:
                                if dir in folder_list:
                                    folder=join(subdir, dir)
                                    rmtree(folder)
                        
                                    s=str(count)+") Removed folder -> "+folder
                                    count+=1
                                    file2.write(s)
                                    file2.write('\n') 
                    file2.close()
                cls._log.info(f'Removed {count} unwanted folders from {app_folder}')
                if count > 0:
                    config.application[app]['aip']=""
                    config._save()

                with open (clean_up_log_file, 'a+') as file1: 
                    s=''
                    count=0
                    for subdir, dirs, files in walk(app_folder):
                        for file in files:
                            fileN=join(subdir, file) 
                            for fileName in files_list:
                                
                                if fileN.endswith(fileName):
                                    remove(fileN)
                                
                                    s=str(count)+") Removed file -> "+fileN
                                    count+=1
                                    file1.write(s)
                                    file1.write('\n') 
                    file1.close()
                cls._log.info(f'Removed {count} unwanted files from {app_folder}')
                if count > 0:
                    config.application[app]['aip']=""
                    config._save()

        cls._log.debug('Source Code cleanup done')


class cleanUpHL(cleanUpAIP):
    def __init__(cls,config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return "HL"
