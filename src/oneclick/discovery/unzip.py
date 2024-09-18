from os import walk,remove,stat
from os.path import abspath,exists

#from shutil import unpack_archive
#from pyunpack import Archive,ZipFile,error
from zipfile import ZipFile,BadZipFile
from gzip import open as gz
from tarfile import open as tar, TarError
from shutil import copyfileobj
from tqdm.auto import tqdm
from cast_common.util import create_folder
from cast_common.logger import Logger
from datetime import datetime

from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config


class Unzip(SourceValidation):
   skip = ['__MACOSX','.DS_Store']

   def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

   def unzip(cls,src_fldr:str) -> tuple[bool,int,int]:
      unarchived_files = 0
      archived_files = 0
      error = False
      found = True

      loop = 0
      while found:
         loop +=1
         cls.zip_log.info(f'Pass {loop}')
         
         found = False
         for root, dirs, files in tqdm(walk(src_fldr), leave=False, position=1):
            try:
               if '__MACOSX' in root or '.DS_Store' in files:
                  continue
               for file in files:
                  full_name = abspath(f'{root.strip()}\\{file}')
                  dest = full_name.replace(f".{full_name.split('.')[-1]}",'')

                  file_type=''
                  if file.endswith(".gz"):
                     archived_files += 1
                     found=True
                     file_type = 'Gnu Zip'
                     with gz(full_name, 'rb') as f_in:
                        if not exists(dest):
                           with open(dest, 'wb') as f_out:
                              copyfileobj(f_in, f_out)               

                  elif file.endswith(".tar") or \
                       file.endswith(".gztar") or \
                       file.endswith(".bztar") or \
                       file.endswith(".tgz"):
                     with tar(full_name) as f_in:
                        archived_files += 1
                        found=True
                        file_type = 'Tape Archive (tar)'
                        create_folder(dest)
                        f_in.extractall(dest)

                  elif file.endswith(".7z") or file.endswith(".zip") :
                     archived_files += 1
                     found=True
                     file_type = 'zip archive'
                     full_name = abspath(f'{root.strip()}\\{file}')
                     create_folder(dest)
                     with ZipFile(full_name) as zf:
                        for member in tqdm(zf.infolist(), desc=f'Extracting {full_name}',position=0,leave=False):
                           zf.extract(member, dest)
                     #Archive(full_name).extractall(dest,auto_create_dir=True)

                  else:
                     unarchived_files += 1

                  if len(file_type):    
                     file_stats = stat(full_name)
                     cls.zip_log.info(f'Unpacked({file_type}): {full_name} {int(round(file_stats.st_size/1024,0))} KB')  
                     # cls.log.info(f'Unpacked({file_type}): {full_name}')
                     remove(full_name)
                  else:
                     cls.zip_log.info(f'Skipped {full_name}')
            except BadZipFile:
               #not a valid zip file log it then remove from staging folder
               print('')
               cls.log.error(f'Bad zip file: {full_name}')  
               remove(full_name)

            except (TarError, ValueError, Exception) as ex:
               print('')
               cls.log.error(f'Error while unpacking: {full_name}')  
               cls.log.error(str(ex))
               error = True

      #terminate on error 
      if error: 
         raise

      return archived_files, unarchived_files

   def run(cls,config:Config):
      cls._log.debug(f'Running {cls.__class__.__name__} for all applications')
      # cls._log.debug('Running unzip step')

      #scan delivery folder for application folders
      apps= config.application
      # for (dirpath,dirnames,filenames) in walk(work_folder):
      #    apps.extend(dirnames)
      

      found = True
      while found:
         found = False
         for app in tqdm(apps, desc="Unzipping files", leave=True):
            log_folder=abspath(f'{config.logs}/{config.project_name}/{app}/unpack')
            create_folder(log_folder)

            dateTimeObj=datetime.now()
            file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

            zip_log_file= abspath(f"{log_folder}/{file_suffix}.log")
            log_name = 'Unzip-files'
            cls.zip_log = Logger(log_name,level=cls._log_level,file_name=zip_log_file,console_output=False)
            cls.zip_log.info(f'{config.project}/{app}')
            archived_files, unarchived_files = cls.unzip(abspath(f'{config.work}/{config.project_name}/{app}'))

            msg = f'{config.project_name}/{app} found and unpacked {archived_files} archives found in {unarchived_files} files'
            cls.log.info(msg)
            cls.zip_log.info(msg)
            # embedded_archives = archived_files - 1
            # if embedded_archives > 0:   
            #    cls.log.info(f'{archived_files} files unzipped successfully. {embedded_archives} embedded archives found and unzipped successfully.\n')
            # else:
            #    cls.log.info(f'{archived_files} files unzipped successfully. 0 embedded archives found.\n')
            Logger.loggers.remove(log_name)

      cls.log.info('Archive file unpack complete')

   def get_title(cls) -> str:
      return 'DISCOVER ARCHIVES AND UNZIP'                               




