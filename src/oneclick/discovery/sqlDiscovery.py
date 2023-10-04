from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config
from os import walk
from os.path import abspath
from re import findall,IGNORECASE

from cast_common.util import  format_table
from pandas import DataFrame,ExcelWriter,Series,json_normalize
from tqdm import tqdm

#TODO: Add filename and location for each item (d1)
class SQLDiscovery(SourceValidation):

    def __init__(cls, config:Config, log_level:int):
        super().__init__(config,cls.__class__.__name__,log_level)

    _pattern={
#        'Create Table'   :r'create\s{1,}table\s{1,}([^\n|^\s|^\(]+)[^\(]',
#        'Create Table'   :r'create\s{1,}table\s[^#]{1,}([^\n|^\s|^\(]+)[^\(]',
        'Create Table'   :r'create\s{1,}table\s([^\n|^\s|^\(]+)[^\(]',
        'Alter Table'   :r'alter\s{1,}table\s{1,}([^\n|^\s|^\(]+)',
        'Create function':r'create\s{1,}function\s{1,}([^\n|^\s|^\(]+)[^\(]',
        'Alter function'   :r'alter\s{1,}function\s{1,}([^\n|^\s|^\(]+)',
        'Create procedure':r'create\s{1,}procedure\s{1,}([^\n|^\s|^\(]+)[^\(]',
        'Alter procedure'   :r'alter\s{1,}procedure\s{1,}([^\n|^\s|^\(]+)',
        'Create view':r'create\s{1,}view\s{1,}([^\n|^\s|^\(]+)[^\(]',
        'Alter view'   :r'alter\s{1,}view\s{1,}([^\n|^\s|^\(]+)',
        'Create trigger':r'create\s{1,}trigger\s{1,}([^\n|^\s|^\(]+)[^\(]',
        'Alter trigger'   :r'alter\s{1,}trigger\s{1,}([^\n|^\s|^\(]+)',
    }

    def read_sql_file(cls,file):

        rslt = {}
        rslt['file-name']=file
        with open(file, encoding="cp437") as f:
            content = f.read()
            for key in cls._pattern.keys():
                pattern = cls._pattern[key]
                rslt[key]=findall(pattern,content,IGNORECASE)
                if len(rslt[key])==0:
                   rslt[key]=[] 
        cls._data.append(rslt)
        pass

    def run(cls,config:Config):
        
        apps= config.application

        for app in apps:
            cls._log.info(f'Running {cls.__class__.__name__} for {app}')

            cls._data=[]
            sql_files = []
            non_sql_files = []
            app_folder = abspath(f'{config.work}\\AIP\\{config.project_name}\\{app}')
            cls._log.info(f'Searching {app_folder}')
            with tqdm(total=0) as pbar:
                for root, dirs, files in walk(app_folder):
                    for file in files:
                        if file.endswith(".bod") or \
                        file.endswith(".fnc") or \
                        file.endswith(".prc") or \
                        file.endswith(".trg") or \
                        file.endswith(".bdy") or \
                        file.endswith(".spc") :
                            fn = abspath(f'{root}/{file}')
                            cls._log.warning(f'Non-standard SQL file found: {fn}')
                            non_sql_files.append(fn)
                            # cls._log.warning(f'Potential SQL files with another alternate extension found in {app} review SQLReport and rename if appropriate')

                        if file.endswith(".sql") or file.endswith(".dtd"):
                            pbar.update(1)
                            sql_files.append(abspath(f'{root}/{file}'))
                    pass

            cls._log.info(f'Found {len(sql_files)} SQL and {len(non_sql_files)} potential SQL files.')

            if len(sql_files):
                for file in tqdm(sql_files,desc='SQLDiscovery'):
                    cls.read_sql_file(file)

                summary_df = DataFrame(columns=['Name','Total','Unique','Dups'])
                df = json_normalize(cls._data)
                detail = {}
                for key in tqdm(cls._pattern.keys(),desc='Compiling report'):
                    if key in df.keys():
                        detail_df=df.explode(key).dropna()
                        if not detail_df.empty:
                            detail_df=detail_df[['file-name',key]]
                            detail[key]=detail_df.sort_values(by=[key])
                            dups = len(detail_df.drop_duplicates(subset=[key]))
                            total=len(detail_df)
                            summary_df.loc[len(summary_df.index)] = [key,total,dups,total-dups]
                        else:
                            summary_df.loc[len(summary_df.index)] = [key,0,0,0]
                            detail[key]=None

                if not summary_df.empty:
                    filename = abspath(f'{config.report}/{config.project_name}/{app}/{app}-SQLReport.xlsx')
                    writer = ExcelWriter(filename, engine='xlsxwriter')
                    format_table(writer,summary_df,'Summary')
                    for key in tqdm(cls._pattern.keys(),desc=f'Writing {filename}'):
                        if not detail[key] is None:
                            format_table(writer,detail[key],key)
                    writer.close()
                    cls._log.info(f'SQL Discovery Report: {filename}')
            else:
                cls._log.warning(f'No SQL found')
        cls._log.info('SQLDiscovery complete.')
        pass


