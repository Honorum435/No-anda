# Abre el Asistente Legal como app de escritorio: ventana propia, sin pestanas ni barra
# de direcciones del navegador.
# - Si el servidor ya esta andando, solo abre la ventana.
# - Si no, limpia instancias trabadas y lo levanta OCULTO y SOLO para esta PC
#   (127.0.0.1): nadie del mismo Wi-Fi puede entrar a esta copia.
# - Si se activo el acceso desde el celular (datos\.celular_activo), levanta tambien
#   ese servidor, que escucha en la red local y siempre pide PIN.
$ErrorActionPreference = "SilentlyContinue"
$raiz    = $PSScriptRoot
$py      = Join-Path $raiz ".venv\Scripts\python.exe"
$puerto  = 8501
$celular = 8510
$url     = "http://127.0.0.1:$puerto"

function Esta-Vivo($p) {
    try { return (Invoke-WebRequest -Uri "http://127.0.0.1:$p/_stcore/health" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}

if (-not (Esta-Vivo $puerto)) {
    # Limpiar instancias trabadas de la app de escritorio (no la del celular).
    Get-CimInstance Win32_Process |
        Where-Object { $_.CommandLine -like '*streamlit*run*app.py*' -and $_.CommandLine -notlike '*--celular*' } |
        ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Start-Process -FilePath $py -WorkingDirectory $raiz -WindowStyle Hidden -ArgumentList @(
        "-m", "streamlit", "run", "src\app.py",
        "--server.port", "$puerto", "--server.address", "127.0.0.1",
        "--server.headless", "true", "--browser.gatherUsageStats", "false"
    )
    # Esperar hasta ~40 s a que levante (la primera vez carga los modelos).
    for ($i = 0; $i -lt 80; $i++) {
        Start-Sleep -Milliseconds 500
        if (Esta-Vivo $puerto) { break }
    }
}

# Acceso desde el celular, si se habilito en Ajustes -> Usar en el celular.
if ((Test-Path (Join-Path $raiz "datos\.celular_activo")) -and -not (Esta-Vivo $celular)) {
    Start-Process -FilePath $py -WorkingDirectory $raiz -WindowStyle Hidden -ArgumentList @(
        "-m", "streamlit", "run", "src\app.py",
        "--server.port", "$celular", "--server.address", "0.0.0.0",
        "--server.headless", "true", "--browser.gatherUsageStats", "false",
        "--", "--celular"
    )
}

# Ventana propia (modo aplicacion de Edge, que viene con Windows; si no, Chrome).
# Maximizada: mas espacio y los bordes de la pantalla funcionan como topes (Fitts).
$edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
          "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") |
        Where-Object { Test-Path $_ } | Select-Object -First 1
$chrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
            "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe") |
          Where-Object { Test-Path $_ } | Select-Object -First 1
$navegador = if ($edge) { $edge } elseif ($chrome) { $chrome } else { $null }
if ($navegador) {
    Start-Process -FilePath $navegador -ArgumentList @("--app=$url", "--start-maximized")
} else {
    Start-Process $url
}
