@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Tao moi truong ao...
    python -m venv venv
)

call "venv\Scripts\activate.bat"

echo Cai thu vien...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Da cai xong.
echo Mo file .env va dien GEMINI_API_KEY neu muon dung AI tong quat.
echo Sau do chay CHAY_WEB.bat
echo.
pause
