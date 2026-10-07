@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist library.db del /q library.db
echo Da xoa database. Lan chay tiep theo se tao lai du lieu demo.
pause
