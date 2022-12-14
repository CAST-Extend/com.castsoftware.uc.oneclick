from logger import Logger
from unzip import Unzip
from prep import Prepare
from cloc import ClocPreCleanup
from logger import INFO
from argparse import ArgumentParser


from os.path import isfile,isdir

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

    process = [
    #    Prepare(args,log_level),
    #    Unzip(args,log_level),
       ClocPreCleanup(args,log_level)
    ]

    step = 1
    for p in process:
        log.info(f'Step {step}.')
        if issubclass(type(p), SourceValidation):
            if p.run():
                pass
        p.run(["app1","app2"])
        step = step + 1
