import re
import shutil
#from logger import Logger
import subprocess
import os
import xlwt
from xlwt import Workbook
from datetime import datetime


class sourceDiscovery():

    # def runUnzipAll(self,dirLoc):
    #     #subprocess.call(['\scripts\unzipall.bat'])
    #     print('\n#1. Source Code unzipping is in progress')
    #     print('----Folder to unzip - '+dirLoc)
    #     path=os.getcwd()
    #     dirname = os.path.dirname(__file__)
    #     #print(dirname)
    #     hlDir=dirLoc
    #     filepath=dirname+'\\scripts\\unzipall.bat'
    #     #p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
    #     p = subprocess.Popen([filepath,dirLoc], shell=True, stdout = subprocess.PIPE)
    #     stdout, stderr = p.communicate()
    #     #print(p.returncode)
    #     return p.returncode,dirname

    # def runCodeCleanup(self,dirLoc,dirname,output_path):
    #     print('#3. Source Code cleanup is in progress')
    #     #filepathHL=dirname+'\\scripts\\cleanup-hl.bat'  
    #     #filepathHAIP=dirname+'\\scripts\\cleanup-aip.bat' 
    #     dateTimeObj=datetime.now()
    #     file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")
    #     #print('bba - '+dirLoc)
    #     #print('bba - '+str(os.listdir(dirLoc).count))
    #     exclusionFileList= dirname+'\\scripts\\deleteFileList.txt'
    #     exclusionFolderList= dirname+'\\scripts\\deleteFolderList.txt'
    #     clean_up_log_file= output_path +f"\\deletedFiles_{file_suffix}.txt"
    #     clean_up_log_folder= output_path +f"\\deletedFolders_{file_suffix}.txt"
    
    #     #items = os.listdir(dirLoc)
    #     #deleting unwanted files and writing those logs to deleteFileList.txt file.
    #     with open (clean_up_log_file, 'a+') as file1: 
    #         s=''
    #         with open(exclusionFileList) as f:
    #             files_list = f.read().splitlines()
    #             #print(files_list)
    #         count=1
    #         for subdir, dirs, files in os.walk(dirLoc):
    #             for file in files:
    #                 fileN=os.path.join(subdir, file) 
    #                 for fileName in files_list:
    #                     #print(fileName)
    #                     if fileN.endswith(fileName):
    #                         os.remove(fileN)
    #                         #print('Removed file -> '+fileN)     
    #                         s=str(count)+") Removed file -> "+fileN
    #                         count+=1
    #                         file1.write(s)
    #                         file1.write('\n') 

    #     #deleting unwanted folders and writing those logs to deleteFolderList.txt file.
    #     with open (clean_up_log_folder, 'a+') as file2: 
    #         s=''
    #         with open(exclusionFolderList) as f:
    #             folder_list = f.read().splitlines()
    #             #print(folder_list)
    #         count=1
    #         for subdir, dirs, files in os.walk(dirLoc):
    #                 for dir in dirs:
    #                     if dir in folder_list:
    #                         folder=os.path.join(subdir, dir)
    #                         shutil.rmtree(folder)
    #                         #print('Removed folder -> '+folder)       
    #                         s=str(count)+") Removed folder -> "+folder
    #                         count+=1
    #                         file2.write(s)
    #                         file2.write('\n') 
    #     print('Cleanup completed successfully')
    #     print('Completed step number 3 out of 5.\n')         

    # def runCloc(self,dirLoc,file_Suffix,flag,workbook,output_path):
    #     dateTimeObj=datetime.now()
    #     file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

    #     source_code_path=dirLoc
    #     #print(source_code_path)
    #     path=os.getcwd()
    #     #print(path)
    #     dirname = os.path.dirname(__file__)
    #     #print(dirname)
    #     cloc_path=dirname+'\\scripts\\cloc-1.64.exe'
    #     cloc_output_file=output_path+f"\\Cloc_Output_{file_Suffix}_{file_suffix}.txt"
    #     list_of_tech_file=dirname+'\\scripts\\ListOfTechnologies.csv'
    #     cloc_output_xls=output_path+f"\\Cloc_Output_{file_suffix}.xls"
           
    #     #creating clock command    
    #     Cloc_cmd=cloc_path+' '+ source_code_path+' >> '+cloc_output_file
        

    #     #executing clock command if cloc_ouput.txt file is not exists already 
    #     if os.path.exists(cloc_output_file):
    #         os.remove(cloc_output_file)
    #         os.system(Cloc_cmd)
    #     else:
    #         os.system(Cloc_cmd)

    #     #reading cloc_output.txt file
    #     summary_list=[]   
    #     with open(cloc_output_file, 'r') as f:
    #         content = f.read()
    #         f.seek(0)
    #         summary_list= [line.rstrip('\n').lstrip() for line in f]
    #         #print(summary_list)

    #     su_list=[]
    #     for i in summary_list:
    #         if i.__contains__('http'):
    #             break
    #         else:
    #             su_list.append(i)
    #     #print(su_list)

    #     #extracting required data from content of cloc_output.txt using python regex
    #     pattern='(\S{1,}|\w{1,}[:])\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
    #     statistics_list=re.findall(pattern,content)
    #     statistics_list.insert(0,('LANGUAGE','FILES','BLANK','COMMENT','CODE','APPLICABLE'))

    #     for i in range(len(statistics_list)):
    #         statistics_list[i]=list(statistics_list[i])   

    #     #extracting supported technologies from ListOfTechnologies.csv file into sup_tech list
    #     sup_tech = []
    #     with open(list_of_tech_file, 'r') as f:   
    #         sup_tech = f.readlines()
    #         sup_tech = [line.rstrip(',YES\n').lower() for line in sup_tech if line.__contains__(',YES') ]

    #     #if technology present in sup_tech list then mark it as YES otherwise Mark is as NO
    #     for i in range(1,len(statistics_list)-1):
    #         if statistics_list[i][0].lower() in sup_tech:
    #             statistics_list[i].append('YES')
    #         else:
    #             statistics_list[i].append('NO')

        

    #     if flag==0:
    #         su_sheet = workbook.add_sheet("Cloc Summary")
    #         su_list.insert(0,'Cloc Summary Before CleanUP')
    #         #write value into excel sheet one by one
    #         style = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;'
    #                           'font: colour black, bold True;')
    #         for i in range(len(su_list)):
    #             if i==0:
    #                 su_sheet.write(i, 0, su_list[i],style) 
    #             else:
    #                 su_sheet.write(i, 0, su_list[i])
            
    #         sheet = workbook.add_sheet("Stats Before Code CleanUP")
    #         #write value into excel sheet one by one
    #         for i in range(len(statistics_list)):
    #             for j in range(len(statistics_list[i])):
    #                 if i==0:
    #                     sheet.write(i, j, statistics_list[i][j],style)
    #                 else:
    #                     sheet.write(i, j, statistics_list[i][j])

    #     else:
    #         su_sheet = workbook.get_sheet("Cloc Summary")
    #         su_list.insert(0,'Cloc Summary After CleanUP')
    #         #write value into excel sheet one by one
    #         style = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;'
    #                           'font: colour black, bold True;')
    #         for i in range(len(su_list)):
    #             if i==0:
    #                 su_sheet.write(i, 1, su_list[i],style) 
    #             else:
    #                 su_sheet.write(i, 1, su_list[i])

    #         sheet = workbook.add_sheet("Stats After Code CleanUP")
    #         #write value into excel sheet one by one
    #         for i in range(len(statistics_list)):
    #             for j in range(len(statistics_list[i])):
    #                 if i==0:
    #                     sheet.write(i, j, statistics_list[i][j],style)
    #                 else:
    #                     sheet.write(i, j, statistics_list[i][j])

    #         #check whether cloc xls is already present or not. If already present delete and then save excel sheet as Cloc_Output.xls
    #         if os.path.exists(cloc_output_xls):
    #             os.remove(cloc_output_xls)
    #             workbook.save(cloc_output_xls)
    #         else:
    #             workbook.save(cloc_output_xls)

    #     #deletes the cloc txt output file
    #     os.remove(cloc_output_file)

       
    def generateXLS(self,dirLoc,output_path):
        #get the current date and time.
        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

        table_list=[]
        procedure_list=[]
        function_list=[]
        view_list=[]
        trigger_list=[]
        file_list=[]

        # path=os.getcwd()
        # #print(path)
        # dirname = os.path.dirname(__file__)
        #print(dirname)
        #SQL_TXT_File=output_path+f"\\SQL_Output_{file_suffix}.txt"
        SQL_XLS_File=output_path+f"\\SQL_Output_{file_suffix}.xls"

        # Read SQL File and extract neccessary info using regex.
        def read_sql_file(file_path,file):
            #print(file)
            file_list.append(file)
            
            with open(file_path, encoding="cp437") as f:
                content = f.read()

                table_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[T|t][A|a][B|b][L|l][E|e]\s{1,}([^\n|^\s|^\(]+)'
                tbl_list=re.findall(table_pattern,content)
                table_list.extend(tbl_list)

                proc_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[P|p][R|r][O|o][C|c][E|e][D|d][U|u][R|r][E|e]\s{1,}([^\n|^\s|^\(]+)'
                proc_list=re.findall(proc_pattern,content)
                procedure_list.extend(proc_list)

                func_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[F|f][U|u][N|n][C|c][T|t][I|i][O|o][N|n]\s{1,}([^\n|^\s|^\(]+)'
                func_list=re.findall(func_pattern,content)
                function_list.extend(func_list)

                view_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[V|v][I|i][E|e][W|w]\s{1,}([^\n|^\s|^\(]+)'
                vi_list=re.findall(view_pattern,content)
                view_list.extend(vi_list)

                trig_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[T|t][R|r][I|i][G|g][G|g][E|e][R|r]\s{1,}([^\n|^\s|^\(]+)'
                trig_list=re.findall(trig_pattern,content)
                trigger_list.extend(trig_list)

        #get the list of files from the directory
        def list_of_files(dirName):
            files_list = os.listdir(dirName)
            all_files = list()
            for entry in files_list:
                # Create full path
                full_path = os.path.join(dirName, entry)
                if os.path.isdir(full_path):
                    all_files = all_files + list_of_files(full_path)
                else:           
                    all_files.append((full_path,entry))
            return all_files



        # Folder Path
        path = dirLoc
        #path = r"C:\Users\SHP\Desktop\Python\Temp\Temp"

        # Change the directory
        os.chdir(path)

        files=list_of_files(path)

        for file_path,file in files:
            # Check whether file is in SQL format or not
            if file.endswith(".sql"):
                read_sql_file(file_path, file)

        table_dict={}
        for i in table_list:
            if i not in table_dict.keys():
                table_dict[i]=table_list.count(i)
        #print(table_dict)

        procedure_dict={}
        for i in procedure_list:
            if i not in procedure_dict.keys():
                procedure_dict[i]=procedure_list.count(i)
        #print(procedure_dict)

        function_dict={}
        for i in function_list:
            if i not in function_dict.keys():
                function_dict[i]=function_list.count(i)
        #print(function_dict)

        view_dict={}
        for i in view_list:
            if i not in view_dict.keys():
                view_dict[i]=view_list.count(i)
        #print(view_dict)

        trigger_dict={}
        for i in trigger_list:
            if i not in trigger_dict.keys():
                trigger_dict[i]=trigger_list.count(i)
        #print(trigger_dict)

        file_dict={}
        for i in file_list:
            if i not in file_dict.keys():
                file_dict[i]=file_list.count(i)
        #print(file_dict)

        # with open (SQL_TXT_File, 'a+') as file:        
        #     s="a. Number of SQL files -> "+str(len(file_dict))
        #     file.write(s)
        #     file.write('\n') 
        #     s="b. Number of Tables -> "+str(len(table_dict))
        #     file.write(s)
        #     file.write('\n')
        #     s="c. Number of Procedures -> "+str(len(procedure_dict))
        #     file.write(s)
        #     file.write('\n')
        #     s="d. Number of Functions -> "+str(len(function_dict))
        #     file.write(s)
        #     file.write('\n')
        #     s="e. Number of Triggers -> "+str(len(trigger_dict))
        #     file.write(s)
        #     file.write('\n')
        #     s="f. Number of Views -> "+str(len(view_dict))
        #     file.write(s)
        #     file.write('\n') 

        #creating new Excel Workbook.
        wb = Workbook()

        # add_sheet is used to create new sheet.
        sheet = wb.add_sheet('Summary')
        sheet.write(0,0,'Number of Tables')
        sheet.write(1,0,'Number of Procedures')
        sheet.write(2,0,'Number of Functions')
        sheet.write(3,0,'Number of Triggers')
        sheet.write(4,0,'Number of Views')
        sheet.write(5,0,'Number of SQL files')

        sheet.write(0,1,str(len(table_dict)))
        sheet.write(1,1,str(len(procedure_dict)))
        sheet.write(2,1,str(len(function_dict)))
        sheet.write(3,1,str(len(trigger_dict)))
        sheet.write(4,1,str(len(view_dict)))
        sheet.write(5,1,str(len(file_dict)))

        style = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;' 'font: colour black, bold True;')

        sheet1 = wb.add_sheet('Table Name')
        sheet1.write(0,0,'Table_Names', style)
        sheet1.write(0,1,'Cout_Of_Tables', style)
        sheet1.write(0,2,'Is_Duplicated', style)
        i=1
        for key,value in table_dict.items():
            sheet1.write(i,0,key)
            sheet1.write(i,1,value)
            if value>1:
                sheet1.write(i,2,'Yes')
            else:
                sheet1.write(i,2,'No')
            i+=1

        sheet2 = wb.add_sheet('Procedure Name')
        sheet2.write(0,0,'Procedure_Names', style)
        sheet2.write(0,1,'Count_Of_Procedures', style)
        sheet2.write(0,2,'Is_Duplicated', style)
        j=1
        for key,value in procedure_dict.items(): 
            sheet2.write(j,0,key)
            sheet2.write(j,1,value)
            if value>1:
                sheet2.write(j,2,'Yes')
            else:
                sheet2.write(j,2,'No')
            j+=1

        sheet3 = wb.add_sheet('Function Name')
        sheet3.write(0,0,'Function_Names', style)
        sheet3.write(0,1,'Count_Of_Functions', style)
        sheet3.write(0,2,'Is_Duplicated', style)
        k=1
        for key,value in function_dict.items(): 
            sheet3.write(k,0,key)
            sheet3.write(k,1,value)
            if value>1:
                sheet3.write(k,2,'Yes')
            else:
                sheet3.write(k,2,'No')
            k+=1

        sheet4 = wb.add_sheet('View Name')
        sheet4.write(0,0,'View_Names', style)
        sheet4.write(0,1,'Count_Of_Views', style)
        sheet4.write(0,2,'Is_Duplicated', style)
        l=1
        for key,value in view_dict.items(): 
            sheet4.write(l,0,key)
            sheet4.write(l,1,value)
            if value>1:
                sheet4.write(l,2,'Yes')
            else:
                sheet4.write(l,2,'No')
            l+=1

        sheet5 = wb.add_sheet('Trigger Name')
        sheet5.write(0,0,'Trigger_Names', style)
        sheet5.write(0,1,'Count_Of_Triggers', style)
        sheet5.write(0,2,'Is_Duplicated', style)
        m=1
        for key, value in trigger_dict.items(): 
            sheet5.write(m,0,key)
            sheet5.write(m,1,value)
            if value>1:
                sheet5.write(m,2,'Yes')
            else:
                sheet5.write(m,2,'No')
            m+=1

        #print(file_list)
        sheet6 = wb.add_sheet('File Details')
        sheet6.write(0,0,'File_Names', style)
        sheet6.write(0,1,'Count_Of_Files', style)
        sheet6.write(0,2,'Is_Duplicated', style)
        n=1
        for key,value in file_dict.items(): 
            sheet6.write(n,0,key)
            sheet6.write(n,1,value)
            if value>1:
                sheet6.write(n,2,'Yes')
            else:
                sheet6.write(n,2,'No')
            n+=1
            
        #If SQL XLS is already present delete and then create new SQL XLS.
        if os.path.exists(SQL_XLS_File):
            os.remove(SQL_XLS_File)
            wb.save(SQL_XLS_File)
        else:
            wb.save(SQL_XLS_File)
        

#printing some inital messages to the user
print('\nCAST automated cloc output, source dicovery and intial analysis')
print('Copyright (c) 2022 CAST Software Inc.\n')
print('If you need assistance, please contact Bhanu Prakash (BBA) from the CAST IN PS team\n')


#taking source code path as input from the user.
dirLoc=input(r'Enter the path containing a zip file of your source code (for example -> C:\sourceCode): ')

#creating object from sourceDiscovery class
obj=sourceDiscovery()

#1. Run unZip batch 
r_code,dirname=obj.runUnzipAll(dirLoc)

#extract output_path from properties.txt file
properties_file=dirname+'\\scripts\\Properties.txt'
with open(properties_file,'r') as f:
    path_list = f.read().split('=')
    output_path=path_list[1].strip()

#check whether path is valid or not, if not valid show the error message and exit from the program.
isExist = os.path.exists(output_path)
if not isExist:
    print("Please udpate the output folder in \script\properties.txt, the output folder does not seem to be valid!")
    s=input('Press any key to exit.')
    exit()

if r_code==0:
    print('Unzip Completed successfully')
    print('Completed step number 1 out of 5.\n')
    
    #2. Run Cloc utility before cleanup
    print('#2. Cloc utility (Before Cleanup) is in progress')
    fileSuffix='beforeCleanup'
    flag=0
    #creating new excel shhet with sheet name Stats
    workbook = xlwt.Workbook()
    obj.runCloc(dirLoc,fileSuffix,flag,workbook,output_path)
    print('Cloc utility (Before Cleanup) completed - Report Generated Successfully')
    print('Completed step number 2 out of 5.\n')

    #3. Run AIP Cleanup
    obj.runCodeCleanup(dirLoc,dirname,output_path)

    #4. Run Cloc utility after cleanup
    print('#4. Cloc utility (After Cleanup) is in progress')
    fileSuffix='afterCleanup'
    flag=1
    obj.runCloc(dirLoc,fileSuffix,flag,workbook,output_path)
    print('Cloc (After Cleanup) completed - Report Generated Successfully')
    print('Completed step number 4 out of 5.\n')

else:
    print('Unzip unsuccsessful'+str(r_code))
    exit


#5 Genrate SQL XLS
print('#5. Generating SQL report is in progress')
obj.generateXLS(dirLoc,output_path)
print('SQL report is generated successfully')
print('Completed step number 5 out of 5.\n')

print('All the Cleanup, Cloc and SQL output files are available here -> '+output_path)
s=input('Press any key to exit.')