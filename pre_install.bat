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
set "python_version=3.10.6

:: Define the URL and file name of the Python installer
set "url=https://www.python.org/ftp/python/%python_version%/python-%python_version%-amd64.exe"
set "installer=python-%python_version%-amd64.exe"

:: Define the installation directory
set "targetdir1=C:\Python%python_version%"
set "targetdir2=C:\Python%python_version%\Scripts"


:: Download the Python installer
powershell -Command "(New-Object Net.WebClient).DownloadFile('%url%', '%~dp0%installer%')"

:: Install Python
echo Installing Python Version %latest_py_version%...
start /wait "" "%~dp0%installer%" /quiet /passive TargetDir="%targetdir1%" Include_test=0 ^
&& (echo Done.) || (echo Failed!)
echo.


:: Add Python to the system PATH
echo Adding Python to the system PATH...
setx PATH "%targetdir1%;%targetdir2%;%PATH%" /m
if %errorlevel% EQU 1 (
  echo Warning: Python has been successfully installed to your system BUT failed to set system PATH. Try running the script as administrator.
  pause
  exit
)
echo Success: Python %python_version% has been successfully installed and added to the system PATH

:: Cleanup
del "%~dp0%installer%"

echo .
echo .
echo .
echo Alert: Please run the `install.bat` file to continue with the oneClick installtion...
echo .
echo .
echo .

pause
exit /b