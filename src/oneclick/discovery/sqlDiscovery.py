from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config
from os import walk
from os.path import abspath
from re import findall

from cast_common.util import  format_table
from pandas import DataFrame,ExcelWriter,Series

#TODO: Add filename and location for each item (d1)
class SQLDiscovery(SourceValidation):

    def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)


    def run(cls,config:Config):
        
        apps= config.application

        for app in apps:
            cls._log.info(f'Running {cls.__class__.__name__} for {app}')

            cls.table_list=[]
            cls.procedure_list=[]
            cls.function_list=[]
            cls.view_list=[]
            cls.trigger_list=[]
            cls.file_list=[]
            cls.alt_ext_lst=[]

            alt_ext_wrn = False

            app_folder = abspath(f'{config.work}\\AIP\\{config.project_name}\\{app}')
            for root, dirs, files in walk(app_folder):
                for file in files:
                    if file.endswith(".bod") or \
                       file.endswith(".fnc") or \
                       file.endswith(".prc") or \
                       file.endswith(".trg") or \
                       file.endswith(".bdy") or \
                       file.endswith(".spc") :
                        fn = abspath(f'{root}/{file}')
                        cls.alt_ext_lst.append(fn)  
                        if not alt_ext_wrn:                      
                            cls._log.warning(f'Potential SQL files with another alternate extension found in {app} review SQLReport and rename if appropriate')
                            alt_ext_wrn=True

                    if file.endswith(".sql") or file.endswith(".dtd") :
                        found = True
                        cls.read_sql_file(root,file)

            table_dict={}
            for i in cls.table_list:
                if i not in table_dict.keys():
                    table_dict[i]=cls.table_list.count(i)
            #print(table_dict)

            procedure_dict={}
            for i in cls.procedure_list:
                if i not in procedure_dict.keys():
                    procedure_dict[i]=cls.procedure_list.count(i)
            #print(procedure_dict)
            
            function_dict={}
            for i in cls.function_list:
                if i not in function_dict.keys():
                    function_dict[i]=cls.function_list.count(i)
            #print(function_dict)

            view_dict={}
            for i in cls.view_list:
                if i not in view_dict.keys():
                    view_dict[i]=cls.view_list.count(i)
            #print(view_dict)

            trigger_dict={}
            for i in cls.trigger_list:
                if i not in trigger_dict.keys():
                    trigger_dict[i]=cls.trigger_list.count(i)
            #print(trigger_dict)

            file_dict={}
            for i in cls.file_list:
                if i not in file_dict.keys():
                    file_dict[i]=cls.file_list.count(i)

            filename = abspath(f'{config.report}/{config.project_name}/{app}/{app}-SQLReport.xlsx')
            writer = ExcelWriter(filename, engine='xlsxwriter')
            tabs = []

            summary_list = []
            summary_list.append(cls.summary_data('Tables',table_dict,cls.table_list))    
            summary_list.append(cls.summary_data('Procedures',procedure_dict,cls.procedure_list))    
            summary_list.append(cls.summary_data('Functions',function_dict,cls.function_list))    
            summary_list.append(cls.summary_data('Triggers',trigger_dict,cls.trigger_list))    
            summary_list.append(cls.summary_data('Views',view_dict,cls.view_list))    
            summary_list.append(cls.summary_data('SQL files',file_dict,cls.file_list)) 
            tabs.append(format_table(writer,DataFrame(summary_list),'Summary'))  

            if len(table_dict):
                tabs.append(format_table(writer,cls.detail_data(table_dict),'Tables')) 
            if len(procedure_dict):
                tabs.append(format_table(writer,cls.detail_data(procedure_dict),'Procedures'))            
            if len(function_dict):
                tabs.append(format_table(writer,cls.detail_data(function_dict),'Functions'))            
            if len(trigger_dict):
                tabs.append(format_table(writer,cls.detail_data(trigger_dict),'Triggers'))            
            if len(view_dict):
                tabs.append(format_table(writer,cls.detail_data(view_dict),'Views'))            
            if len(file_dict):
                tabs.append(format_table(writer,cls.detail_data(file_dict),'Files'))            

            if len(cls.alt_ext_lst):
                tabs.append(format_table(writer,DataFrame(cls.alt_ext_lst,columns=['Filename']),'AltSQLExten'))            


            writer.close()

            pass

        cls._log.info('Unzip step complete')
        pass

    def summary_data(cls,name,unique,total)->Series:
        return {'Catagory':name,'Unique':len(unique),"Total":len(total)}

    def detail_data(cls,data:dict)->DataFrame:
        df = DataFrame(data.items(),columns=['Name','Count'])
        df['Duplicated'] = df['Count']>1
        return df

    def read_sql_file(cls,file_path,file):
        #print(file)
        fn = abspath(f'{file_path}/{file}')
        if fn in cls.file_list:
            return

        #todo: identify additional patterns to recongize addition sql code (d1)
        cls.file_list.append(fn)
        with open(fn, encoding="cp437") as f:
            content = f.read()

            table_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[T|t][A|a][B|b][L|l][E|e]\s{1,}([^\n|^\s|^\(]+)'
            tbl_list=findall(table_pattern,content)
            cls.table_list.extend(tbl_list)

            proc_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[P|p][R|r][O|o][C|c][E|e][D|d][U|u][R|r][E|e]\s{1,}([^\n|^\s|^\(]+)'
            proc_list=findall(proc_pattern,content)
            cls.procedure_list.extend(proc_list)

            #regular expressions for PL/SQL
            proc_pattern_2='[P|p][R|r][O|o][C|c][E|e][D|d][U|u][R|r][E|e]\s{1,}([^\n|^\s|^\(]+)'
            proc_list_2=findall(proc_pattern_2,content)
            cls.procedure_list.extend(proc_list_2)

            func_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[F|f][U|u][N|n][C|c][T|t][I|i][O|o][N|n]\s{1,}([^\n|^\s|^\(]+)'
            func_list=findall(func_pattern,content)
            cls.function_list.extend(func_list)

            #regular expressions for PL/SQL
            func_pattern_2='[F|f][U|u][N|n][C|c][T|t][I|i][O|o][N|n]\s{1,}([^\n|^\s|^\(]+)'
            func_list_2=findall(func_pattern_2,content)
            cls.function_list.extend(func_list_2)

            view_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[V|v][I|i][E|e][W|w]\s{1,}([^\n|^\s|^\(]+)'
            vi_list=findall(view_pattern,content)
            cls.view_list.extend(vi_list)

            trig_pattern='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[T|t][R|r][I|i][G|g][G|g][E|e][R|r]\s{1,}([^\n|^\s|^\(]+)'
            trig_list=findall(trig_pattern,content)
            cls.trigger_list.extend(trig_list)

            #regular expressions for PL/SQL
            trig_pattern_2='[C|c][R|r][E|e][A|a][T|t][E|e]\s{1,}[T|t][R|r][I|i][G|g][G|g][E|e][R|r]\s{1,}([^\n|^\s|^\(]+)'
            trig_list_2=findall(trig_pattern_2,content)
            cls.trigger_list.extend(trig_list_2)
            
            f.close()
