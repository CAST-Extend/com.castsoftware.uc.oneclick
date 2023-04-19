from os import walk,remove
from os.path import abspath

from shutil import unpack_archive

from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config
from pyunpack import Archive

class Unzip(SourceValidation):

   def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)


   def run(cls,config:Config):
      cls._log.debug('Running unzip step')

      #scan delivery folder for application folders
      apps= config.application
      # for (dirpath,dirnames,filenames) in walk(work_folder):
      #    apps.extend(dirnames)

      found = True
      cls._log.info(f'Running {cls.__class__.__name__} for all applications')
      while found:
         found = False
         for app in apps:
            app_folder_aip = f'{config.work}\\AIP\\{config.project_name}\\{app}'
            for root, dirs, files in walk(app_folder_aip):
               for file in files:
                  # if file.endswith(".zip") or \
                  #    file.endswith(".tar") or \
                  #    file.endswith(".gztar") or \
                  #    file.endswith(".bztar"):
                  #    found = True
                     
                  #    full_name = f'{root}\\{file}'
                  #    cls._log.info(f'Unzipping {full_name}')
                  #    unpack_archive(full_name,root)
                  #    remove(full_name)

                  if file.endswith(".zip") or \
                     file.endswith(".tar") or \
                     file.endswith(".gztar") or \
                     file.endswith(".bztar") or \
                     file.endswith(".7z"):

                     root = abspath(root)
                     full_name = abspath(f'{root}\\{file}')
                     cls._log.info(f'Unzipping {full_name}')
                     found = True
                     Archive(full_name).extractall(root)
                     remove(full_name)

            app_folder_hl = f'{config.work}\\HL\\{config.project_name}\\{app}'
            for root, dirs, files in walk(app_folder_hl):
               for file in files:
                  if file.endswith(".zip") or \
                     file.endswith(".tar") or \
                     file.endswith(".gztar") or \
                     file.endswith(".bztar") or \
                     file.endswith(".7z"):

                     root = abspath(root)
                     full_name = abspath(f'{root}\\{file}')
                     cls._log.info(f'Unzipping {full_name}')
                     found = True
                     Archive(full_name).extractall(root)
                     remove(full_name)



      cls._log.info('Unzip step complete')
                                




