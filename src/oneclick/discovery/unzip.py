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
from oneclick.configTest import Config,Status,App


class Unzip(SourceValidation):
   skip = ['__MACOSX','.DS_Store']

   @property
   def name(self) -> str:
      return __class__.__name__

   # def get_title(self) -> str:
   #    return 'DISCOVER ARCHIVES AND UNZIP'                               

   def __init__(self):
       pass

   def unzip(self,src_fldr:str,appl) -> tuple[bool,int,int]:
      unarchived_files = 0
      archived_files = 0
      error = False
      found = True

      loop = 0
      while found:
         loop +=1
         self.zip_log.info(f'Pass {loop}')
         
         found = False
         for root, dirs, files in walk(src_fldr):
            try:
               if '__MACOSX' in root or '.DS_Store' in files:
                  continue
               
               print (self.show_progress())

               for file in files:
                  full_name = abspath(f'{root.strip()}\\{file}')
                  dest = full_name.replace(f".{full_name.split('.')[-1]}",'')

                  file_type=''
                  if file.endswith(".gz"):
                     archived_files += 1
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
                        file_type = 'Tape Archive (tar)'
                        create_folder(dest)
                        f_in.extractall(dest)

                  elif file.endswith(".7z") or file.endswith(".zip") :
                     archived_files += 1
                     file_type = 'zip archive'
                     full_name = abspath(f'{root.strip()}\\{file}')
                     create_folder(dest)
                     with ZipFile(full_name) as zf:
                        for member in tqdm(zf.infolist(), desc=f'Extracting {full_name}',position=0,leave=True):
                           zf.extract(member, dest)

                  else:
                     unarchived_files += 1

                  print (self.show_progress())

                  if len(file_type):    
                     found=True
                     appl['unpacked']+=1
                     file_stats = stat(full_name)
                     self.zip_log.info(f'Unpacked({file_type}): {full_name} {int(round(file_stats.st_size/1024,0))} KB')  
                     # self.log.info(f'Unpacked({file_type}): {full_name}')
                     remove(full_name)
                  else:
                     self.zip_log.info(f'Skipped {full_name}')
            except BadZipFile:
               #not a valid zip file log it then remove from staging folder
               print('')
               self.log.error(f'Bad zip file: {full_name}')  
               remove(full_name)

            except (TarError, ValueError, Exception) as ex:
               print('')
               self.log.error(f'Error while unpacking: {full_name}')  
               self.log.error(str(ex))
               error = True

      #terminate on error 
      if error: 
         raise
      return archived_files, unarchived_files

   # process_cnt = 0
   # process_txt = '\\|/-\\|/-'
   # def show_progress(self,done=False):
   #    config = self.config

   #    out = f'\r{self.process_txt[self.process_cnt]} Running {self.name} for project: {config.project_name}                                                       \n'
   #    out = out + 'Appl Name                                         Status                     Unpacked\n'
   #    out = out + '------------------------------------------------- ------------------------ ----------\n'

   #    for app in config.applist:
   #       app_name = app['name']
   #       app_status = app['status']['aip']
   #       if 'unpacked' not in app:
   #          app['unpacked'] = 0
   #       out = out + f"{app_name:<50}{Status(app_status).name.replace('_', ' '):<25}{app['unpacked']:>10}\n"

   #    if not done:
   #       for l in range(len(config.applist)+4):
   #          out = out + '\033[F'
   #       out = out + '\r'
   #       self.process_cnt += 1
   #       if self.process_cnt == len(self.process_txt):
   #             self.process_cnt = 0
   #       out = out + '\r\033[?25l'
   #    else:
   #       out = out + '\033[?25h'
   #       pass

   #    pass
   #    return out

   def run(self):
      config = self.config
      log = self.log

      log.debug('Unpack files')
      work_folder=abspath(f'{config.stage_folder}/{config.project_name}')


      for app in config.applist:
         app_status = app['status']
         if app_status['aip'] < Status.UNPACK_START:
            app['unpacked']=0

      print (self.show_progress())

      for app in config.applist:
         app_name = app['name']
         app_status = app['status']
         if app_status['aip'] < Status.STAGED:
            config.log.error(f'{app_name} must be staged before unziping files')
            return False
         elif app_status['aip'] > Status.UNPACK_END:
            config.log.debug(f'{app_name} already unpacked')
            continue

         app_name = app['name']
         app_status['highlight'] = app_status['aip']  = Status.UNPACK_START
         config._save()

         #configure logging for each app
         log_folder=abspath(f'{config.log_folder}/{config.project_name}/{app_name}/unpack')
         create_folder(log_folder)

         dateTimeObj=datetime.now()
         file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

         zip_log_file= abspath(f"{log_folder}/{file_suffix}.log")
         log_name = 'Unzip-files'
         self.zip_log = Logger(log_name,level=config.log_level,file_name=zip_log_file,console_output=False)
         self.zip_log.info(f'{config.project}/{app}')

         archived_files, unarchived_files = self.unzip(abspath(f'{work_folder}/{app_name}'),app)
         print (self.show_progress())

         app['status']['highlight'] = app['status']['aip']  = Status.UNPACK_END
         config._save()

         msg = f'{config.project_name}/{app_name} found and unpacked {archived_files} archives found in {unarchived_files} files'
         # self.log.info(msg)
         self.zip_log.info(msg)
         # embedded_archives = archived_files - 1
         # if embedded_archives > 0:   
         #    self.log.info(f'{archived_files} files unzipped successfully. {embedded_archives} embedded archives found and unzipped successfully.\n')
         # else:
         #    self.log.info(f'{archived_files} files unzipped successfully. 0 embedded archives found.\n')
         Logger.loggers.remove(log_name)

      self.log.info(self.show_progress(True))
      self.log.debug('Archive file unpack complete')
      return True





