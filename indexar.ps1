# Indexa documentos. Sin argumentos usa datos/ejemplos.
# Uso:  .\indexar.ps1            (ejemplos)
#       .\indexar.ps1 "C:\ruta\a\estudio"   (otra carpeta)
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\src\indexar.py" @args
