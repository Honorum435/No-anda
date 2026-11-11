@echo off
chcp 65001 >nul
echo Cerrando el Asistente Legal...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*streamlit*run*app.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo Listo, el Asistente Legal esta cerrado. Podes cerrar esta ventana.
timeout /t 3 >nul
