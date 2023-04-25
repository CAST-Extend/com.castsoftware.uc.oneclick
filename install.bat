@echo off
setlocal EnableDelayedExpansion

:: Check for administrative permissions
  echo Administrative permissions required. Detecting permissions...
  net session >nul 2>&1
  if %errorLevel% == 0 (
    echo Success: Administrative permissions confirmed.
    goto :app1
  ) else (
    echo Failure: Current permissions inadequate.
    echo Please run the script as an Administrator.
    pause
    exit
  )

:: Set Python version
:app1
set "python_version=3.10.0

:: Define the URL and file name of the Python installer
set "url=https://www.python.org/ftp/python/%python_version%/python-%python_version%-amd64.exe"
set "installer=python-%python_version%-amd64.exe"

:: Define the installation directory
set "targetdir1=C:\Python%python_version%"
set "targetdir2=C:\Python%python_version%\Scripts"


:: Download the Python installer
powershell -Command "(New-Object Net.WebClient).DownloadFile('%url%', '%~dp0%installer%')"

:: Install Python
echo Installing Python Version %latest_py_version%
start /wait "" "%~dp0%installer%" /quiet /passive TargetDir="%targetdir1%" Include_test=0 ^
&& (echo Done.) || (echo Failed!)
echo.


:: Add Python to the system PATH
echo Adding Python to the system PATH...
setx PATH "%targetdir1%;%targetdir2%;%PATH%" /m
if %errorlevel% EQU 1 (
  echo Python has been successfully installed to your system BUT failed to set system PATH. Try running the script as administrator.
  pause
  exit
)
echo Python %python_version% has been successfully installed and added to the system PATH.

:: Cleanup
echo Cleaning up...
echo .
echo .
echo .
del "%~dp0%installer%"

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
copy "%~dp0oneClick.bat" %CODE_FOLDER%
goto :start
:OC2
cd /d "D:\CAST\CODE"
copy "%~dp0oneClick.bat" %CODE_FOLDER%
goto :start
:OC3
cd /d "C:\CAST\CODE"
copy "%~dp0oneClick.bat" %CODE_FOLDER%
goto :start


:start
cls
start cmd /k "%~dp0_.bat"
exit