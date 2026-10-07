@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (py -m venv venv 2>nul || python -m venv venv)
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe KIEM_TRA_MYSQL.py
pause
