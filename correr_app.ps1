# Abre la interfaz web de chat en el navegador.
# Uso:  .\correr_app.ps1
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot   # asegura que Streamlit tome .streamlit\config.toml (el tema)
& "$PSScriptRoot\.venv\Scripts\python.exe" -m streamlit run "src\app.py"
