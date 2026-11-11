# Motor de instalacion del Asistente Legal. Se corre UNA vez en la PC donde se va a usar.
# (No correr a mano: usar "instalar.bat" o "Instalar Asistente Legal.exe".)
#
# Deja la maquina lista de cero: Python, entorno virtual, dependencias, Tesseract
# (OCR en espanol), Word, modelos de IA, el archivo de causas (si se indica), la app de
# escritorio (icono en el escritorio y en el menu Inicio) y, si se pide, el acceso desde
# el celular. Se puede correr de nuevo sin romper nada: sirve tambien para actualizar.
#
# Protocolo para el instalador grafico (lineas por la salida estandar, en UTF-8):
#   @@PASO|n|total|Titulo     empieza un paso
#   @@INFO|texto              lo que esta haciendo ahora
#   @@OK|texto                algo salio bien
#   @@AVISO|texto             algo no salio del todo bien (en lenguaje llano)
#   @@ERROR|texto             error grave
#   @@FIN|ok|<avisos>  o  @@FIN|error|<motivo>
# Cualquier otra linea es el registro tecnico.
param(
    [switch]$SinInteraccion,   # sin preguntas ni "Enter para cerrar" (lo usa el instalador grafico)
    [switch]$Celular,          # habilitar tambien el acceso desde el celular
    [string]$Datos = "",       # carpeta "datos" del archivo de causas a copiar
    [switch]$ReemplazarDatos   # pisar el archivo de causas que ya este instalado
)
$ErrorActionPreference = "Stop"
$proj = $PSScriptRoot
$TOTAL = 9
$script:avisos = 0
# UTF-8 sin BOM: el instalador grafico lee la salida en UTF-8.
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

function Marca($tipo, $texto) { [Console]::Out.WriteLine("@@" + $tipo + "|" + $texto) }
function Titulo($t) {
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Cyan
    Write-Host "   $t" -ForegroundColor Cyan
    Write-Host "=========================================" -ForegroundColor Cyan
}
function Paso($n, $t) {
    Write-Host ""
    Write-Host "[$n/$TOTAL] $t..."
    Marca "PASO" "$n|$TOTAL|$t"
}
function Info($m)  { Write-Host "  $m"; Marca "INFO" $m }
function Ok($m)    { Write-Host "  [OK] $m" -ForegroundColor Green; Marca "OK" $m }
function Aviso($m) { Write-Host "  [!]  $m" -ForegroundColor Yellow; $script:avisos++; Marca "AVISO" $m }
function Cerrar($codigo) {
    if (-not $SinInteraccion) { Read-Host "Enter para cerrar" | Out-Null }
    exit $codigo
}

if (-not $SinInteraccion) { Titulo "Instalando Asistente Legal" }

# --------------------------------------------------------------- 1) Python
Paso 1 "Python"
$py = $null
foreach ($cmd in @("python", "py")) {
    try {
        $v = & $cmd --version 2>$null
        if ($v -match "Python 3") { $py = $cmd; break }
    } catch {}
}
if (-not $py) {
    Info "No hay Python. Se intenta instalarlo (puede tardar varios minutos)."
    try {
        winget install -e --id Python.Python.3.13 --accept-source-agreements --accept-package-agreements
        # winget no refresca el PATH de esta sesion: buscar el exe donde suele quedar
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path", "User")
        foreach ($cmd in @("python", "py")) {
            try {
                $v = & $cmd --version 2>$null
                if ($v -match "Python 3") { $py = $cmd; break }
            } catch {}
        }
    } catch {
        Write-Host "  winget no pudo instalar Python."
    }
}
if (-not $py) {
    # El detalle tecnico va solo al registro; al usuario se le explica en lenguaje llano.
    Write-Host ""
    Write-Host "Detalle tecnico: no hay Python 3 y winget no pudo instalarlo. Instalarlo a mano desde python.org/downloads marcando 'Add Python to PATH'." -ForegroundColor Red
    $motivo = "No se pudo instalar un componente que el programa necesita. Revise que la computadora tenga internet y toque Volver a intentar. Si vuelve a pasar, copie el detalle y envíeselo a quien le instaló el programa."
    Marca "ERROR" $motivo
    Marca "FIN" "error|$motivo"
    Cerrar 1
}
Ok "Python: $(& $py --version)"

# ------------------------------------------------------- 2) Entorno virtual
Paso 2 "Entorno"
$vpy = "$proj\.venv\Scripts\python.exe"
if (-not (Test-Path $vpy)) { & $py -m venv "$proj\.venv" }
Ok "Entorno listo"

# --------------------------------------------------------- 3) Dependencias
Paso 3 "Dependencias"
Info "Instalando las herramientas del programa (varios minutos la primera vez)."
& $vpy -m pip install --upgrade pip --quiet
& $vpy -m pip install -r "$proj\requirements.txt"
if ($LASTEXITCODE -ne 0) { Aviso "No se pudieron instalar todas las herramientas del programa: puede que no abra." }
else { Ok "Herramientas instaladas" }

