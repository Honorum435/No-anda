@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo El Asistente Legal no esta instalado todavia. Corre primero "instalar.bat".
    pause
    exit /b
)
echo Abriendo el Asistente Legal... (se abre solo en el navegador en unos segundos)
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0abrir.ps1"
