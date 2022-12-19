import os
from datetime import datetime
import shutil
from sourceValidation import SourceValidation 
from config import Config
  
  
  
class Cleanup(SourceValidation): 

    def __init__(cls, log_level:int):
      super().__init__(cls.__class__.__name__,log_level)
  
    
    def run(cls,dirLoc,config:Config):
            print('#3. Source Code cleanup is in progress')
            #filepathHL=dirname+'\\scripts\\cleanup-hl.bat'  
            #filepathHAIP=dirname+'\\scripts\\cleanup-aip.bat' 
            dateTimeObj=datetime.now()
            file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
            #print('bba - '+dirLoc)
            #print('bba - '+str(os.listdir(dirLoc).count))
            exclusionFileList= config.base+'\\scripts\\deleteFileList.txt'
            exclusionFolderList= config.base+'\\scripts\\deleteFolderList.txt'
            clean_up_log_file= config.base +f"\\deletedFiles_{file_suffix}.txt"
            clean_up_log_folder= config.base+f"\\deletedFolders_{file_suffix}.txt"
        
            #items = os.listdir(dirLoc)
            #deleting unwanted files and writing those logs to deleteFileList.txt file.
            with open (clean_up_log_file, 'a+') as file1: 
                s=''
                with open(exclusionFileList) as f:
                    files_list = f.read().splitlines()
                    #print(files_list)
                count=1
                for subdir, dirs, files in os.walk(dirLoc):
                    for file in files:
                        fileN=os.path.join(subdir, file) 
                        for fileName in files_list:
                            #print(fileName)
                            if fileN.endswith(fileName):
                                os.remove(fileN)
                                #print('Removed file -> '+fileN)     
                                s=str(count)+") Removed file -> "+fileN
                                count+=1
                                file1.write(s)
                                file1.write('\n') 

            #deleting unwanted folders and writing those logs to deleteFolderList.txt file.
            with open (clean_up_log_folder, 'a+') as file2: 
                s=''
                with open(exclusionFolderList) as f:
                    folder_list = f.read().splitlines()
                    #print(folder_list)
                count=1
                for subdir, dirs, files in os.walk(dirLoc):
                        for dir in dirs:
                            if dir in folder_list:
                                folder=os.path.join(subdir, dir)
                                shutil.rmtree(folder)
                                #print('Removed folder -> '+folder)       
                                s=str(count)+") Removed folder -> "+folder
                                count+=1
                                file2.write(s)
                                file2.write('\n') 
            cls._log.info('Cleanup completed successfully')
            cls._log.info('Completed step number 3 out of 5.\n')
              