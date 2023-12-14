from argparse import ArgumentParser

from cast_common.logger import ERROR
from os.path import abspath,exists,dirname
from os import chdir,getcwd,getenv
from oneclick.config  import Config,yes_no_input,folder_input,url_input,string_input,set_value
from oneclick.exceptions import NoConfigFound,InvalidConfiguration,InvalidConfigNoBase

def print_restart(config,error):
    msg = f"""
        {error}
        
        To rerun OneClick setup open a command prompt go to the {config.base} folder and 
        run "OneClick setup -b {config.base}"
    """
    print (msg)
    exit(1)
    

if __name__ == '__main__':

    print('\nCAST OneClick Setup')
    print('Copyright (c) 2023 CAST Software Inc.')
    print('For assistance, we can be reached at oneclick@castsoftware.com\n')

    parser = ArgumentParser(prog='OneClick')
    subparsers = parser.add_subparsers(title='command',dest='command')
    config_parser = subparsers.add_parser('setup')
    config_parser.add_argument('-b','--baseFolder', required=True, help='Base Folder Location',metavar='BASE_FOLDER')
    config_parser.add_argument('-d','--debug',type=bool)
    config_parser.add_argument('-p','--projectName', help='Name of the project')

    # base = folder_input('Where is OneClick installed ')
    try:
        config = Config(parser,log_level=ERROR)
    except InvalidConfigNoBase as e:
        print (e)
        exit(1)

    print('Greetings and welcome to OneClick setup. This setup is used to configure settings that are global to all applications.\n')

    chdir(config.base)
    print (f'OneClick installation location: {getcwd()}')

    config.cloc_version='cloc-1.96.exe'
    if len(config.java_home) == 0:
        config.java_home=getenv('JAVA_HOME')
    if len(config.java_home) == 0:
        if yes_no_input ('The JAVA_HOME environment variable cannot be found, is Java installed?'):
            config.java_home = folder_input("Java installation folder location",config.java_home,'bin/java.exe')
        else:
            print_restart(config,'Java is required for OneClick to work properly, please install it and rerun setup')
    else:
        print (f'JAVA_HOME is set to {config.java_home}')

    msg = """
Application Analysis: 

    To utilize OneClick for application scanning, one can utilize either the Imaging Console or the Highlight CLI. It 
    is essential to ensure that both oneclick and Imaging Console are installed on the same server.

    Will OneClick be used to analyze applications using the Imaging Console?"""
    if yes_no_input(msg):
        config.console_url = url_input('\tAIP Console Enterprise Edition URL',set_value(config.console_url,'http://localhost:8081'))
        config.console_cli = folder_input('\tWhere are the AIP Console automation tools installed?',config.console_cli,"aip-console-tools-cli.jar",True)
        config.console_key = string_input('\tAIP Console Enterprise Edition API Key',config.console_key)
        config.enable_security_assessment = yes_no_input('\tEnable security analysis',config.enable_security_assessment)
        config.blueprint = yes_no_input('\tEnable Blueprint analysis',config.blueprint)
    else:
        config.console['Active']=False
        config._save()
        msg = f"""
    OneClick will not include MRI Application Analysis.  To enable it rerun setup

    OneClick setup -b {config.base}"""

    msg = """
    In order to conduct a Highlight analysis, OneClick relies on both the Highlight CLI and Agent. It is important to 
    ensure that both are easily accessible. Are you planning on utilizing OneClick for Highlight analysis of your applications?"""
    if yes_no_input(msg):
        config.hl_cli = folder_input('\tHighlight command line interface installation location',config.hl_cli,'HighlightAutomation.jar',True)
        agent_folder = f'{config.perl_install_dir}'.replace('\\strawberry\\perl','')
        agent_folder = folder_input('\tHighlight agent installation location',agent_folder,'strawberry',False)
        config.perl_install_dir=abspath(f'{agent_folder}/strawberry/perl')
        config.analyzer_dir=abspath(f'{agent_folder}/perl')

        msg = """
        While running OneClick, users may be prompted to enter the Highlight URL and Credentials. Alternatively, these can be configured 
        for all applications. Would it be beneficial to use the same URL and credentials for all applications?"""

        if yes_no_input(msg):
            if len(config.hl_url)==0:
                config.hl_url = "https://rpa.casthighlight.com/"
            config.hl_url = url_input('\t\tHighlight URL',config.hl_url)
            config.hl_url = f"{config.hl_url}"
            config.hl_user = string_input('\t\tHighlight user name',config.hl_user)
            config.hl_password = string_input('\t\tHighlight password',config.hl_password)
            config.hl_instance = string_input('\t\tHighlight instance id',config.hl_instance)
        else:
            config.hl_user = ''
            config.hl_password = ''
            config.hl_instance = ''

    else:
        msg = f"""
    OneClick will not include Highlight Application Analysis.  To enable it rerun setup

    OneClick setup -b {config.base}"""


    msg = f"""
CAST Profiler Installation:

    OneClick can run CAST Profiler as part of the application code discovery process. To include it please
    download the CLI from https://profiler.castsoftware.io/ and unpack the zip file where OneClick can access it.

    Should CAST Profiler be included as part of the application code discovery"""
    profiler_folder = ''
    if yes_no_input (msg):
        if len(config.profiler) > 0:
            profiler_folder = '\\'.join(config.profiler.split('\\')[:-1])
        config.profiler = folder_input("    CAST-Profiler CLI installation location",profiler_folder,'CAST-Profiler.exe') + '\\CAST-Profiler.exe'
    else: 
        config.profiler=''
        msg = f"""
    OneClick will not include CAST Profiler.  To enable it rerun setup

    OneClick setup -b {config.base}"""
   
        pass
    pass

    print (f"""
    Setup Complete!
    
        To run oneclick go to the {config.base} folder and run: OneClick run -p <project>
        For more information refer to: https://github.com/CAST-Extend/com.castsoftware.uc.oneclick/wiki/Running-OneClick
    """)
