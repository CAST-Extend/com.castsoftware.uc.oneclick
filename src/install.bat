@echo off
::validate input parameters
set CODE_FOLDER=%1
if "%CODE_FOLDER%x" == "x" GOTO missingCodeParam
if not exist %CODE_FOLDER% goto missingCodeFolder

echo Configure for installation
:: Check for Python Installation

python --version 2>NUL
if errorlevel 1 (
	py --version
	if errorlevel 1 goto noPython
	set EXEC=py
) else set EXEC=python

:: Check for Python Installation
call pip --version 2>NUL
if errorlevel 1 goto noPip

echo creating virutal enviroment 
IF NOT EXIST "%CODE_FOLDER%\DELIVER" MKDIR "%CODE_FOLDER%\DELIVER"
IF NOT EXIST "%CODE_FOLDER%\.oneClick" MKDIR "%CODE_FOLDER%\.oneClick"
IF NOT EXIST "%CODE_FOLDER%\SCRIPTS" MKDIR "%CODE_FOLDER%\SCRIPTS"
%EXEC% -m pip install --user --upgrade pip > NUL

if not exist "%CODE_FOLDER%\.venv" %EXEC% -m venv "%CODE_FOLDER%\.venv"
if errorlevel 1 goto venvFail
call %CODE_FOLDER%\.venv\scripts\activate.bat

echo adding Onclick package from PyPi
pip install com.castsoftware.uc.oneClick
Call :UnZipFile "%CODE_FOLDER%" "scripts.zip"


call %CODE_FOLDER%\.venv\scripts\deactivate.bat

echo OneClick installation completed successfuly 
echo .
echo To use the tool, it must first be configured for more on this please
echo refer to the documentation at https://github.com/CAST-Extend/com.castsoftware.uc.oneclick/wiki#global-configuration

exit /b 

:UnZipFile <ExtractTo> <newzipfile>
set vbs="%temp%\_.vbs"
if exist %vbs% del /f /q %vbs%
>%vbs%  echo Set fso = CreateObject("Scripting.FileSystemObject")
>>%vbs% echo If NOT fso.FolderExists(%1) Then
>>%vbs% echo fso.CreateFolder(%1)
>>%vbs% echo End If
>>%vbs% echo set objShell = CreateObject("Shell.Application")
>>%vbs% echo set FilesInZip=objShell.NameSpace(%2).items
>>%vbs% echo objShell.NameSpace(%1).CopyHere(FilesInZip)
>>%vbs% echo Set fso = Nothing
>>%vbs% echo Set objShell = Nothing
cscript //nologo %vbs%
if exist %vbs% del /f /q %vbs%
exit /b

:missingCodeParam
echo Missing Code Folder Location parameter
goto usage

:missingCodeFolder
echo Destination folder "%CODE_FOLDER%" must already exist
goto usage

:noPython
echo Python version 10.x must be installed to use OneClick
goto usage

:noPip
echo PIP not found
goto usage

:venvFail
echo Unable to install virtual environment
goto usage

:usage
echo install ^<Code Folder Location^>
popd
exit /b