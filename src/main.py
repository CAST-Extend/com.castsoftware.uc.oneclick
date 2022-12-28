from logger import Logger
from config import Config

from discovery.unzip import Unzip
from discovery.prep import Prepare
from discovery.cloc import ClocPreCleanup,ClocPostCleanup
from discovery.cleanup import cleanUpAIP,cleanUpHL
from discovery.sqlDiscovery import SQLDiscovery
#from discovery.discoveryReport import DiscoveryReport

from analysis.analysis import Analysis
from analysis.highlight_analysis import HLAnalysis
from analysis.aip_analysis import AIPAnalysis
from analysis.trackAnalysis import TrackAnalysis

from action_plan import ActionPlan
from runArg import RunARGAIP,RunARG

from logger import INFO
from argparse import ArgumentParser
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

    print('\nCAST automated cloc output, source dicovery and intial analysis')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    print('If you need assistance, please contact Nevin Kaplan (NKA) from the CAST IN PS team\n')

    parser = ArgumentParser(description='One Click')
    parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location')
    parser.add_argument('-c','--companyName', required=True, help='Name of the project')
    parser.add_argument('-p','--projectName', required=True, help='Name of the project')
    parser.add_argument('-r','--reset', required=False,help='Cleanup all work and start over')
    parser.add_argument('-s','--start', required=False, help='Start from specific step')


    parser.add_argument('--hlURL', required=False, help='Highlight URL')
    parser.add_argument('--hlUser', required=False, help='Highlight User')
    parser.add_argument('--hlPassword', required=False, help='Highlight Password')
    parser.add_argument('-i','--hlInstance', required=True, help='Highlight Instance Id')
    
    # TODO: add args for aip and console rest setup
    # TODO: add arg to reset analysis status for specific application

    args = parser.parse_args()

    config=Config(args.baseFolder,args.projectName)
    config.reset=args.reset    
    config.company_name=args.companyName

    if args.hlURL is not None: 
        config.hl_url=args.hlURL
    if args.hlUser is not None: 
        config.hl_user=args.hlUser
    if args.hlPassword is not None: 
        config.hl_password=args.hlPassword
    if args.hlInstance is not None: 
        config.hl_instance=args.hlInstance

    post_aip = [
        ActionPlan(config,log_level),
        RunARGAIP(config,log_level)
    ]

    post_highlight = [
        #TODO generate Highlight BOM report (phase 2)
    ]

    process = [
        # environment setup
        Prepare(log_level),
        Unzip(log_level),
        
        # source code preparation
        ClocPreCleanup(config,log_level),
        cleanUpAIP(log_level),
        cleanUpHL(log_level),
        ClocPostCleanup(config,log_level),
        
        # reporting
        SQLDiscovery(log_level),
        #TODO discovery report on project level, should be in app level
        # DiscoveryReport(log_level),

        # application analysis process
        #TODO enable concurent process for analysis
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
        if issubclass(type(p), SourceValidation):
            status = p.run(config)

        if issubclass(type(p), Analysis):
            status = p.run(config)

        if issubclass(type(p), RunARG):
            status = p.run(config)


        # if issubclass(type(p), ActionPlan):
        #     for appl in config.application:
        #         log.info(f'Working on action items for {appl}')
        #         p.run(appl)

        step += 1
