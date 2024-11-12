from oneclick.configTest import Config,Status
from cast_common.logger import Logger,INFO
from cast_common.util import run_process,check_process,format_table,create_folder
from oneclick.discovery.sourceValidation import SourceValidation 
from time import sleep

from platform import system
from os import remove
from os.path import exists,abspath,getsize
from re import findall
from pandas import DataFrame,ExcelWriter
from openpyxl import load_workbook
from tqdm import tqdm
from subprocess import Popen

from string import ascii_uppercase
from win32api import GetLogicalDriveStrings
from win32wnet import WNetOpenEnum,WNetEnumResource
from win32netcon import RESOURCE_REMEMBERED,RESOURCETYPE_DISK

from ctypes import windll, c_int, c_wchar_p
from time import sleep
from openpyxl import load_workbook

#TODO: Convert total line to formulas (d1-SHP)
#TODO: Format all numbers as integers not text (d1-SHP)
#TODO: Group tabs in pairs (before, after) then by application (d2)

class ClocPreCleanup(SourceValidation):
    writer = None

    @property
    def max_cloc(cls):
        return ClocPreCleanup._max_cloc
    @property
    def running_cloc(cls):
        return ClocPreCleanup._running_cloc
    @running_cloc.setter
    def running_cloc(cls,value):
        ClocPreCleanup._running_cloc = value

    @property
    def choose(self) -> bool:
        return True
    
    @property
    def name(self) -> str:
        return 'Technology Discovery - Before Cleanup'

    def __init__(cls):
        ClocPreCleanup._max_cloc=2
        ClocPreCleanup._running_cloc=0
        cls._df = {}
        pass

    @property
    def phase(cls):
        return 'Before'

    @property
    def cloc_base(cls):
        return f'{cls.config.base}\\cloc' 
    @property
    def cloc_project(cls):
        return f'{cls.cloc_base}\\{cls.config.project_name}'

    @property
    def cloc_results(cls):
        return cls._df

    def cloc_output_path(cls,appl:str):
        return abspath(f'{cls.config.report_folder}/{cls.config.project_name}/{appl}/{appl}-cloc-{cls.phase}.txt')

    def cloc_output_ignore_path(cls,appl:str):
        return abspath(f'{cls.config.report_folder}/{cls.config.project_name}/{appl}/{appl}-cloc-ignored-{cls.phase}.txt')

    def _get_free_drive(cls):
        drives = set(ascii_uppercase[2:])
        for d in GetLogicalDriveStrings().split(':\\\x00'):
            drives.discard(d)
        # Discard persistent network drives, even if not connected.
        henum = WNetOpenEnum(RESOURCE_REMEMBERED, 
            RESOURCETYPE_DISK, 0, None)
        while True:
            result = WNetEnumResource(henum)
            if not result:
                break
            for r in result:
                if len(r.lpLocalName) == 2 and r.lpLocalName[1] == ':':
                    drives.discard(r.lpLocalName[0])
        if drives:
            return sorted(drives)[-1] + ':'

    def _run_cloc(cls,work_folder:str,cloc_output:str,cloc_output_ignored:str):
        args = [cls.config.cloc,work_folder,"--report-file",cloc_output,"--ignored",cloc_output_ignored,"--quiet"]
        cls.log.debug(' '.join(args))
        proc = run_process(args,False)
        if proc.poll() is not None and exists(cloc_output):
            return 'DONE'
        else:
            return proc

    def run(cls):

        config = cls.config
        # cls.open_excel_writer()
        
        #cls.cloc_path=abspath(f'{config.base}\\scripts\\{cls.config.cloc_version}')
        
        list_of_tech_file=abspath(f'{config.scripts_folder}/ListOfTechnologies.csv')
        with open(list_of_tech_file) as f:
            cls.tech_list = f.read().splitlines()
            
        process = {}
        output = {}
        cloc_run=False

        # create a subst drive
        DefineDosDevice = windll.kernel32.DefineDosDeviceW
        DefineDosDevice.argtypes = [ c_int, c_wchar_p, c_wchar_p ]

        project_folder=abspath(f'{config.stage_folder}/{config.project_name}')
        # Create a subst. Check the return for non-zero to mean success
        drive=project_folder
        platform = system()
        if platform == 'Windows':
            drive = cls._get_free_drive()
            if drive is None or DefineDosDevice(0, drive, project_folder ) == 0:
                raise RuntimeError("Subst failed")

        for appl in config.applist:
            app_status = appl['status']['aip']

            # was there an error with the last run
            # if so we need to reset the status to restart cloc
            if cls.phase=='Before' and app_status == Status.CLOC_PRE_CLEAN_ERROR:
                appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_START
            elif cls.phase=='After' and app_status == Status.CLOC_POST_CLEAN_ERROR:
                appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_POST_CLEAN_START

        print(cls.show_progress())

        create_folder(abspath(f'{config.report_folder}/{config.project_name}'))

        # if cls.phase=='Before':
        #     ClocPreCleanup.writer = ExcelWriter(ClocPreCleanup.excel_file_name, engine='xlsxwriter')

        # do a little cleanup        
        for appl in config.applist:
            app_name = appl['name']
            app_status = appl['status']['aip']
            cloc_output = cls.cloc_output_path(app_name)
            cloc_output_ignored = cls.cloc_output_ignore_path(app_name)

            # if config.start== cls.name:
            #     if cls.phase=='Before':
            #         appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_REPORT
            #     else:
            #         appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_POST_CLEAN_START

            if (cls.phase=='Before' and (app_status == Status.CLOC_PRE_CLEAN_QUEUE or app_status < Status.CLOC_PRE_CLEAN_START)) or \
                (cls.phase=='After' and (app_status == Status.CLOC_POST_CLEAN_QUEUE or app_status < Status.CLOC_POST_CLEAN_START)) :
                if exists(cloc_output):
                    cls.config.log.info(f'Removing {cloc_output}')
                    remove(cloc_output)
                    print(cls.show_progress())
                if exists(cloc_output_ignored):
                    cls.config.log.info(f'Removing {cloc_output_ignored}')
                    remove(cloc_output_ignored)
                    print(cls.show_progress())
                if 'loc' in appl:
                    appl['loc']=''

        print(cls.show_progress())

        #run cloc for all applications
        while True:
            for appl in config.applist:
                app_name = appl['name']
                app_status = appl['status']['aip']

                if (cls.phase == 'Before' and app_status >= Status.CLOC_PRE_CLEAN_END) or \
                    (cls.phase == 'After' and app_status >= Status.CLOC_POST_CLEAN_END):
                        continue

                create_folder(f'{config.report_folder}/{config.project_name}/{app_name}')
                cloc_output = cls.cloc_output_path(app_name)
                cloc_output_ignored = cls.cloc_output_ignore_path(app_name)
                if platform == 'Windows':            
                    work_folder = abspath(f'{drive}/{app_name}')
                else:
                    work_folder = abspath(f'{config.work}/{config.project_name}/{app_name}')

                #if the report is already out there - no need to continue
                if (cls.phase=='Before' and app_status in [Status.CLOC_PRE_CLEAN_QUEUE,Status.CLOC_PRE_CLEAN_START,Status.UNPACK_END]) or \
                   (cls.phase=='After' and app_status in [Status.CLOC_POST_CLEAN_QUEUE,Status.CLOC_POST_CLEAN_START,Status.SOURCE_CLEAN_END]) :
                    #this application cloc run has been queued, can we run it now?
                    if cls.running_cloc < cls.max_cloc:
                        # if it exists, remove the report file

                        proc = cls._run_cloc(work_folder, cloc_output, cloc_output_ignored)
                        if proc == 'DONE':
                            appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_REPORT if cls.phase=='Before' else Status.CLOC_POST_CLEAN_REPORT
                            config._save()
                        else:
                            cls.running_cloc += 1
                            process[app_name] = proc
                            appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_RUNNING if cls.phase=='Before' else Status.CLOC_POST_CLEAN_RUNNING
                            config._save()

                elif (cls.phase=='Before' and app_status == Status.CLOC_PRE_CLEAN_RUNNING) or \
                     (cls.phase=='After' and app_status == Status.CLOC_POST_CLEAN_RUNNING):
                    #cloc is running fvor this application, check if it has completed yet
                    try:
                        #get the results
                        if (app_name in process and process[app_name].poll() is None):
                            pass
                        else:
                            if exists(cloc_output) and getsize(cloc_output) > 0:
                                if cls.phase == 'Before':
                                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_REPORT
                                elif cls.phase == 'After':
                                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_POST_CLEAN_REPORT
                                # process[app_name]='DONE'
                                cls.running_cloc -= 1
                            else:
                                if cls.phase == 'Before':
                                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_ERROR
                                elif cls.phase == 'After':
                                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_POST_CLEAN_ERROR

                                output, error = process[app_name].communicate()

                                print(cls.show_progress(done=True))
                                config.log.error(output.decode())

                            config._save()

                    except IOError:
                        if not exists(cloc_output) and getsize(cloc_output) == 0:
                            cls.log.error(f'Error running cloc on {cloc_output}')
                    except ValueError as ex:
                        if str(ex) == 'read of closed file':
                            cls.log.debug(f'Process already closed {app_name}')
                    except Exception as ex:
                        cls.log.warning(f'{type(ex)} Error: {str(ex)}')
                        pass

                if cls.phase == 'Before' and app_status == Status.CLOC_PRE_CLEAN_REPORT and not exists(cloc_output):
                    #something went wrong with the cloc run
                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_ERROR
                    continue
                if cls.phase == 'After' and app_status == Status.CLOC_POST_CLEAN_REPORT and not exists(cloc_output):
                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_POST_CLEAN_ERROR
                    continue

                if (cls.phase == 'Before' and app_status == Status.CLOC_PRE_CLEAN_REPORT) or \
                   (cls.phase == 'After' and app_status == Status.CLOC_POST_CLEAN_REPORT) :
                    cls.process_results()
                    appl['status']['aip'] = appl['status']['highlight'] = Status.CLOC_PRE_CLEAN_END if cls.phase=='Before' else Status.CLOC_POST_CLEAN_END
                print(cls.show_progress())
                sleep(1)
            print(cls.show_progress())

            # are we done with all applications?
            done = True
            for appl in config.applist:
                app_status = appl['status']['aip']
                if (cls.phase == 'Before' and app_status < Status.CLOC_PRE_CLEAN_END) or \
                   (cls.phase == 'After' and app_status < Status.CLOC_POST_CLEAN_END) :
                    done = False
                    break
            if done:
                break

        # Delete the subst.
        if platform == 'Windows' and DefineDosDevice(2, drive, project_folder ) == 0:
            raise RuntimeError("Subst failed")

        if cls.phase == 'After' and ClocPreCleanup.writer is not None:
            ClocPreCleanup.writer.close()


        config._save()
        cls.log.info(cls.show_progress(True))

        cloc_location = abspath(f'{config.report_folder}/{config.project_name}')
        cls.log.info(f'All pre cleanup CLOC reports generated for project: {config.project_name}, see {cloc_location}')
        return True

    def process_results(self):

        def parse_rpt(app_name,cloc_output,cloc_output_ignored,phase):
            with open(cloc_output, 'r') as f:
                content = f.read()

            #extracting required data from content of cloc_output.txt using python regex
            header=content.split('\n')[2]
            header_list=findall('\w+',header.upper())

            summary='\n'.join(content.split('\n')[4:-4])
            pattern='(.{25})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})\s{1,}(\d{1,})'
            statistics_list=findall(pattern,summary)
            with open(cloc_output_ignored, 'r') as fp:
                lines = len(fp.readlines())
            statistics_list.append(('Unknown Files','0','0','0',str(lines)))
            df = DataFrame(statistics_list,columns=header_list)

            #making technolgy case insensitive
            self.tech_list = list(map(lambda x: x.lower().strip(), self.tech_list))
            df['APPLICABLE']=df['LANGUAGE'].str.lower().str.strip().isin(self.tech_list)

            #converting column values into int from string
            numbers=['FILES','BLANK','COMMENT','CODE']
            total_line=['']
            for name in numbers:
                df[name] = df[name].astype('int')
            tab_name = f'{app_name}-{phase}'
            tab_name = (tab_name[:30] + '..') if len(tab_name) > 30 else tab_name
            loc = df['CODE'].sum()
            appl['loc']= f'{loc:>10,.0f}'
            return df,tab_name


        config = self.config
        excel_file_name = abspath(f'{config.report_folder}/{config.project_name}/{config.project_name}-cloc.xlsx')
        if exists(excel_file_name):
            remove(excel_file_name)
        writer = ExcelWriter(excel_file_name, engine='xlsxwriter')

        for appl in config.applist:
            status = appl['status']['aip']
            app_name = appl['name']

            if status >= Status.CLOC_PRE_CLEAN_REPORT:
                before_cloc_rpt = abspath(f'{config.report_folder}/{config.project_name}/{app_name}/{app_name}-cloc-Before.txt')
                before_ignr_rpt = abspath(f'{config.report_folder}/{config.project_name}/{app_name}/{app_name}-cloc-ignored-Before.txt')
                after_cloc_rpt = abspath(f'{config.report_folder}/{config.project_name}/{app_name}/{app_name}-cloc-After.txt')
                after_ignr_rpt = abspath(f'{config.report_folder}/{config.project_name}/{app_name}/{app_name}-cloc-ignored-After.txt')

                if status >= Status.CLOC_PRE_CLEAN_REPORT and exists(before_cloc_rpt) and exists(before_ignr_rpt):
                    df,tab_name = parse_rpt(app_name, before_cloc_rpt, before_ignr_rpt, 'Before')
                    format_table(writer, df, tab_name, total_line=True)

                if status >= Status.CLOC_POST_CLEAN_REPORT and exists(after_cloc_rpt) and exists(after_ignr_rpt):
                    df,tab_name = parse_rpt(app_name, after_cloc_rpt, after_ignr_rpt, 'After')
                    format_table(writer, df, tab_name, total_line=True)

        writer.close()
        pass

class ClocPostCleanup(ClocPreCleanup):
    @property
    def choose(self) -> bool:
        return False
    
    @property
    def name(self) -> str:
        return 'Technology Discovery - After Cleanup'

    def __init__(cls):
        pass
    
    @property
    def phase(cls):
        return 'After'

        