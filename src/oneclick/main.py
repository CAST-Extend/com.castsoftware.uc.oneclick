from cast_common.logger import Logger,INFO,DEBUG
from cast_common.util import create_folder
from oneclick.config import Config

from oneclick.discovery.unzip import Unzip
from oneclick.discovery.prep import Prepare
from oneclick.discovery.cloc import ClocPreCleanup,ClocPostCleanup
from oneclick.discovery.cleanup import cleanUpAIP,cleanUpHL
from oneclick.discovery.sqlDiscovery import SQLDiscovery
from oneclick.discovery.discoveryReport import DiscoveryReport

from oneclick.analysis.analysis import Analysis
from oneclick.analysis.highlight_analysis import HLAnalysis
from oneclick.analysis.aip_analysis import AIPAnalysis
from oneclick.analysis.trackAnalysis import TrackAnalysis

from cast_action_plan.action_plan import ActionPlan
from oneclick.runArg import RunARGAIP,RunARG

from argparse import ArgumentParser
from oneclick.sendEmail import EmailNotification
from sys import exit
from os.path import abspath

from oneclick.discovery.sourceValidation import SourceValidation 

__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2022, CAST Software"

#TODO: d2-Ability to install onclick with all its components via PIP (d2)
#TODO: d1-send emails (d1-SHP)
if __name__ == '__main__':

    #printing some inital messages to the user
    log_level = INFO
    log = Logger("main")

    print('\nCAST One Click')
    print('Copyright (c) 2023 CAST Software Inc.\n')
    print('If you need assistance, please contact Technical Due Diligence @team.ddassessment@castsoftware.com\n')

    parser = ArgumentParser(description='One Click')
    parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location')
    parser.add_argument('-p','--projectName', required=True, help='Name of the project')

    parser.add_argument('-c','--companyName', required=False, default='Company Name', help='Name of the project')

    parser.add_argument('-d','--debug', required=False, default=False,type=bool)

    parser.add_argument('--hlURL', required=False,default='https://rpa.casthighlight.com/WS2/', help='Highlight URL')
    parser.add_argument('--hlUser', required=False, help='Highlight User')
    parser.add_argument('--hlPassword', required=False, help='Highlight Password')
    parser.add_argument('-i','--hlInstance', required=False, help='Highlight Instance Id')
    parser.add_argument('--hlCLI', required=False, help='Highlight CLI Location')
    parser.add_argument('--HLPerlInstallDir', required=False, help='Highlight Perl Installation Location (HighlightAgent\\strawberry\\perl)')
    parser.add_argument('--HLAnalyzerDir', required=False, help='Highlight Perl Installation Location (HighlightAgent\\perl)')

    parser.add_argument('--aipURL', required=False, help='AIP API URL')
    parser.add_argument('--aipUser', required=False, help='AIP API  User')
    parser.add_argument('--aipPassword', required=False, help='AIP API  Password')

    parser.add_argument('--consoleURL', required=False, help='AIP Console URL')
    parser.add_argument('--consoleKey', required=False, help='AIP Console Key')
    parser.add_argument('--consoleNode', required=False,default='local', help='AIP Console Key')
    parser.add_argument('--consoleCLI', required=False, help='AIP Console Key')

    parser.add_argument('--dbHost', required=False, help='Database Host')
    parser.add_argument('--dbPort', required=False, help='Database Port',default="2284")
    parser.add_argument('--dbUser', required=False, help='Database User',default="operator")
    parser.add_argument('--dbPassword', required=False, help='Database Password')
    parser.add_argument('--dbDatabase', required=False, help='Database Database',default="postgres")

    parser.add_argument('--JavaHome', required=False, help='Location of the JRE')


    # parser.add_argument('--from-email', required=False, help='Email sending from')
    # parser.add_argument('--from-to', required=False, help='Email sending from')
    # parser.add_argument('--from-email', required=False, help='Email sending from')
    # parser.add_argument('--from-email', required=False, help='Email sending from')

    parser.add_argument('--start',choices=['Analysis','Report'],default='Discovery',help='Start from catagory')
    parser.add_argument('--end',choices=['Discovery','Analysis','Report'],default='Report',help='End after catagory')

    # TODO: add args for aip and console rest setup (d2)
    # TODO: add arg to reset analysis status for specific application (d2)

    args = parser.parse_args()
    if args.debug:
        log_level=DEBUG

    config=Config(args.baseFolder,args.projectName)
    config.company_name=args.companyName

    config.hl_url=args.hlURL
    config.hl_user=args.hlUser
    config.hl_password=args.hlPassword
    config.hl_instance=args.hlInstance
    config.hl_cli=args.hlCLI
    config.perlInstallDir=args.HLPerlInstallDir
    config.analyzerDir=args.HLAnalyzerDir

    config.aip_url=args.aipURL
    config.aip_user=args.aipUser
    config.aip_password=args.aipPassword

    config.console_url=args.consoleURL
    config.console_key=args.consoleKey
    config.console_cli=args.consoleCLI
    config.node=args.consoleNode

    config.host=args.dbHost
    config.port=args.dbPort
    config.user=args.dbUser
    config.password=args.dbPassword
    config.database=args.dbDatabase

    config.java_home=args.JavaHome
    if not config.is_hl_config_valid:
        exit(1)

    create_folder(abspath(f'{config.base}/STAGED'))
    create_folder(abspath(config.work))
    create_folder(abspath(config.logs))
    create_folder(abspath(f'{config.logs}/{config.project_name}'))
    create_folder(abspath(config.report))
    create_folder(abspath(f'{config.report}/{config.project_name}'))

    post_aip = [
        ActionPlan(config,log_level),
        RunARGAIP(config,log_level)
    ]

    post_highlight = [
        #TODO generate Highlight BOM report (d1)
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
        DiscoveryReport(config,log_level),

        #todo: add discovery report email notification
        # EmailNotification(config,log_level),

        # application analysis process
        #TODO DLM module?
        AIPAnalysis(log_level),
        HLAnalysis(log_level),
        TrackAnalysis(post_aip,log_level),

        RunARG(config,log_level)

        #TODO continue processing after analysis is done (d2)
        #TODO generate obsolescence report (d2)
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
                elif status > 0:
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