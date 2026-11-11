# Busca en el indice (100% local, sin costo, no necesita clave).
# Uso:  .\buscar.ps1 "nulidad de allanamiento sin orden"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\src\buscar.py" @args
