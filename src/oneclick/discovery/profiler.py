from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.config import Config
from cast_common.logger import Logger,INFO
from cast_common.util import run_process,track_process,check_process,format_table,create_folder
from os import listdir,remove,rename
from os.path import exists,abspath,getsize
from pandas import json_normalize,ExcelWriter
from json import load
from tqdm import tqdm



class ProfilerPreCleanup(SourceValidation):

    def __init__(cls, config: Config, log_level:int=INFO, name = None):
        if name is None: 
            name = cls.__class__.__name__

        super().__init__(config,cls.__class__.__name__,log_level)

        cls.config = config
        cls._df = {}
        pass

    @property
    def phase(cls):
        return 'Before'

    def _run_profiler(cls,app_name:str, work_folder:str,profiler_output:str):

        profiler_path=cls.config.profiler
        profiler_output=abspath(f'{cls.config.report}\{cls.config.project_name}\{app_name}')
        work_folder=abspath(f'{cls.config.work}/AIP/{cls.config.project_name}\{app_name}')

        create_folder(profiler_output)

        args = [profiler_path,
                work_folder,
                '--generate-report', profiler_output,
                '--name',app_name,
                '--output',profiler_output,
                '--offline','--details','--no-upload','--no-browser','--complete-insight'
            ]
        cls._log.info(' '.join(args))

        #cleanup any old files
        files = [f for f in listdir(profiler_output) if f.startswith(app_name) and f.endswith('result.json')]
        for f in files:
            remove (f'{profiler_output}/{f}')

        # run profiler
        proc = run_process(args,wait=False)
        track_process(proc)

        #rename the profile output file to a standard name
        files = [f for f in listdir(profiler_output) if f.startswith(app_name) and f.endswith('result.json')]
        new_name = abspath(f'{profiler_output}/{app_name}-{cls.phase}.json')
        if len(files) > 0:
            old_name = abspath(f'{profiler_output}/{files[0]}')
            if exists(new_name):
                remove(new_name)
            rename(old_name,new_name)

        #process results
        if exists(new_name):
            with open(new_name) as f:
                prflr = load(f)

            #process the data
            alerts = json_normalize(prflr['alerts'])

            composition = json_normalize(prflr['composition'],max_level=1)
            omposition = json_normalize(prflr['composition'],max_level=1)
            if 'subExtensions' in composition.columns:
                composition = composition.explode(column=['subExtensions']).fillna('')

            dependencies = json_normalize(prflr['dependencies'])
            if 'iconNames' in dependencies.columns:
                dependencies = dependencies.explode(column=['iconNames'])
            if 'versions' in dependencies.columns:
                dependencies = dependencies.explode(column=['versions'])

            frameworks = json_normalize(prflr['frameworks'])
            ext_list = json_normalize(prflr['extensions_list'],max_level=1).transpose().reset_index()
            ext_list = ext_list.rename(columns={'index':'Name',0:'Count'})
            files = json_normalize(prflr['files'],max_level=1)	

            # add results to excel sheet
            file_name = abspath(f'{profiler_output}/{app_name}-{cls.phase.lower()}-prfl-rslts.xlsx')
            writer = ExcelWriter(file_name, engine='xlsxwriter')
            if not alerts.empty: format_table(writer,alerts,'alerts',total_line=True)
            if not composition.empty: format_table(writer,composition,'composition',total_line=True)
            if not dependencies.empty: format_table(writer,dependencies,'dependencies',total_line=True)
            if not ext_list.empty: format_table(writer,ext_list,'ext_list',total_line=True)
            if not files.empty: format_table(writer,files,'files',total_line=True)
            if not frameworks.empty: format_table(writer,frameworks,'frameworks',total_line=True)
            writer.close()
        else: 
            cls._log.warning('No profiler results found')
        pass

    def run(cls,config:Config):
        for appl in config.application:
            work_folder = abspath(f'{config.work}/AIP/{config.project_name}/{appl}')
            profiler_output=abspath(f'{config.report}/{config.project_name}/{appl}')
            
            create_folder(profiler_output)
            cls._run_profiler(app_name=appl,work_folder=work_folder,profiler_output=profiler_output)
            
