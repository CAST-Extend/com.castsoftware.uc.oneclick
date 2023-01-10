@echo off
call z:\work\com.castsoftware.uc.oneclick\.venv\Scripts\activate.bat


set PYTHONPATH=src;..\com.castsoftware.uc.python.common\src;..\com.castsoftware.uc.action-plan;..\com.castsoftware.uc.arg
set PYTHON=z:\work\com.castsoftware.uc.oneclick\.venv\Scripts\python.exe

%PYTHON% src\main.py %*

