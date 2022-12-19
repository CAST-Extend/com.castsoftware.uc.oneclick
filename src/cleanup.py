from datetime import datetime
import os
import shutil
from sourceValidation import SourceValidation 
from config import Config
from os import mkdir,getcwd,remove

class cleanUp(SourceValidation):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        

    #def runCodeCleanup(self,dirLoc,dirname,output_path):
    def run(cls,config:Config):
        print('Source Code cleanup is in progress')
        
        dir = getcwd()
        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
        
        exclusionFileList= f'{dir}\\scripts\\deleteFileList.txt'
        exclusionFolderList= f'{dir}\\scripts\\deleteFolderList.txt'
        clean_up_log_file= output_path +f"\\deletedFiles_{file_suffix}.txt"
        clean_up_log_folder= output_path +f"\\deletedFolders_{file_suffix}.txt"
        work_folder = f'{config.base}\\work\\{config.project}'  

        apps= config.application
        found = True
        while found:
            found = False
            for app in apps:
                app_folder = f'{work_folder}\\{app}'
                with open (clean_up_log_file, 'a+') as file1: 
                    s=''
                    with open(exclusionFileList) as f:
                        files_list = f.read().splitlines()
                        
                    count=1
                    for subdir, dirs, files in os.walk(app_folder):
                        for file in files:
                            fileN=os.path.join(subdir, file) 
                            for fileName in files_list:
                                
                                if fileN.endswith(fileName):
                                    os.remove(fileN)
                                
                                    s=str(count)+") Removed file -> "+fileN
                                    count+=1
                                    file1.write(s)
                                    file1.write('\n') 

                #deleting unwanted folders and writing those logs to deleteFolderList.txt file.
                with open (clean_up_log_folder, 'a+') as file2: 
                    s=''
                    with open(exclusionFolderList) as f:
                        folder_list = f.read().splitlines()
                        
                    count=1
                    for subdir, dirs, files in os.walk(app_folder):
                            for dir in dirs:
                                if dir in folder_list:
                                    folder=os.path.join(subdir, dir)
                                    shutil.rmtree(folder)
                        
                                    s=str(count)+") Removed folder -> "+folder
                                    count+=1
                                    file2.write(s)
                                    file2.write('\n') 
        print('Cleanup completed successfully')