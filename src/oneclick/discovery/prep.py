from cast_common.logger import Logger
from cast_common.util import create_folder, yes_no_input,folder_input,secret_input,url_input,string_input
from os import mkdir,walk,listdir
from os.path import exists,abspath,isdir
from glob import glob
from shutil import copytree,rmtree
from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.configTest import Config,Status
from oneclick.exceptions import InvalidConfiguration


from tqdm import tqdm

class Prepare(SourceValidation):

    @property
    def choose(self) -> bool:
        return True
    
    @property
    def name(self) -> str:
        return __class__.__name__

    def __init__(self):
        pass


    def add_app(self,app_name:str):
        config = self.config
        
        print ("When running an MRI analysis include:")
        security = yes_no_input('\tSecurity analysis', default_value=True)
        blueprint = yes_no_input('\tBlueprint analysis', default_value=True)
        if yes_no_input(f'Add {app_name}?', default_value=True):
            config.log.info(f'Adding {app_name}')
            config.add_app(app_name, security, blueprint)
            create_folder(abspath(f'{config.deliver_folder}/{config.project_name}/{app_name}'))
        pass

    def run(self):
        config = self.config
        self.log.info(f'Starting project: {config.project_name}')

        print(self.show_progress())

        #scan delivery folder for application folders
        dir=[]
        project_folder = abspath(f'{config.deliver_folder}\\{config.project_name}')
        dirnames = listdir(project_folder) 
        if len(dirnames) == 0:
            config.log.warning(f'No applications found in {project_folder}')
            while True:
                if len(config.applist) > 0:
                    # for i in range(7):
                    #     print('\033[A',end='')
                    if not yes_no_input('Add another application?', default_value=False):
                        break
                self.add_app(string_input('What is the name of the application'))
                pass
            pass
        else:
            pass

        dirnames = listdir(project_folder) 
        self.log.info(f'Found {len(dirnames)} applications in {project_folder}')
        for folder in dirnames:
            app_folder = abspath(f'{project_folder}\\{folder}')

            found = False
            for app in config.applist:
                if app['name'] == folder:
                    found = True
                    break
            if not found:
                if yes_no_input (f'Found an extra folder, "{app_folder}", that does not exist in your project, add it now'):
                    self.add_app(folder)
            else:
                self.log.debug(f'{app_folder} found in the project configuration file')

            # self.log.info(f'Looking for source code in {app_folder}')
            files = []
            while len(files) == 0:
                files = glob(f'{app_folder}\\*')
                if len(files) == 0:
                    if not yes_no_input(f'{app_folder} has no source files, please add it now?',default_value=True):
                        self.log.info('Terminated by user')
                        exit(1)
            print(self.show_progress())
            pass
        
        pass
        
        self.log.info(config.application_report())

        for app in config.applist:
            app_folder = abspath(f'{project_folder}\\{app["name"]}')
            stage_folder = abspath(f'{config.stage_folder}\\{config.project_name}\\{app["name"]}')
            if Status(app['status']['aip']) < Status.STAGED:
                if glob(f'{stage_folder}\\*'):
                    self.log.info(f'Removing {stage_folder}')
                    rmtree(stage_folder)
                create_folder(stage_folder)
                self.log.info(f'Staging {app_folder} to {stage_folder}')
                status = copytree(app_folder,stage_folder,dirs_exist_ok=True)
                self.log.info(f'All files copied to {status}')
                app['status']['aip']=app['status']['highlight']=Status.STAGED
                config._save()
            else:
                self.log.info(f'{app["name"]} already staged')

            print(self.show_progress())
            pass

        self.log.info(f'Environment preparation complete for project {config.project_name}')

        return True

