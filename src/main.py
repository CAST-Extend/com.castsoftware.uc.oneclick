from logger import Logger
from config import Config

from discovery.unzip import Unzip
from discovery.prep import Prepare
from discovery.cloc import ClocPreCleanup,ClocPostCleanup
from discovery.cleanup import cleanUpAIP,cleanUpHL
from discovery.sqlDiscovery import SQLDiscovery
from discovery.discoveryReport import DiscoveryReport

from analysis.analysis import Analysis
from analysis.highlight_analysis import HLAnalysis
from analysis.aip_analysis import AIPAnalysis
from analysis.trackAnalysis import TrackAnalysis

from action_plan import ActionPlan
from runArg import RunARGAIP,RunARG

from logger import INFO
from argparse import ArgumentParser

from util import create_folder
from os.path import abspath

#from os.path import isfile,isdir

#from discovery import Unzip,Prepare


from discovery.sourceValidation import SourceValidation 

__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2022, CAST Software"



if __name__ == '__main__':

    #printing some inital messages to the user
    log_level = INFO
    log = Logger("main")

    print('\nCAST One Click')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    print('If you need assistance, please contact Technical Due Diligence @team.ddassessment@castsoftware.com\n')

    parser = ArgumentParser(description='One Click')
    parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location')
    parser.add_argument('-c','--companyName', required=True, help='Name of the project')
    parser.add_argument('-p','--projectName', required=True, help='Name of the project')
    parser.add_argument('-r','--reset', required=False,help='Cleanup all work and start over')

    parser.add_argument('-s','--stop', required=False, help='Stop running at this step')

    parser.add_argument('--hlURL', required=False, help='Highlight URL')
    parser.add_argument('--hlUser', required=False, help='Highlight User')
    parser.add_argument('--hlPassword', required=False, help='Highlight Password')
    parser.add_argument('-i','--hlInstance', required=False, help='Highlight Instance Id')

    parser.add_argument('--aipURL', required=False, help='AIP API URL')
    parser.add_argument('--aipUser', required=False, help='AIP API  User')
    parser.add_argument('--aipPassword', required=False, help='AIP API  Password')

    parser.add_argument('--consoleURL', required=False, help='AIP Console URL')
    parser.add_argument('--consoleKey', required=False, help='AIP Console Key')

    parser.add_argument('--dbHost', required=False, help='Database Host')
    parser.add_argument('--dbPort', required=False, help='Database Port')
    parser.add_argument('--dbUser', required=False, help='Database User')
    parser.add_argument('--dbPassword', required=False, help='Database Password')
    parser.add_argument('--dbDatabase', required=False, help='Database Database')


    parser.add_argument('--start',choices=['Analysis','Report'],default='Discovery',help='Start from catagory')
    parser.add_argument('--end',choices=['Discovery','Analysis','Report'],default='Report',help='End after catagory')
    
    # TODO: add args for aip and console rest setup
    # TODO: add arg to reset analysis status for specific application

    args = parser.parse_args()

    config=Config(args.baseFolder,args.projectName)
    config.reset=args.reset    
    config.company_name=args.companyName

    config.hl_url=args.hlURL
    config.hl_user=args.hlUser
    config.hl_password=args.hlPassword
    config.hl_instance=args.hlInstance

    config.aip_url=args.aipURL
    config.aip_user=args.aipUser
    config.aip_password=args.aipPassword

    config.console_url=args.consoleURL
    config.console_key=args.consoleKey

    config.host=args.dbHost
    config.port=args.dbPort
    config.user=args.dbUser
    config.password=args.dbPassword
    config.database=args.dbDatabase

    create_folder(abspath(f'{config.base}/work'))
    create_folder(abspath(config.work))
    create_folder(abspath(config.logger))
    create_folder(abspath(config.output))
    create_folder(abspath(config.report))

    post_aip = [
        ActionPlan(config,log_level),
        RunARGAIP(config,log_level)
    ]

    post_highlight = [
        #TODO generate Highlight BOM report (phase 2)
    ]

    process = [

        # environment setup
        Prepare(config,log_level),
        Unzip(config,log_level),
        
        # source code preparation
        ClocPreCleanup(config,log_level),
        cleanUpAIP(config,log_level),
        cleanUpHL(config,log_level),
        ClocPostCleanup(config,log_level),


        # reporting
        SQLDiscovery(config,log_level),
        #TODO discovery report on project level, should be in app level
        DiscoveryReport(config,log_level),

        # application analysis process
        #TODO DLM module?
        AIPAnalysis(log_level),
        HLAnalysis(log_level),
        TrackAnalysis(post_aip,log_level),

        RunARG(config,log_level)

        #TODO continue processing after analysis is done (phase 2)
        #TODO generate obsolescence report (phase 2)
    ]

    step = 1
    for p in process:
        log.info(f'******************* Step {step} - {p.__class__.__name__} *******************************')
        if args.start == 'Discovery':
            if issubclass(type(p), SourceValidation):
                status = p.run(config)

        if args.end == 'Discovery':
            break

        if args.start in ['Discovery','Analysis']:
            if issubclass(type(p), Analysis):
                status = p.run(config)
                if status and issubclass(type(p), TrackAnalysis):
                    log.error('One or more analysis failed, review logs and restart')
                    break

        if args.end == 'Analysis':
            break

        if args.start in ['Discovery','Analysis','Report']:
            if issubclass(type(p), RunARG):
                status = p.run(config)


        # if issubclass(type(p), ActionPlan):
        #     for appl in config.application:
        #         log.info(f'Working on action items for {appl}')
        #         p.run(appl)

        step += 1

    log.info('Complete')
