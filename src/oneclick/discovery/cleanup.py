from datetime import datetime
from os import mkdir,getcwd,walk,remove,chmod,rmdir
from stat import S_IWUSR
from os.path import abspath,join
#from shutil import rmtree
from oneclick.discovery.sourceValidation import SourceValidation
from oneclick.configTest import Config,Status
from cast_common.logger import Logger,INFO
from cast_common.util import create_folder

from pandas import Series,DataFrame

import re 

#todo: review cleanup lists for aip and hl, do we need separate or can we keep it as one and run HL from AIP folder?

class Cleanup(SourceValidation):
    @property
    def choose(self) -> bool:
        return False
    
    @property
    def name(self) -> str:
        return 'Cleanup'

    def __init__(cls):
        pass
    
    @property
    def cleanup_file_prefix(cls):
        return ""

    def run(cls):
        config = cls.config
        config.log.debug('Source Code cleanup in progress')

        #have the minimum requirements been met to run cleanup
        can_run = True
        for appl in config.applist:
            if appl['status']['aip'] < Status.CLOC_PRE_CLEAN_END:
                can_run = False
                break
        if not can_run:
            config.log.info('Cleanup cannot run, please run "Technology Discovery - Before Cleanup" step first')
            return False

        # for app in config.applist:
        #     app_status = app['status']
        #     if app_status['aip'] < Status.SOURCE_CLEAN_START:
        #         app['deleted'] = {'folders': 0, 'files': 0}


        output_path = abspath(f'{config.log_folder}/{config.project_name}')

        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        
        exclusionFileList= abspath(f'{config.base}/scripts/{cls.cleanup_file_prefix}deleteFileList.txt')
        with open(exclusionFileList) as f:
            files_list = f.read().splitlines()

        exclusionFolderList= abspath(f'{config.base}/scripts/{cls.cleanup_file_prefix}deleteFolderList.txt')
        with open(exclusionFolderList) as f:
            folder_list = f.read().splitlines()

        apps = config.applist
        # cls._log.info(f'Running {cls.__class__.__name__} for all applications')

        for app in apps:
            app_status = app['status']
            if app_status['aip'] < Status.UNPACK_END:
                config.log.info(f'Cleanup cannot run, please run "Source Code Discovery - Unpack" step first')
                return False
            
            if app_status['aip'] < Status.SOURCE_CLEAN_START:
                app_status['aip'] = app_status['highlight'] = Status.SOURCE_CLEAN_START

        print(cls.show_progress())

        for app in apps:
            app_name = app['name']
            if 'deleted' not in app:
                app['deleted'] = {'folders': 0, 'files': 0}

            deleted=app['deleted']                

            if app_status['aip'] >= Status.SOURCE_CLEAN_END:
                continue 

            if type(deleted['folders']) is str:
                deleted['folders']=0

            if type(deleted['files']) is str:
                deleted['files']=0

            deleted_files = deleted['files']
            deleted_folders = deleted['folders']

            app['status']['aip'] = app['status']['highlight'] = Status.SOURCE_CLEAN_START

            log_folder=abspath(f'{config.log_folder}/{config.project_name}/{app_name}/cleanup')
            create_folder(log_folder)

            cleanup_log_file= abspath(f"{log_folder}/{file_suffix}.log")
            cls.cleanup_log = Logger('File',level=config.log_level,file_name=cleanup_log_file,console_output=False)
            cls.cleanup_log.info(f'{config.project_name}/{app}')
            # cls._log.info(f'Cleanup file log: {cleanup_log_file}')

            app_folder = abspath(f'{config.stage_folder}\\{config.project_name}\\{app_name}')

            # cls._log.info(f'Reviewing {app} ({app_folder})')
            # with open (clean_up_log_file, 'a+') as file1: 
            #     with open (clean_up_log_folder, 'a+') as file2: 

            s=''                            

            cls.cleanup_log.info('Cleaning Folders')
            for subdir, dirs, files in walk(app_folder):
                for dir in dirs:
                    cls.cleanup_log.info(f'{subdir}\\{dir}')
                    if cls.find_with_list(dir,folder_list):
                        folder=join(subdir, dir)
                        rmtree(folder)
                        deleted_folders+=1
                        deleted['folders'] += 1
                        cls.cleanup_log.info(f'Removing Folder: {folder}')
                        found=True
                print(cls.show_progress())

            cls.cleanup_log.info('Cleaning Files')
            for subdir, dirs, files in walk(app_folder):
                for file in files:
                    cls.cleanup_log.info(f'{subdir}\\{dir}')
                    if cls.find_with_list(file,files_list):
                        file=join(subdir, file)
                        remove(file)
                        deleted_files+=1
                        deleted['files'] += 1
                        cls.cleanup_log.info(f'Removing File: {file}')
                        found=True
                print(cls.show_progress())

            # cls._log.info(f'Removed {deleted_files} files and {deleted_folders} folders from {app_folder}')
            # cls.log.info(f'Application {app}, removed {deleted_files} files and {deleted_folders} folders')               
            # cls.log.info(f'Cleanup log: {cleanup_log_file}\n')
    
            print(cls.show_progress())

        for app in apps:
            app_status = app['status']
            app_status['aip'] = app_status['highlight'] = Status.SOURCE_CLEAN_END

        config._save()
        cls.show_progress(done=True)
        config.log.info('Source Code cleanup done')
        return True

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

    chmod(top, S_IWUSR)
    rmdir(top)    

class cleanUpHL(Cleanup):
    def __init__(cls,config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

    @property
    def cleanup_file_prefix(cls):
        return "HL"
    
    def get_title(cls) -> str:
        return "CLEANUP FOR CAST HIGHLIGHT"
