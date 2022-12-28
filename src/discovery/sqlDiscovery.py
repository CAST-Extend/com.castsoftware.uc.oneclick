from discovery.sourceValidation import SourceValidation 
from config import Config
from datetime import datetime
from xlwt import Workbook
from os import mkdir,getcwd,remove
from os.path import dirname,exists
import re
import os
from xlwt import Workbook
import xlwt
from util import create_folder


class SQLDiscovery(SourceValidation):

    def __init__(cls, log_level:int):
        super().__init__(cls.__class__.__name__,log_level)
        
    @property
    def base(cls):
        return f'{cls.config.base}\\sql-discovery' 
    @property
    def project(cls):
        return f'{cls.base}\\{cls.config.project_name}'

    #def runCodeCleanup(self,dirLoc,dirname,output_path):
    def run(cls,config:Config):
         #get the current date and time.
        cls.config = config
        dateTimeObj=datetime.now()
        file_suffix=dateTimeObj.strftime("%d-%b-%Y(%H.%M.%S.%f)")

        table_list=[]
        procedure_list=[]
        function_list=[]
        view_list=[]
        trigger_list=[]
        file_list=[]

        SQL_XLS_File=f'{config.work}\\SQL_Output_{file_suffix}.xls'
        cls._workbook_name = f'{config.work}\\sql_{config.project_name}.xls'
                
        # Read SQL Files and extract neccessary info using regex.
        apps= config.application
        found = True
        while found:
            found = False
            for app in apps:
                app_folder = f'{config.work}\\{app}\\AIP'
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
                        f.close()

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
                path = app_folder
                #path = r"C:\Users\SHP\Desktop\Python\Temp\Temp"

                # Change the directory
                os.chdir(app_folder)

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