from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.configTest import Config,Status
from os import walk
from os.path import abspath
from re import findall,IGNORECASE,sub

from cast_common.util import  format_table
from pandas import DataFrame,ExcelWriter,Series,json_normalize


#TODO: Add filename and location for each item (d1)
class SQLDiscovery(SourceValidation):
    @property
    def choose(self) -> bool:
        return True
    
    @property
    def name(self) -> str:
        return 'SQL Discovery'

    def __init__(cls):
        pass

    _pattern={
        'Create Tables'      :r'create\stable\s[^#]([^\n|^\s|^\(]+)[^\(]',
        'Create Functions'   :r'create\sfunction\s([^\n|^\s|^\(]+)[^\(]',
        'Create Procedures'  :r'create\sprocedure\s([^\n|^\s|^\(]+)[^\(]',
        'Create Views'       :r'create\sview\s([^\n|^\s|^\(]+)[^\(]',
        'Create Triggers'    :r'create\strigger\s([^\n|^\s|^\(]+)[^\(]',
        'Alter Tables'       :r'alter\stable\s([^\n|^\s|^\(]+)',
        'Alter Functions'    :r'alter\sfunction\s([^\n|^\s|^\(]+)',
        'Alter Procedures'   :r'alter\sprocedure\s([^\n|^\s|^\(]+)',
        'Alter Views'        :r'alter\sview\s([^\n|^\s|^\(]+)',
        'Alter Triggers'     :r'alter\strigger\s([^\n|^\s|^\(]+)',
    }

    def parse_sql(cls,file):

        rslt = {}
        rslt['file-name']=file
        with open(file, encoding="cp437") as f:
            content = f.read()
            for key in cls._pattern.keys():
                pattern = cls._pattern[key]
                rslt[key]=findall(pattern,content,IGNORECASE)
                rslt[key]=list(map(lambda x: sub(r'\W+','',x), rslt[key]))
                if len(rslt[key])==0:
                   rslt[key]=[] 
        cls._data.append(rslt)
        pass

    def run(cls):
        config = cls.config
        apps= config.applist

        print(cls.show_progress())

        for app in apps:
            app_name=app['name']
            cls.log.info(f'application {app_name}')

            status = app['status']
            if status['aip'] < Status.CLOC_POST_CLEAN_END:
                cls.log.warning(f'CLOC not completed for {app_name}')
                return False

            status['aip'] = status['highlight'] = Status.SQL_DISCOVERY_START
            if 'sql' not in app:
                app['sql']={'tables':0,'functions':0,'procedures':0,'views':0,'triggers':0}
            config._save()

            cls._data=[]
            sql_files = []
            non_sql_files = []
            app_folder = abspath(f'{config.stage_folder}/{config.project_name}/{app_name}')
            for root, dirs, files in walk(app_folder):
                for file in files:
                    if file.endswith(".bod") or \
                    file.endswith(".fnc") or \
                    file.endswith(".prc") or \
                    file.endswith(".trg") or \
                    file.endswith(".bdy") or \
                    file.endswith(".spc") :
                        fn = abspath(f'{root}/{file}')
                        cls.log.warning(f'Non-standard SQL file found: {fn}')
                        non_sql_files.append(fn)
                        # cls._log.warning(f'Potential SQL files with another alternate extension found in {app} review SQLReport and rename if appropriate')

                    if file.endswith(".sql") or file.endswith(".dtd"):
                        sql_files.append(abspath(f'{root}/{file}'))
                pass

            # cls._log.info(f'Found {len(sql_files)} SQL and {len(non_sql_files)} potential SQL files.')

            if len(sql_files):
                for file in sql_files:
                    cls.parse_sql(file)

                summary_df = DataFrame(columns=['Name','Total','Unique','Dups'])
                df = json_normalize(cls._data)
                detail = {}
                for key in cls._pattern.keys():
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

                app['sql']['tables'] = int(summary_df.loc[0]['Total'])
                app['sql']['functions'] = int(summary_df.loc[1]['Total'])
                app['sql']['procedures'] = int(summary_df.loc[2]['Total'])
                app['sql']['views'] = int(summary_df.loc[3]['Total'])
                app['sql']['triggers'] = int(summary_df.loc[4]['Total'])
                config._save()
                
                # total_artifacts = total_tables + total_functions + total_procedures + total_triggers + total_views
                # print('-------------------------------------')
                # print('Artifacts                     Count')
                # print('-------------------------------------')
                # print(f'Tables                          {total_tables}')
                # print(f'Functions                       {total_functions}')
                # print(f'Procedures                      {total_procedures}')
                # print(f'Views                           {total_views}')
                # print(f'Triggers                        {total_triggers}')
                # print('-------------------------------------')
                # print(f'Total Artifacts                 {total_artifacts}')
                # print('-------------------------------------')

                if not summary_df.empty:
                    summary_df=summary_df.sort_values(['Name'],ascending=False)
                    filename = abspath(f'{config.report_folder}/{config.project_name}/{app_name}/{app_name}-SQLReport.xlsx')
                    writer = ExcelWriter(filename, engine='xlsxwriter')
                    dups_format = writer.book.add_format({'bg_color': '#FFFF00', 'font_color': '#9C0006'})
                    xls=format_table(writer,summary_df,'Summary',total_line=True)
                    xls.conditional_format(f'D2:D{len(summary_df)}', {'type':'cell','criteria':'>','value':0,'format':dups_format})

                    for key in cls._pattern.keys():
                        if not detail[key] is None:
                            xls = format_table(writer,detail[key],key)
                            xls.conditional_format(f'A1:B{len(detail[key])}', {'type':'formula','criteria':'=COUNTIF($B:$B,$B1)>1','format':dups_format})

                    writer.close()
                    print(cls.show_progress())
                    # cls._log.info(f'SQL Discovery Report: {filename}')
                    # cls._log.info(f'detailed discovery report available at {filename}\n')
            else:
                #cls._log.warning(f'No SQL found\n')
                pass
            pass
        # cls._log.info('SQLDiscovery complete.')
        pass
        print(cls.show_progress())
        return True


