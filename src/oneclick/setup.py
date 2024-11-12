from argparse import ArgumentParser

from os.path import abspath,exists,dirname
from os import chdir,getcwd,getenv
from cast_common.util import yes_no_input,folder_input,secret_input,url_input,string_input
from oneclick.config import Config
from oneclick.exceptions import NoConfigFound,InvalidConfiguration,InvalidConfigNoBase
from pkg_resources import get_distribution


from argparse import ArgumentParser
from pkg_resources import get_distribution
from oneclick.config import Config
from oneclick.exceptions import InvalidConfigNoBase

def main():
    version = get_distribution('com.castsoftware.uc.oneclick').version
    print(f'\nCAST OneClick Setup, v{version}')
    print('Copyright (c) 2024 CAST Software Inc.')
    print('If you need assistance, please contact oneclick@castsoftware.com')

    parser = ArgumentParser(prog='OneClick')
    parser.add_argument('-b', '--baseFolder', help='Base Folder Location', metavar='BASE_FOLDER')
    parser.add_argument('-w', '--workingFolder', help='Working Folder Location', metavar='WORKING_FOLDER')
    parser.add_argument('-d', '--debug', type=bool)

    try:
        config = Config(parser)
    except InvalidConfigNoBase as e:
        print(e)
        return

    configure_oneclick(config)

def configure_oneclick(config):
    chdir(config.base)

    print(f'OneClick installation location: {config.base}')
    config.workbase = input('OneClick Working Folder: ') or config.workbase

    config.java_home = configure_java(config)
    config.profiler = configure_profiler(config)

    if input('Configure MRI automatic scans? (y/n) ').lower() == 'y':
        configure_mri(config)

    if input('Configure Highlight automatic scans? (y/n) ').lower() == 'y':
        configure_highlight(config)

def configure_java(config):
    config.cloc_version='cloc-1.96.exe'

def configure_java(config):
    if len(config.java_home) == 0:
        config.java_home=getenv('JAVA_HOME')
    config.java_home = folder_input("Java installation folder location",config.java_home,'bin/java.exe')

def configure_profiler(config):
    profiler_folder = ''
    if len(config.profiler) > 0:
        profiler_folder = '\\'.join(config.profiler.split('\\')[:-1])
    config.profiler = folder_input("CAST-Profiler folder location",profiler_folder,'CAST-Profiler.exe',combine=True) 

def configure_mri(config):
    print ('Configuring for AIP Console')
    if yes_no_input('\tAre both "AIP Console Enterprise Edition" and the matching "AIP Console automation tools" installed?'):
        config.console_url = url_input('\t"AIP Console Enterprise Edition" URL',config.console_url)
        config.console_cli = folder_input('\t"AIP Console automation tools" location',dirname(config.console_cli),"aip-console-tools-cli.jar",True)
        config.console_key = secret_input('\t"AIP Console Enterprise Edition" API Key', config.console_key)
        config.enable_security_assessment = yes_no_input('\tEnable security analysis',config.enable_security_assessment)
        config.blueprint = yes_no_input('\tEnable Blueprint analysis',config.blueprint)

    if config.is_console_active:
        print ('AIP Console configuration complete')
    else:
        print ('Error updating AIP Console configuration!')
    print ('\n')

def configure_highlight(config):
    config.hl_cli = folder_input('\tHighlight command line interface installation location',config.hl_cli,'HighlightAutomation.jar',True)
    agent_folder = f'{config.perl_install_dir}'.replace('\\strawberry\\perl','')
    agent_folder = folder_input('\tHighlight agent installation location',agent_folder,'strawberry',False)
    config.perl_install_dir=abspath(f'{agent_folder}/strawberry/perl')
    config.analyzer_dir=abspath(f'{agent_folder}/perl')

    if yes_no_input('\tAre all of your applications using the same Highlight portal?'):
        if len(config.hl_url)==0:
            config.hl_url = "https://rpa.casthighlight.com/"
        config.hl_url = url_input('\t\tHighlight URL',config.hl_url)
        config.hl_url = f"{config.hl_url}"
        config.hl_user = string_input('\t\tHighlight user name',config.hl_user)
        config.hl_password = secret_input('\t\tHighlight password', config.hl_password)
        config.hl_instance = string_input('\t\tHighlight instance id',config.hl_instance)

    if config.is_hl_active:
        print ('Highlight configuration complete')
    else:
        print ('Error updating Highlight configuration!')
    print ('\n')

if __name__ == '__main__':
    main()