# ------------------------------------------------------ 4) Tesseract (OCR)
Paso 4 "Tesseract (OCR)"
$tessRutas = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)
$tess = $tessRutas | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $tess) {
    Info "El lector de documentos escaneados no está instalado. Se intenta instalarlo."
    try {
        winget install -e --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
        $tess = $tessRutas | Where-Object { Test-Path $_ } | Select-Object -First 1
    } catch {}
}
if ($tess) {
    Ok "Lector de documentos escaneados instalado"
    if (-not (Test-Path "$proj\datos\tessdata\spa.traineddata")) {
        Aviso "Falta el idioma español para leer documentos escaneados: esos documentos no se van a leer bien."
    }
} else {
    Aviso "No se encontró el lector de documentos escaneados: esos documentos no se van a poder leer (todo lo demás funciona igual)."
}

# ------------------------------------------------------- 5) Word (.doc viejos)
Paso 5 "Microsoft Word"
try {
    $w = New-Object -ComObject Word.Application
    Ok "Word $($w.Version)"
    $w.Quit()
} catch {
    Aviso "No se encontró Word: los documentos .doc viejos no se van a poder leer."
}

# ---------------------------------------------------------- 6) Modelos de IA
Paso 6 "Modelos de IA"
Info "Descargando la inteligencia artificial (unos 2 GB, una sola vez)."
try {
    & $vpy "$proj\src\descargar_modelos.py"
    if ($LASTEXITCODE -ne 0) { throw "descarga incompleta" }
    Ok "Inteligencia artificial descargada"
} catch {
    Aviso "No se pudo descargar la inteligencia artificial ahora; se descarga sola en la primera consulta."
}
& $vpy -c "import torch; print('  [i] Placa de video: ' + (torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no hay (el indexado va a ser lento, pero funciona)'))"

