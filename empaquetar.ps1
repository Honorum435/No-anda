# Arma el instalador de la app de escritorio:   dist\Instalar Asistente Legal.exe
#
# Lleva SOLO el programa: sin .venv (se recrea al instalar), sin las causas, sin el
# indice, sin el historial, sin el PIN y sin la clave de Gemini. Asi el instalador se
# puede pasar por pendrive o por mail sin exponer nada del estudio. Los datos se copian
# aparte (ver INSTALAR.md).
#
# Al ejecutarlo en otra PC: abre una ventana grafica que busca el archivo de causas (en el
# disco externo), descomprime el programa en %USERPROFILE%\AsistenteLegal y corre
# instalar.ps1 (Python, dependencias, modelos, iconos). Si ya estaba instalado, lo
# ACTUALIZA sin tocar la carpeta datos.
#
# El .exe se compila con el compilador de C# que trae Windows (.NET Framework 4), con el
# icono de la balanza y el programa adentro (ver instalador\). No hace falta instalar nada para armarlo.
#
# Uso (en esta PC):   powershell -ExecutionPolicy Bypass -File empaquetar.ps1
$ErrorActionPreference = "Stop"
$raiz = $PSScriptRoot
$dist = Join-Path $raiz "dist"
$trab = Join-Path $env:TEMP "asistente_legal_empaque"
$prog = Join-Path $trab "programa"
$csc  = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if (-not (Test-Path $csc)) { $csc = "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe" }

Remove-Item $trab -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $prog, $dist | Out-Null

Write-Host "[1/3] Copiando el programa (sin datos del estudio)..."
$archivos = "abrir.ps1", "abrir.vbs", "Asistente Legal.bat", "Cerrar Asistente Legal.bat",
            "instalar.bat", "instalar.ps1", "Permitir celular.bat", "permitir_celular.ps1",
            "desinstalar.ps1", "correr_app.ps1", "requirements.txt", "INSTALAR.md", "README.md"
foreach ($a in $archivos) { Copy-Item -LiteralPath (Join-Path $raiz $a) -Destination $prog }
robocopy (Join-Path $raiz "src") (Join-Path $prog "src") /E /XD __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $prog ".streamlit") | Out-Null
Copy-Item (Join-Path $raiz ".streamlit\config.toml") (Join-Path $prog ".streamlit")
# Solo lo que no es del estudio: el idioma espanol del OCR y los ejemplos ficticios.
foreach ($d in "tessdata", "ejemplos") {
    robocopy (Join-Path $raiz "datos\$d") (Join-Path $prog "datos\$d") /E /NFL /NDL /NJH /NJS /NP | Out-Null
}

# Control: que no se cuele nada privado.
$privado = Get-ChildItem $prog -Recurse -Force | Where-Object {
    $_.Name -in @(".clave_gemini", ".pin_celular", ".celular_activo", ".tamano_letra") -or
    $_.FullName -match '\\datos\\(indice|indice_backup|historial|drive_casos|casos_reales)(\\|$)'
}
if ($privado) { throw "El paquete incluiria datos privados: $($privado.FullName -join ', ')" }

Write-Host "[2/3] Comprimiendo..."
$zip = Join-Path $trab "programa.zip"
tar -a -c -f $zip -C $prog .
if ($LASTEXITCODE -ne 0) { throw "No se pudo comprimir el programa." }

Write-Host "[3/3] Armando el instalador grafico (.exe con el icono de la balanza)..."
# El codigo del instalador vive en instalador\*.cs (ventana grafica con la identidad de la app).
# El compilador que trae Windows es C# 5: ver las reglas al principio de cada archivo.
$fuentes = Get-ChildItem (Join-Path $raiz "instalador") -Filter *.cs | ForEach-Object { $_.FullName }
if (-not $fuentes) { throw "No se encontro el codigo del instalador en instalador\*.cs" }
$manifiesto = Join-Path $raiz "instalador\app.manifest"
$icono = Join-Path $raiz "src\static\icono.ico"
$exeTmp = Join-Path $trab "Instalador.exe"
& $csc /nologo /codepage:65001 /target:winexe /optimize+ "/out:$exeTmp" "/win32icon:$icono" `
    "/win32manifest:$manifiesto" "/resource:$zip,programa.zip" "/resource:$icono,icono.ico" `
    /reference:System.Windows.Forms.dll /reference:System.Drawing.dll `
    /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll $fuentes
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $exeTmp)) { throw "No se pudo compilar el instalador." }

$final = Join-Path $dist "Instalar Asistente Legal.exe"
Move-Item -Force $exeTmp $final
Remove-Item $trab -Recurse -Force -ErrorAction SilentlyContinue
$mb = [math]::Round((Get-Item $final).Length / 1MB, 1)
Write-Host ""
Write-Host "  [OK] Instalador listo: $final ($mb MB)" -ForegroundColor Green
Write-Host "  Llevelo a la otra PC y haga doble clic. El archivo de causas viaja aparte (disco externo): ver INSTALAR.md."
