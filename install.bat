@echo off
setlocal EnableDelayedExpansion

:: Initialize the default PIP install version
set PIP_INSTALL_VERSION=1.6.9

:: Set Python version
set "python_version=3.10.6"

:: Check script name
if "%~0"=="install.bat" (

    :: Check for command-line arguments
    if not "%1"=="" (
        if "%1"=="upgrade" (
            echo Detected upgrade command...

            if not "%2"=="" (
                set "PIP_INSTALL_VERSION=%2"
             
            ) else (
                echo ...
            )
        )
    ) else (
        echo ...
    )
)
echo .
echo .
echo .
echo .
echo ============================================================
echo Installation version: com.castsoftware.uc.arg == %PIP_INSTALL_VERSION% 
echo ============================================================
echo .
echo .
echo .
echo .


:: Check for administrative permissions
echo =============================================================
echo Administrative permissions required; Detecting permissions...
echo =============================================================
net session >nul 2>&1
if %errorLevel% == 0 (
    echo .
    echo .
    echo .
    echo .
    echo =============================================
    echo Success: Administrative permissions confirmed
    echo =============================================
    echo .
    echo .
    echo .
    echo .
    goto PythonInstallCheck
) else (
    echo .
    echo .
    echo .
    echo .
    echo ===================================================================================
    echo Failure: Current permissions inadequate. Please run the script as an Administrator.
    echo ===================================================================================
    echo .
    echo .
    echo .
    echo .
    pause
    exit
)

:PythonInstallCheck
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python already installed.
    goto PipCheck
) else (
    goto PythonInstall
)

:PythonInstall
:: Define the URL and file name of the Python installer
set "url=https://www.python.org/ftp/python/%python_version%/python-%python_version%-amd64.exe"
set "installer=python-%python_version%-amd64.exe"

:: Define the installation directory
set "targetdir1=C:\Python%python_version%"

:: Download the Python installer
powershell -Command "(New-Object Net.WebClient).DownloadFile('%url%', '%~dp0%installer%')"

:: Install Python
echo Installing Python Version %python_version%...
start /wait "" "%~dp0%installer%" /quiet /passive TargetDir="%targetdir1%" Include_test=0 PrependPath=1 ^
&& (echo Done.) || (echo Failed!)
echo.

:: Cleanup
del "%~dp0%installer%"

goto PipCheck

:PipCheck

python -m ensurepip --default-pip
call pip --version 2>nul
if errorlevel 1 (
  echo PIP not found, please ensure it's installed.
  pause
  exit
) else (
  goto FolderCreation
)

:: OneClick base folder creation

:FolderCreation
if exist "T:\CAST\CODE" (
  echo .
  echo .
  echo ==========================================
  echo OneClick base folder already exists in T:\ 
  echo ==========================================
  echo .
  echo .
  goto :OC1
) else if exist "D:\CAST\CODE" (
  echo .
  echo .
  echo ==========================================
  echo OneClick base folder already exists in D:\ 
  echo ==========================================
  echo .
  echo .
  goto :OC2
) else if exist "C:\CAST\CODE" (
  echo .
  echo .
  echo ==========================================
  echo OneClick base folder already exists in C:\ 
  echo ==========================================
  echo .
  echo .
  goto :OC3
) else (
  goto create_Path
)

:create_Path
if exist "T:\" (
  mkdir "T:\CAST\CODE"
  echo .
  echo .
  echo ======================================================
  echo Success: Created the OneClick base folder T:\CAST\CODE 
  echo ======================================================
  echo .
  echo .
  goto :OC1
) else if exist "D:\" (
  mkdir "D:\CAST\CODE"
  echo .
  echo .
  echo ======================================================
  echo Success: Created the OneClick base folder D:\CAST\CODE 
  echo ======================================================
  echo .
  echo .
  goto :OC2
) else if exist "C:\" (
  mkdir "C:\CAST\CODE"
  echo .
  echo .
  echo ======================================================
  echo Success: Created the OneClick base folder C:\CAST\CODE 
  echo ======================================================
  echo .
  echo .
  goto :OC3
) else (
  echo .
  echo .
  echo ========================================
  echo Error: None of the required drives exist
  echo ========================================
  echo .
  echo .
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
echo .
echo .
echo ==========================
echo Configure for installation
echo ==========================
echo .
echo .

:: Check for Python Installation
python -m ensurepip --default-pip
call pip --version 2>NUL
echo .
echo .
echo ======================
echo pip --version %PIP_INSTALL_VERSION%
echo ======================
echo .
echo .
if errorlevel 1 goto noPip

echo creating virtual environment
IF NOT EXIST "%CODE_FOLDER%\DELIVER" MKDIR "%CODE_FOLDER%\DELIVER"
IF NOT EXIST "%CODE_FOLDER%\.oneClick" MKDIR "%CODE_FOLDER%\.oneClick"
IF NOT EXIST "%CODE_FOLDER%\SCRIPTS" MKDIR "%CODE_FOLDER%\SCRIPTS"
python -m pip install --user --upgrade pip > NUL

:: Rename .venv if it exists
if exist "%CODE_FOLDER%\.venv" (
    for /f "delims=" %%a in ('wmic os get LocalDateTime ^| find "."') do (
            set datetime=%%a
        )
        set datetime=!datetime:~0,14!
        set datetime=!datetime:~0,4!!datetime:~4,2!!datetime:~6,2!_!datetime:~8,2!!datetime:~10,2!!datetime:~12,2!
        rename "%CODE_FOLDER%\.venv" "venv_!datetime!"
    
)

:: Create a new .venv folder
if not exist "%CODE_FOLDER%\.venv" (
    python -m venv "%CODE_FOLDER%\.venv"
    if errorlevel 1 goto venvFail
)

call %CODE_FOLDER%\.venv\scripts\activate.bat

copy "%~dp0oneClick.bat" %CODE_FOLDER%
xcopy "%~dp0scripts" "%CODE_FOLDER%\SCRIPTS\" /E /H /C /I /Y  

echo .
echo .
echo ================================
echo adding Onclick package from PyPi
echo ================================
echo .
echo .

pip install com.castsoftware.uc.oneclick==1.0.0

echo .
echo .
echo .
echo .
echo =========================================
echo Success: OneClick installation is set up!
echo =========================================
echo .
echo .
echo .
echo .
goto config_setup

:missingCodeParam
echo .
echo .
echo ======================================
echo Missing Code Folder Location parameter
echo ======================================
echo .
echo .
goto usage

:missingCodeFolder
echo .
echo .
echo =====================================================
echo Destination folder "%CODE_FOLDER%" must already exist
echo =====================================================
echo .
echo .
goto usage

:noPip
echo .
echo .
echo =============
echo PIP not found
echo =============
echo .
echo .
goto usage

:venvFail
echo .
echo .
echo =====================================
echo Unable to install virtual environment
echo =====================================
echo .
echo .

goto usage

:usage
echo .
echo .
echo ================================
echo install ^<Code Folder Location^>
echo ================================
echo .
echo .

:config_setup
echo .
echo .
echo ======================================
echo OneClick global configuration setup...
echo ======================================
echo .
echo .

cd /d "%CODE_FOLDER%"
python -m oneclick.setup config -b %CODE_FOLDER%

call %CODE_FOLDER%\.venv\scripts\deactivate.bat

pause
exit /b