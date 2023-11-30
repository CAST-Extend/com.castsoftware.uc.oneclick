from argparse import ArgumentParser

from os.path import abspath,exists,dirname
from os import chdir,getcwd,getenv
from oneclick.config  import Config,yes_no_input,folder_input,url_input,string_input
from oneclick.exceptions import NoConfigFound,InvalidConfiguration,InvalidConfigNoBase


if __name__ == '__main__':

    print('\nCAST OneClick Setup')
    print('Copyright (c) 2023 CAST Software Inc.\n')
    print('If you need assistance, please contact us at oneclick@castsoftware.com\n')


    parser = ArgumentParser(prog='OneClick')
    subparsers = parser.add_subparsers(title='command',dest='command')
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location',metavar='BASE_FOLDER')
    config_parser.add_argument('-d','--debug',type=bool)
    config_parser.add_argument('-p','--projectName', help='Name of the project')

    # base = folder_input('Where is OneClick installed ')
    try:
        config = Config(parser)
    except InvalidConfigNoBase as e:
        print (e)
        exit(1)

    chdir(config.base)
    print (f'OneClick installation location: {getcwd()}')

    config.cloc_version='cloc-1.96.exe'
    if len(config.java_home) == 0:
        config.java_home=getenv('JAVA_HOME')
    config.java_home = folder_input("Java installation folder location",config.java_home,'bin/java.exe')

    profiler_folder = ''
    if len(config.profiler) > 0:
        profiler_folder = '\\'.join(config.profiler.split('\\')[:-1])
    config.profiler = folder_input("CAST-Profiler folder location",profiler_folder,'CAST-Profiler.exe') + '\\CAST-Profiler.exe'

    if yes_no_input('Configure MRI automatic scans'):
        print ('')
        print ('Configuring for AIP Console')
        if yes_no_input('\tAre both "AIP Console Enterprise Edition" and the matching "AIP Console automation tools" installed?'):
            config.console_url = url_input('\t"AIP Console Enterprise Edition" URL',config.console_url)
            config.console_cli = folder_input('\t"AIP Console automation tools" location',dirname(config.console_cli),"aip-console-tools-cli.jar",True)
            config.console_key = string_input('\t"AIP Console Enterprise Edition" API Key',config.console_key)
            config.enable_security_assessment = yes_no_input('\tEnable security analysis',config.enable_security_assessment)
            config.blueprint = yes_no_input('\tEnable Blueprint analysis',config.blueprint)

        if config.is_console_active:
            print ('AIP Console configuration complete')
        else:
            print ('Error updating AIP Console configuration!')
        print ('\n')
    
    if yes_no_input('\tConfigure Highlight automatic scans'):
        if yes_no_input('\tAre both the Highlight Agent and Command Line Interface installed?'):

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
                config.hl_password = string_input('\t\tHighlight password',config.hl_password)
                config.hl_instance = string_input('\t\tHighlight instance id',config.hl_instance)

        if config.is_hl_active:
            print ('Highlight configuration complete')
        else:
            print ('Error updating Highlight configuration!')
        print ('\n')


        pass
    pass
