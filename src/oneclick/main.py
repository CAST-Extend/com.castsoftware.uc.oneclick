__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2024, CAST Software"

from pkg_resources import get_distribution
from oneclick.configTest import Config,Status
from oneclick.base import Base
from oneclick.exceptions import InvalidConfiguration,InvalidConfigNoBase

from oneclick.discovery.unzip import Unzip
from oneclick.discovery.prep import Prepare
from oneclick.discovery.cloc import ClocPreCleanup,ClocPostCleanup
from oneclick.discovery.profiler import ProfilerPreCleanup
from oneclick.discovery.cleanup import Cleanup,rmtree
from oneclick.discovery.sqlDiscovery import SQLDiscovery
from oneclick.discovery.discoveryReport import DiscoveryReport



from oneclick.analysis.analysis import Analysis
from oneclick.analysis.runAnalysis import RunHighlight
from oneclick.analysis.highlight_analysis import HLAnalysis
from oneclick.analysis.aip_analysis import AIPAnalysis
from oneclick.analysis.trackAnalysis import TrackAnalysis

from inquirer import List,prompt
from os.path import abspath,exists

if __name__ == '__main__':
    version = get_distribution('com.castsoftware.uc.oneclick').version
    print(f'\nCAST OneClick Setup, v{version}')
    print(f'com.castsoftware.uc.python.common v{get_distribution("com.castsoftware.uc.python.common").version}')
    print('Copyright (c) 2024 CAST Software Inc.')
    print('If you need assistance, please contact oneclick@castsoftware.com')
    
    config = Config()
    Base(config)    
    try:
        config.log.info(f'****************** Starting CAST OneClick for project {config.project_name} ******************')

        if config.reset:
            config.log.info(f'Resetting all applications')
            for app in config.applist:
                app['status']['highlight'] = app['status']['aip'] = Status.NOT_STARTED
            config._save()

            for folder in [abspath(f'{config.stage_folder}/{config.project_name}'),
                        abspath(f'{config.highlight_folder}/{config.project_name}'),
                        abspath(f'{config.report_folder}/{config.project_name}')]:
                config.log.info(f'Removing {folder}')
                if exists(folder):
                    rmtree(folder)
            for app in config.applist:
                app['deleted'] = {'folders':'','files':''}
                app['sql'] = {'tables':'','functions':'','procedures':'','views':'','triggers':''}
                app['loc'] = ''
                app['unpacked'] = ''

        # config.log.info(config.application_report())
        process = [

            # environment setup
            Prepare(),
            Unzip(),
            
            # source code preparation
            ClocPreCleanup(),
            Cleanup(),
            ClocPostCleanup(),
            # ProfilerPreCleanup(),

            # reporting
            SQLDiscovery(),
            DiscoveryReport(),

            #todo: add discovery report email notification
            # EmailNotification(),

            # application analysis process
            #TODO DLM module?
            # AIPAnalysis(),
            # HLAnalysis(),
            # TrackAnalysis()

            RunHighlight()

            #RunARG(config,log_level)

        ]

        choices = []
        for obj in process:
            if  obj.choose:
                choices.append(f'{obj.name}') 

        start=0
        end=len(choices)-1
        if not (config.quiet):
            questions = [
                List(
                    'start with step',
                    message="Starting process step?", 
                    choices=choices,
                    default=choices[0]
                    ),
                List(
                    'End with step',
                    message="Ending process step", 
                    choices=choices,
                    default=choices[len(choices)-1]
                    )
            ]
            answers = prompt(questions)
            config.start = answers['start with step']
            config.end = answers['End with step']

        start = end = 0        
        if config.start == None or len(config.start) == 0:
            start=0
        else:
            start = 0
            for i in range(len(process)):
                if process[i].name.startswith(config.start):
                    start=i
                    break

        if config.end == None or len(config.end) == 0:
            end=len(process)-1
        else:
            end = len(process)
            for i in range(len(process)):
                if process[i].name.startswith(config.end):
                    end=i
                    break

        if start > end:
            raise InvalidConfiguration(f'End step {process[end].name} is before start step {process[start].name}')
        elif not process[start].choose:
            raise InvalidConfiguration(f'Start step {process[start].name} is not a selectable step')

        config.start = process[start].name
        config.end = process[end].name

        config.log.info(f'Starting project {config.project_name} at "{config.start}" and ending at "{config.end}"')
        active=False
        step = 0
        for p in process:
            step += 1
            #look for starting class
            if p.name == process[start].name:
                active=True

            if not active: 
                config.log.info(f'Skipping {p.name}')
                continue

            # if issubclass(type(p), Analysis) and end == 'Discovery':
            #     config.log.info('--end Discovery selected, process stopping here')
            #     break

            p.log.info(f'=> STEP {step} : {p.name}')
            
            if p.can_run:
                # config.log.info(f'Running {p.name}')
                status = p.run()
                if not status:
                    # config.log.error(f'Error running {p.name}')
                    break
                config._save()
            else:
                config.log.info(f'Skipping {p.name}, configuration is incomplete')
            pass


    except InvalidConfiguration as ic:
        config.log.error(ic)
    except Exception as ex:
        from traceback import format_exc

        print ('\n\n\n\n\n\n\n\n')

        config.log.error(format_exc())
    config.log.info(f'Thanks for using CAST OneClick. For more information, contact oneclick@castsoftware.com')

