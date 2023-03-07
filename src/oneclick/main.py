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

from argparse import ArgumentParser,RawTextHelpFormatter
from oneclick.sendEmail import EmailNotification
from sys import exit
from os.path import abspath

from argparse_formatter import FlexiFormatter,ParagraphFormatter

from oneclick.discovery.sourceValidation import SourceValidation 
from oneclick.exceptions import NoConfigFound

import sys

__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2022, CAST Software"

def get_argparse_defaults(parser):
    defaults = {}
    for action in parser._actions:
        if not action.required and action.dest != "help":
            defaults[action.dest] = action.default
    return defaults


#TODO: d2-Ability to install onclick with all its components via PIP (d2)
#TODO: d1-send emails (d1-SHP)
if __name__ == '__main__':

    #printing some inital messages to the user
    log_level = INFO
    log = Logger("main")

    print('\nCAST One Click')
    print('Copyright (c) 2023 CAST Software Inc.\n')
    print('If you need assistance, please contact Technical Due Diligence @team.ddassessment@castsoftware.com\n')

    parser = ArgumentParser(prog='OneClick',  formatter_class=lambda prog: FlexiFormatter(prog, width=99999, max_help_position=60))
    subparsers = parser.add_subparsers(title='command',dest='command')

    """
        configure default json to be used with all projects going forward
    """
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location',metavar='BASE_FOLDER')
    config_parser.add_argument('-d','--debug',type=bool)
    config_parser.add_argument('-p','--projectName', help='Name of the project')

    #settings
    settings=config_parser.add_argument_group('General Settings')
    settings.add_argument('--java_home', help='Set if java is not part of the system path')
    settings.add_argument('--report_template', help='Set if java is not part of the system path')

    #dashboard access
    dashboard=config_parser.add_argument_group('CAST AIP Dashboard Access')
    dashboard.add_argument('--aipURL', help='AIP API URL')
    dashboard.add_argument('--aipUser', help='AIP API  User')
    dashboard.add_argument('--aipPassword', help='AIP API  Password')

    #highlight
    highlight=config_parser.add_argument_group('CAST Highlight Access')
    highlight.add_argument('--hlURL',default='https://rpa.casthighlight.com', help='Highlight URL',metavar='URL')
    highlight.add_argument('--hlUser',  help='Highlight User',metavar='USER')
    highlight.add_argument('--hlPassword',  help='Highlight Password',metavar='PASSWORD')
    highlight.add_argument('--hlInstance',  help='Highlight Instance Id',type=int,metavar='ID')
    highlight.add_argument('--hlCLI',
                            default='c:/Program Files/CAST/Highlight-Automation-Command/HighlightAutomation.jar', 
                            help='Highlight CLI Location',
                            metavar='LOCATION')
    highlight.add_argument('--HLPerlInstallDir',
                            default='c:/Program Files/CAST/HighlightAgent',
                            help='Highlight Perl Installation Location (HighlightAgent/strawberry/perl)',
                            metavar='LOCATION')
    highlight.add_argument('--HLAnalyzerDir', 
                           default='c:/Program Files/CAST/HighlightAgent/perl',
                           help='Highlight Perl Installation Location (HighlightAgent/perl)',
                           metavar='LOCATION')

    console=config_parser.add_argument_group('CAST AIP Console')
    console.add_argument('--consoleURL',  help='AIP Console URL',metavar='URL')
    console.add_argument('--consoleKey',  help='AIP Console Key',metavar='KEY')
    console.add_argument('--consoleCLI',  help='AIP Console CLI Location',metavar='LOCATION')

    database=config_parser.add_argument_group('CAST AIP Core Database')
    database.add_argument('--dbHost',  help='Database Host')
    database.add_argument('--dbPort',  help='Database Port')
    database.add_argument('--dbUser',  help='Database User',default="operator")
    database.add_argument('--dbPassword',  help='Database Password',default="CastAIP")
    database.add_argument('--dbDatabase',  help='Database Database',default="postgres")

    """
        OneClick "Run" parameters
    """
    run_parser = subparsers.add_parser('run')
    run_parser.add_argument('-b','--baseFolder', help='Base Folder Location')
    run_parser.add_argument('-n','--consoleNode', help='AIP Console Node Name',metavar='NAME')
    run_parser.add_argument('-c','--companyName',  default='Company Name', help='Name of the project')

    run_parser.add_argument('--start',choices=['Analysis','Report'],default='Discovery',help='Start from catagory')
    run_parser.add_argument('--end',choices=['Discovery','Analysis','Report'],default='Report',help='End after catagory')

    run_parser.add_argument('-d','--debug',  default=False,type=bool)

    default_args = get_argparse_defaults(config_parser)
    args = parser.parse_args()

    log.info(f'Running {args.command}')

    try:
        config=Config(parser,default_args)

        if args.command == 'config':
            file = ''
            if args.projectName is None:
                file='Default'
            else:
                file = args.projectName
            log.info(f'{file} configuration file successfuly updated')
            exit ()

    except NoConfigFound as ex:
        log.error(config_parser.format_help())
        log.error(ex)
        exit()

    # parser.add_argument('-c','--companyName',  default='Company Name', help='Name of the project')
    # parser.add_argument('--JavaHome',  help='Location of the JRE')
    # parser.add_argument('--from-email',  help='Email sending from')
    # parser.add_argument('--from-to',  help='Email sending from')
    # parser.add_argument('--from-email',  help='Email sending from')
    # parser.add_argument('--from-email',  help='Email sending from')

    # TODO: add args for aip and console rest setup (d2)
    # TODO: add arg to reset analysis status for specific application (d2)

    args = parser.parse_args()
    if args.debug:
        log_level=DEBUG

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
        if issubclass(type(p), Analysis) and args.end == 'Discovery':
            log.info('--end Discovery selected, process stopping here')
            break


        log.info(f'******************* Step {step} - {p.__class__.__name__} *******************************')
        if args.start == 'Discovery':
            if issubclass(type(p), SourceValidation):
                status = p.run(config)

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