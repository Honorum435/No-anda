# OCR de los PDFs escaneados del archivo y reindexado (lo corre EL HIJO, en la PC con GPU).
# Requiere Tesseract instalado (ver INSTALAR_TESSERACT mas abajo) y datos de idioma 'spa'.
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
Set-Location $PSScriptRoot

Write-Host "==> OCR (espanol) de los PDF escaneados + indexado..."
& "$PSScriptRoot\.venv\Scripts\python.exe" "src\ocr.py"
Write-Host "Listo."
