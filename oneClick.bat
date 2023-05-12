@@echo off

set option=%1
set base=%cd%

if "%option%x" == "x" goto error
if "%option%" == "run" goto ok
if "%option%" == "config" goto ok
goto error
:ok

call .\.venv\scripts\activate
for /f "tokens=1,* delims= " %%a in ("%*") do set ALL_BUT_FIRST=%%b
python -m oneclick.main %option% -b %base% %ALL_BUT_FIRST%

exit /b
:error
echo first parameter must be either "config" or "run"
