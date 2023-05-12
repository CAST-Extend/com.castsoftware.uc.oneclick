from argparse import ArgumentParser
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from os.path import abspath,exists,dirname
from os import chdir,getcwd,getenv
from oneclick.config  import Config
from oneclick.exceptions import NoConfigFound,InvalidConfiguration,InvalidConfigNoBase

def yes_no_input(prompt:str,default_value=True) -> bool:
    while True:
        if default_value:
            default_value='Y'
        else:
            default_value='N'

        val = input(f'{prompt} [{default_value}]?').upper()
        if len(val) == 0: val = default_value

        if val in ['Y','YES']:
            return True
        elif val in ['N','NO']:
            return False
        else:
            print ('Expecting a Y[es] or N[o] response. ',end='')

def url_input(prompt:str,url):
    val = URLValidator()
    while True:
        i = input(f'{prompt} [{url}]: ')
        if len(i)>0:
            url = i
        try:
            val(url)
            return url
        except ValidationError as e:
            print ("Bad URL, please try again")      

def folder_input(prompt:str,folder:str='',file:str=None,combine:bool=False) -> str:
    if combine:
        folder=folder.replace(file,'')

    while True:
        i = input(f'{prompt} [{abspath(folder)}]: ')
        if len(i)==0:
            folder = abspath(folder)
        else:
            folder = abspath(i)
        if exists(folder):
            if file is not None:
                if exists(abspath(f'{folder}/{file}')):
                    break
                else:
                    print (f'{folder} folder does not contain {file}, please try again')
                    continue
            else:
                break
        print (f'{folder} not found, please try again')

    if combine:
        folder = abspath(f'{folder}/{file}')
    return folder

def string_input(prompt:str,default_value=""):
    while True:
        if len(default_value)>0:
            i = input(f'{prompt} [{default_value}]: ')
        else:
            i = input(f'{prompt}: ')

        if len(i)==0:
            if len(default_value) == 0:
                print('Input required, please try again')
                continue
            else:
                i = default_value
        return i            


if __name__ == '__main__':

    print('\nCAST OneClick Setup')
    print('Copyright (c) 2023 CAST Software Inc.\n')
    print('If you need assistance, please contact Technical Due Diligence @team.ddassessment@castsoftware.com\n')


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


    if yes_no_input('Configure MRI automatic scans'):
        print ('')
        if yes_no_input('Are both "AIP Console Enterprise Edition" and the matching "AIP Console automation tools" installed?'):
            print ('\nConfiguring for AIP Console')
            config.console_url = url_input('\t"AIP Console Enterprise Edition" URL',config.console_url)
            config.console_cli = folder_input('\t"AIP Console automation tools" location',dirname(config.console_cli),"aip-console-tools-cli.jar",True)
            config.console_key = string_input('\t"AIP Console Enterprise Edition" Key',config.console_key)
            config.enable_security_assessment = yes_no_input('\tEnable security analysis',config.enable_security_assessment)
            config.blueprint = yes_no_input('\tEnable Blueprint analysis',config.blueprint)
            if config.is_console_active:
                print ('AIP Console configuration complete')
            else:
                print ('Error updating AIP Console configuration!')
            print ('\n')
    
    if yes_no_input('Configure Highlight automatic scans'):
        if yes_no_input('Are both the Highlight Agent and Command Line Interface installed?'):
            print ('\nConfiguring for Highlight')
            if len(config.hl_url)==0:
                config.hl_url = "https://rpa.casthighlight.com/"
            config.hl_url = url_input('\tHighlight URL',config.hl_url)
            config.hl_user = string_input('\tHighlight user name',config.hl_user)
            config.hl_password = string_input('\tHighlight password',config.hl_password)
            config.hl_instance = string_input('\tHighlight instance id',config.hl_instance)
            config.hl_cli = folder_input('\tHighlight command line interface installation location',config.hl_cli,'HighlightAutomation.jar',True)
            
            agent_folder = f'{config.perl_install_dir}'.replace('\\strawberry\\perl','')
            agent_folder = folder_input('\tHighlight agent installation location',agent_folder,'strawberry',False)
            config.perl_install_dir=abspath(f'{agent_folder}/strawberry/perl')
            config.analyzer_dir=abspath(f'{agent_folder}/perl')

            if config.is_console_active:
                print ('Highlight configuration complete')
            else:
                print ('Error updating Highlight configuration!')
            print ('\n')


        pass
    pass
