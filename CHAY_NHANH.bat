@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (py -m venv venv 2>nul || python -m venv venv)
echo [1/3] Cai thu vien...
venv\Scripts\python.exe -m pip install -r requirements.txt
echo [2/3] Kiem tra MySQL...
venv\Scripts\python.exe KIEM_TRA_MYSQL.py
if errorlevel 1 (
 echo Chua ket noi duoc MySQL. Sua MYSQL_PASSWORD trong file .env.
 pause
 exit /b 1
)
echo [3/3] Chay web...
venv\Scripts\python.exe -m streamlit run app.py
pause
