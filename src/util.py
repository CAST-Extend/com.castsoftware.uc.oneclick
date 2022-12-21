from os import mkdir
from os.path import exists,abspath,join
from subprocess import Popen,PIPE,CalledProcessError

import sys



def resource_path(relative_path):
    "get the absolute path to resource, works for dev and for PyInstaller"
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = abspath('.')
    return join(base_path, relative_path)

def create_folder(folder):
    if not exists(folder):
        mkdir(folder)

def run_process(args) -> int:
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        line = line.decode('utf8').lstrip("b'").rstrip('\n')
        if len(line.strip(' ')) > 0:
            print(line)
        ret.append(line)
    stdout, stderr = process.communicate()
    # ret += str(stdout).split('\n')
    # if stderr != b'':
    #     ret += str(stderr).split('\n')
    return process.returncode,ret

def format_table(writer, data, sheet_name,width=None):
    
    data.to_excel(writer, index=False, sheet_name=sheet_name, startrow=1,header=False)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    rows = len(data)
    cols = len(data.columns)-1
    columns=[]
    for col_num, value in enumerate(data.columns.values):
        columns.append({'header': value})

    table_options={
                'columns':columns,
                'header_row':True,
                'autofilter':True,
                'banded_rows':True
                }
    worksheet.add_table(0, 0, rows, cols,table_options)
    
    header_format = workbook.add_format({'text_wrap':True,
                                        'align': 'center'})

    col_width = 10
    if width == None:
        width = []
        for i in range(1,len(data.columns)+1):
           width.append(col_width)
    for col_num, value in enumerate(data.columns.values):
        worksheet.write(0, col_num, value, header_format)
        w=width[col_num]
        worksheet.set_column(col_num, col_num, w)
    return worksheet