# ------------------------------------------------------ 7) Archivo de causas
Paso 7 "Archivo de causas"
$destinoDatos = "$proj\datos"
$yaHay = Test-Path "$destinoDatos\indice\fragmentos.json"
if ($Datos -and (Test-Path "$Datos\indice\fragmentos.json")) {
    $mismo = $false
    try { $mismo = ((Resolve-Path $Datos).Path.TrimEnd('\') -ieq (Resolve-Path $destinoDatos -ErrorAction SilentlyContinue).Path.TrimEnd('\')) } catch {}
    if ($mismo) {
        Ok "El archivo de causas ya está en su lugar"
    } elseif ($yaHay -and -not $ReemplazarDatos) {
        Aviso "Se conservó el archivo de causas que ya estaba instalado"
    } else {
        Info "Copiando el archivo de causas (puede tardar unos minutos)."
        New-Item -ItemType Directory -Force -Path $destinoDatos | Out-Null
        robocopy "$Datos" "$destinoDatos" /E /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -lt 8) { Ok "Archivo de causas copiado" }
        else { Aviso "No se pudo copiar todo el archivo de causas. Puede agregarlo después desde la pestaña Archivo." }
        $global:LASTEXITCODE = 0
    }
} elseif ($yaHay) {
    Ok "Se conserva el archivo de causas ya instalado"
} else {
    Ok "Sin archivo de causas: se agrega después desde la pestaña Archivo"
}

# ------------------------------------------- 8) Accesos e inscripcion en Windows
Paso 8 "Accesos e inscripción en Windows"
$stDir = "$env:USERPROFILE\.streamlit"
New-Item -ItemType Directory -Force -Path $stDir | Out-Null
Set-Content -Path "$stDir\credentials.toml" -Value "[general]`r`nemail = `"`"" -Encoding utf8
# Se abre como app de escritorio: ventana propia (sin pestanas ni barra del navegador),
# con el icono de la balanza y sin la ventana negra (abrir.vbs la esconde).
function Acceso($ruta, $destino, $argumentos, $descripcion) {
    $ws = New-Object -ComObject WScript.Shell
    $lnk = $ws.CreateShortcut($ruta)
    $lnk.TargetPath = $destino
    $lnk.Arguments = $argumentos
    $lnk.WorkingDirectory = $proj
    $lnk.IconLocation = "$proj\src\static\icono.ico,0"
    $lnk.Description = $descripcion
    $lnk.Save()
}
try {
    $wscript = "$env:WINDIR\System32\wscript.exe"
    Acceso "$([Environment]::GetFolderPath('Desktop'))\Asistente Legal.lnk" $wscript "`"$proj\abrir.vbs`"" "Abrir el Asistente Legal"
    $menu = Join-Path ([Environment]::GetFolderPath('Programs')) "Asistente Legal"
    New-Item -ItemType Directory -Force -Path $menu | Out-Null
    Acceso "$menu\Asistente Legal.lnk" $wscript "`"$proj\abrir.vbs`"" "Abrir el Asistente Legal"
    Acceso "$menu\Cerrar Asistente Legal.lnk" "$proj\Cerrar Asistente Legal.bat" "" "Cerrar el Asistente Legal"
    Acceso "$menu\Permitir el celular.lnk" "$proj\Permitir celular.bat" "" "Permitir que el celular entre (una vez)"
    Acceso "$menu\Desinstalar Asistente Legal.lnk" "powershell.exe" "-NoProfile -ExecutionPolicy Bypass -File `"$proj\desinstalar.ps1`"" "Quitar los accesos (no borra los datos)"
    Ok "Icono en el escritorio y en el menú Inicio"
} catch {
    Aviso "No se pudieron crear los iconos. Puede abrir el programa con 'Asistente Legal.bat' en la carpeta de instalación."
}
# Inscripcion en "Agregar o quitar programas" (por usuario: no pide administrador).
try {
    $clave = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistenteLegal"
    New-Item -Path $clave -Force | Out-Null
    $kb = [int](((Get-ChildItem $proj -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notlike "$proj\datos\*" } |
        Measure-Object -Property Length -Sum).Sum) / 1KB)
    $texto = @{
        DisplayName = "Asistente Legal"; DisplayIcon = "$proj\src\static\icono.ico"
        Publisher = "Asistente Legal"; InstallLocation = $proj
        DisplayVersion = (Get-Date -Format "yyyy.MM.dd")
        UninstallString = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$proj\desinstalar.ps1`""
    }
    foreach ($k in $texto.Keys) { New-ItemProperty -Path $clave -Name $k -Value $texto[$k] -PropertyType String -Force | Out-Null }
    foreach ($k in @("NoModify", "NoRepair")) { New-ItemProperty -Path $clave -Name $k -Value 1 -PropertyType DWord -Force | Out-Null }
    New-ItemProperty -Path $clave -Name "EstimatedSize" -Value $kb -PropertyType DWord -Force | Out-Null
    Ok "Registrado en Agregar o quitar programas"
} catch {
    Aviso "No se pudo registrar en Agregar o quitar programas. El programa funciona igual."
}

# ------------------------------------------------------- 9) Celular (opcional)
Paso 9 "Celular"
$quiereCelular = $Celular
if (-not $Celular -and -not $SinInteraccion) {
    Write-Host "  El asistente se puede usar tambien desde el celular, en el mismo Wi-Fi y con PIN."
    Write-Host "  Para eso Windows tiene que dejar pasar la conexion (pide permiso de administrador)."
    $resp = Read-Host "  Lo vas a usar desde el celular? (S/N)"
    $quiereCelular = ($resp -match '^[sS]')
}
if ($quiereCelular) {
    $arg = "-NoProfile -ExecutionPolicy Bypass -File `"$proj\permitir_celular.ps1`""
    if ($SinInteraccion) { $arg += " -SinInteraccion" }
    try {
        Start-Process powershell -Verb RunAs -Wait -ArgumentList $arg
        $regla = $null
        try { $regla = Get-NetFirewallRule -DisplayName "Asistente Legal (celular)" -ErrorAction SilentlyContinue } catch {}
        if ($regla) {
            Ok "Celular habilitado. En el programa: Ajustes, Usar en el celular."
            $publicas = $null
            try { $publicas = Get-NetConnectionProfile | Where-Object { $_.NetworkCategory -eq "Public" } } catch {}
            if ($publicas) {
                Aviso "Su red figura como pública en Windows: para usar el celular, cámbiela a privada en Configuración, Red e Internet."
            }
        } else {
            Aviso "No se habilitó el celular. Puede hacerlo después con 'Permitir el celular' del menú Inicio."
        }
    } catch {
        Aviso "No se dio el permiso de administrador, así que el celular no quedó habilitado. Puede hacerlo después con 'Permitir el celular' del menú Inicio."
    }
} else {
    Ok "Omitido"
}

# ------------------------------------------------------------ Verificacion
if (-not $SinInteraccion) { Titulo "Verificacion final" }
Info "Verificando que todo funcione."
& $vpy "$proj\src\verificar.py"
if ($LASTEXITCODE -ne 0) { Aviso "La comprobación final encontró problemas: toque Ver detalle para más información." }

Write-Host ""
if ($script:avisos -eq 0) {
    Write-Host "=========== LISTO ===========" -ForegroundColor Green
    Write-Host "Abra el Asistente con el icono 'Asistente Legal' del escritorio o del menu Inicio."
} else {
    Write-Host "=== INSTALADO CON AVISOS ($($script:avisos)) ===" -ForegroundColor Yellow
    Write-Host "El asistente igual se puede abrir; revise los avisos de arriba."
}
if (-not (Test-Path "$proj\datos\indice\fragmentos.json")) {
    Write-Host "Falta el archivo de causas: copie la carpeta 'datos' a $proj\datos o agregue los documentos desde la pestana Archivo." -ForegroundColor Yellow
}
Marca "FIN" "ok|$($script:avisos)"
Cerrar 0
