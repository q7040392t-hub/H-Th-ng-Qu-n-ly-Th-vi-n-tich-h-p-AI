@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    call CAI_DAT_LAN_DAU.bat
)

call "venv\Scripts\activate.bat"

echo Dang mo he thong thu vien...
echo http://localhost:8501
python -m streamlit run app.py
pause
