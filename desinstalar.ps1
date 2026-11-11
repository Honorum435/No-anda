# Quita el Asistente Legal del escritorio y del menu Inicio, y lo cierra.
# NO borra los datos (causas, indice, historial, clave): la carpeta queda como esta.
$ErrorActionPreference = "SilentlyContinue"
$raiz = $PSScriptRoot

Write-Host ""
Write-Host "Desinstalando los accesos del Asistente Legal..." -ForegroundColor Cyan

# 1) Cerrar la app (escritorio y celular).
Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -like '*streamlit*run*app.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Remove-Item (Join-Path $raiz "datos\.celular_activo") -Force

# 2) Accesos directos.
Remove-Item (Join-Path ([Environment]::GetFolderPath('Desktop')) "Asistente Legal.lnk") -Force
Remove-Item (Join-Path ([Environment]::GetFolderPath('Programs')) "Asistente Legal") -Recurse -Force

# 3) Inscripcion en "Agregar o quitar programas".
Remove-Item "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistenteLegal" -Recurse -Force

# 4) Regla del firewall para el celular (si se habia agregado; necesita administrador).
if (Get-NetFirewallRule -DisplayName "Asistente Legal (celular)") {
    Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -Command "Get-NetFirewallRule -DisplayName ''Asistente Legal (celular)'' | Remove-NetFirewallRule"'
}

Write-Host "  [OK] Listo. Se quitaron los accesos y la inscripción en Agregar o quitar programas." -ForegroundColor Green
Write-Host ""
Write-Host "  Sus datos siguen en: $raiz" -ForegroundColor Yellow
Write-Host "  Si desea borrarlo del todo, borre esa carpeta (ojo: ahi estan el indice y el historial)."
Write-Host ""
Read-Host "Enter para cerrar"
