# Permite que el celular entre al Asistente Legal: agrega una regla al Firewall de
# Windows para el puerto 8510, SOLO en redes privadas (la de tu casa u oficina; no en
# un Wi-Fi publico). El acceso igual pide PIN.
# Se ejecuta una sola vez y necesita permiso de administrador: "Permitir celular.bat"
# lo pide solo.
param([switch]$SinInteraccion)   # lo usa el instalador grafico: no espera "Enter"
$regla  = "Asistente Legal (celular)"
$puerto = 8510

$esAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
           ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $esAdmin) {
    Start-Process powershell -Verb RunAs -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" + $(if ($SinInteraccion) { " -SinInteraccion" } else { "" }))
    exit
}

try {
    Get-NetFirewallRule -DisplayName $regla -ErrorAction SilentlyContinue | Remove-NetFirewallRule
    New-NetFirewallRule -DisplayName $regla -Direction Inbound -Protocol TCP -LocalPort $puerto `
        -Action Allow -Profile Private | Out-Null
    Write-Host ""
    Write-Host "  [OK] Listo: el celular ya puede entrar al asistente (con PIN)." -ForegroundColor Green
    Write-Host ""
    $publicas = Get-NetConnectionProfile | Where-Object { $_.NetworkCategory -eq "Public" }
    if ($publicas) {
        Write-Host "  [!] Tu red figura como PUBLICA en Windows: asi el celular no va a poder entrar." -ForegroundColor Yellow
        Write-Host "      Si es la red de tu casa u oficina, cambiala a PRIVADA en:" -ForegroundColor Yellow
        Write-Host "      Configuracion > Red e Internet > (tu Wi-Fi) > Tipo de perfil de red > Privada" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [X] No se pudo agregar la regla: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""
if (-not $SinInteraccion) { Read-Host "Enter para cerrar" }
