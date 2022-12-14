from os import walk,remove
from shutil import unpack_archive

from sourceValidation import SourceValidation 


class Unzip(SourceValidation):

   def __init__(cls, args, log_level:int):
      super().__init__(args,cls.__class__.__name__,log_level)


   def run(cls):
      cls._log.info('Running unzip step')
      work_folder = f'{cls._args.baseFolder}\\work\\{cls._args.projectName}'        

      #scan delivery folder for application folders
      apps=[]
      for (dirpath,dirnames,filenames) in walk(work_folder):
         apps.extend(dirnames)

      found = True
      while found:
         found = False
         for app in apps:
            app_folder = f'{work_folder}\\{app}'
            for root, dirs, files in walk(app_folder):
               for file in files:
                  if file.endswith(".zip") or \
                     file.endswith(".tar") or \
                     file.endswith(".gztar") or \
                     file.endswith(".bztar"):
                     found = True

                     full_name = f'{root}\\{file}'
                     cls._log.info(f'Unzipping {full_name}')
                     unpack_archive(full_name,root)
                     remove(full_name)
      cls._log.info('Unzip step complete')
                                




