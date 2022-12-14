from logger import Logger
from config import Config
from unzip import Unzip
from prep import Prepare
from cloc import ClocPreCleanup
from logger import INFO
from argparse import ArgumentParser
from os.path import isfile,isdir

from xlwt import Workbook

from sourceValidation import SourceValidation 

__author__ = "Nevin Kaplan"
__email__ = "n.kaplan@castsoftware.com"
__copyright__ = "Copyright 2022, CAST Software"



if __name__ == '__main__':

    #printing some inital messages to the user
    log_level = INFO
    log = Logger("main")

    print('\nCAST automated cloc output, source dicovery and intial analysis')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    print('If you need assistance, please contact Bhanu Prakash (BBA) from the CAST IN PS team\n')

    parser = ArgumentParser(description='One Click')
    parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location')
    parser.add_argument('-p','--projectName', required=True, help='Name of the project')
    parser.add_argument('-r','--restart', required=False, help='Cleanup all work and start over')
    args = parser.parse_args()

    config=Config()
    config.project=args.projectName    
    config.base=args.baseFolder
    config.restart=args.restart    

    workbook = Workbook()
    process = [
        Prepare(log_level),
        Unzip(log_level),
       ClocPreCleanup(workbook,log_level)
    ]

    step = 1
    for p in process:
        log.info(f'Step {step}.')
        if issubclass(type(p), SourceValidation):
            status = p.run(config)
        step = step + 1
