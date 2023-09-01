from os import walk,remove
from os.path import abspath,exists

#from shutil import unpack_archive
from pyunpack import Archive
from gzip import open as gz
from tarfile import open as tar, TarError
from shutil import copyfileobj

from cast_common.util import create_folder

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
         for root, dirs, files in walk(src_fldr):
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
                     Archive(full_name).extractall(dest,auto_create_dir=True)

                  if found:     
                     cls._log.info(f'Unpacked: {full_name}')  
                     remove(full_name)

            except (TarError, ValueError, Exception) as ex:
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
         for app in apps:
            found = cls.unzip(abspath(f'{config.work}\\AIP\\{config.project_name}\\{app}'))
            found = cls.unzip(abspath(f'{config.work}\\HL\\{config.project_name}\\{app}'))
                     
            #          full_name = abspath(f'{root.strip()}\\{file}')
            #          dest = full_name.replace(f".{full_name.split('.')[-1]}",'')
            #          cls._log.info(f'Unzipping {full_name}')

            #          Archive(full_name).extractall(dest,auto_create_dir=True)
                     
            #          remove(full_name)

      cls._log.info('Unzip step complete')
                                




