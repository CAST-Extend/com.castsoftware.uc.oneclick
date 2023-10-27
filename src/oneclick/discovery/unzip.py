from os import walk,remove
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

   def unzip(cls,src_fldr) -> bool:
      error = False
      found = True
      while found:
         found = False
         for root, dirs, files in tqdm(walk(src_fldr), leave=False, position=1):
            try:
               if '__MACOSX' in root or '.DS_Store' in files:
                  continue
               for file in files:
                  full_name = abspath(f'{root.strip()}\\{file}')
                  dest = full_name.replace(f".{full_name.split('.')[-1]}",'')

                  found=False
                  if file.endswith(".gz"):
                     found = True
                     with gz(full_name, 'rb') as f_in:
                        if not exists(dest):
                           with open(dest, 'wb') as f_out:
                              copyfileobj(f_in, f_out)               

                  elif file.endswith(".tar") or \
                       file.endswith(".gztar") or \
                       file.endswith(".bztar") or \
                       file.endswith(".tgz"):
                     with tar(full_name) as f_in:
                        found = True
                        create_folder(dest)
                        f_in.extractall(dest)

                  elif file.endswith(".7z") or file.endswith(".zip") :
                     found = True
                     full_name = abspath(f'{root.strip()}\\{file}')
                     create_folder(dest)
                     with ZipFile(full_name) as zf:
                        for member in tqdm(zf.infolist(), desc='Extracting ',position=0,leave=False):
                           zf.extract(member, dest)
                     #Archive(full_name).extractall(dest,auto_create_dir=True)

                  if found:     
                     cls.zip_log.info(f'Unpacked: {full_name}')  
                     remove(full_name)
            except BadZipFile:
               #not a valid zip file log it then remove from staging folder
               print('')
               cls._log.error(f'Bad zip file: {full_name}')  
               remove(full_name)

            except (TarError, ValueError, Exception) as ex:
               print('')
               cls._log.error(f'Error while unpacking: {full_name}')  
               cls._log.error(str(ex))
               error = True

      #terminate on error 
      if error: 
         raise

      return found

   def run(cls,config:Config):
      cls._log.info(f'Running {cls.__class__.__name__} for all applications')
      cls._log.debug('Running unzip step')

      #scan delivery folder for application folders
      apps= config.application
      # for (dirpath,dirnames,filenames) in walk(work_folder):
      #    apps.extend(dirnames)
      

      found = True
      while found:
         found = False
         for app in tqdm(apps, desc="Unzipping files", leave=True):
            log_folder=abspath(f'{config.oneclick_work}/LOGS/{config.project_name}/{app}')
            create_folder(log_folder)

            dateTimeObj=datetime.now()
            file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

            zip_log_file= abspath(f"{log_folder}/unzip_{file_suffix}.log")
            log_name = 'Unzip-files'
            cls.zip_log = Logger(log_name,level=cls._log_level,file_name=zip_log_file,console_output=True)

            found = cls.unzip(abspath(f'{config.work}\\AIP\\{config.project_name}\\{app}'))
            found = cls.unzip(abspath(f'{config.work}\\HL\\{config.project_name}\\{app}'))

            Logger.loggers.remove(log_name)

            #          full_name = abspath(f'{root.strip()}\\{file}')
            #          dest = full_name.replace(f".{full_name.split('.')[-1]}",'')
            #          cls._log.info(f'Unzipping {full_name}')

            #          Archive(full_name).extractall(dest,auto_create_dir=True)
                     
            #          remove(full_name)

      cls._log.info('Unzip step complete')
                                




