# Hace una consulta con respuesta de Gemini (necesita GEMINI_API_KEY).
# Uso:  .\correr.ps1 "donde plantee nulidad de allanamiento y como lo redacte?"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
& "$PSScriptRoot\.venv\Scripts\python.exe" "$PSScriptRoot\src\preguntar.py" @args
