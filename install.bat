@echo off
setlocal EnableDelayedExpansion

:: OneClick base folder creation
if exist "T:\CAST\CODE" (
  echo OneClick base folder already exists in T:\
  goto :OC1
) else if exist "D:\CAST\CODE" (
  echo OneClick base folder already exists in D:\
  goto :OC2
) else if exist "C:\CAST\CODE" (
  echo OneClick base folder already exists in C:\
  goto :OC3
) else (
  goto create_Path
)

:create_Path
if exist "T:\" (
  mkdir "T:\CAST\CODE"
  echo Success: Created the OneClick base folder T:\CAST\CODE
  goto :OC1
) else if exist "D:\" (
  mkdir "D:\CAST\CODE"
  echo Success: Created the OneClick base folder D:\CAST\CODE
  goto :OC2
) else if exist "C:\" (
  mkdir "C:\CAST\CODE"
  echo Success: Created the OneClick base folder C:\CAST\CODE
  goto :OC3
) else (
  echo Error: None of the required drives exist.
  pause
  exit
)

:: OneClick installation
:OC1
cd /d "T:\CAST\CODE"
goto :start
:OC2
cd /d "D:\CAST\CODE"
goto :start
:OC3
cd /d "C:\CAST\CODE"
goto :start

:: OneClick File Creation
:: Validate input parameters
:start
set CODE_FOLDER=%1\CAST\CODE
if "%CODE_FOLDER%x" == "x" goto missingCodeParam
if not exist %CODE_FOLDER% goto missingCodeFolder
echo Configure for installation

:: Check for Python Installation
python -m ensurepip --default-pip
call pip --version 2>NUL
echo pip --version
echo .
echo .
echo .
echo .
if errorlevel 1 goto noPip

echo creating virutal enviroment 
IF NOT EXIST "%CODE_FOLDER%\DELIVER" MKDIR "%CODE_FOLDER%\DELIVER"
IF NOT EXIST "%CODE_FOLDER%\.oneClick" MKDIR "%CODE_FOLDER%\.oneClick"
IF NOT EXIST "%CODE_FOLDER%\SCRIPTS" MKDIR "%CODE_FOLDER%\SCRIPTS
python -m pip install --user --upgrade pip > NUL

if not exist "%CODE_FOLDER%\.venv" python -m venv "%CODE_FOLDER%\.venv"
if errorlevel 1 goto venvFail
call %CODE_FOLDER%\.venv\scripts\activate.bat

copy "%~dp0oneClick.bat" %CODE_FOLDER%
xcopy "%~dp0scripts" "%CODE_FOLDER%\SCRIPTS\" /E /H /C /I /Y  

echo adding Onclick package from PyPi
pip install com.castsoftware.uc.oneclick==0.2.2.9

echo .
echo .
echo .
echo Success: OneClick installation is setup!
echo .
echo .
echo .
goto config_setup

:missingCodeParam
echo Missing Code Folder Location parameter
goto usage

:missingCodeFolder
echo Destination folder "%CODE_FOLDER%" must already exist
goto usage

:noPip
echo PIP not found
goto usage

:venvFail
echo Unable to install virtual environment
goto usage

:usage
echo install ^<Code Folder Location^>

:config_setup
echo OneClick global configuration setup...

cd /d "%CODE_FOLDER%"
python -m oneclick.setup config -b %CODE_FOLDER%

call %CODE_FOLDER%\.venv\scripts\deactivate.bat

pause
exit /b