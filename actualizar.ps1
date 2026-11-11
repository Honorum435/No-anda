# Actualiza el archivo del estudio: baja de Google Drive lo NUEVO/cambiado,
# convierte los .doc nuevos a .docx e indexa SOLO lo nuevo (incremental).
#
# Lo corre EL HIJO en su PC (la que tiene rclone + GPU). NO en la PC del papa.
# Nota: confirma que el remoto/origen de rclone ("gdrive:MochiPato" con --drive-shared-with-me)
#       coincida con tu configuracion; es el mismo que se uso en la bajada inicial.
$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot

$rclone = "C:\Users\Usuario\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.74.2-windows-amd64\rclone.exe"
$dest = "$PSScriptRoot\datos\drive_casos\MochiPato"

Write-Host "==> [1/4] Bajando de Google Drive lo nuevo/cambiado (rclone)..."
& $rclone copy "gdrive:MochiPato" $dest --drive-shared-with-me --include "*.{docx,doc,pdf,txt}" --progress

Write-Host ""
Write-Host "==> [2/4] Convirtiendo .doc nuevos a .docx (Word)..."
& "$PSScriptRoot\.venv\Scripts\python.exe" "src\convertir_word.py" $dest

Write-Host ""
Write-Host "==> [3/4] Indexando SOLO lo nuevo..."
& "$PSScriptRoot\.venv\Scripts\python.exe" "src\actualizar.py" $dest

Write-Host ""
Write-Host "==> [4/4] OCR de los PDF escaneados nuevos (sin capa de texto)..."
& "$PSScriptRoot\.venv\Scripts\python.exe" "src\ocr.py" $dest

Write-Host ""
Write-Host "Listo. El archivo quedo actualizado."
