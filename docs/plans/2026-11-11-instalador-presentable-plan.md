---
date: 2026-11-11
origin: docs/brainstorms/2026-11-11-instalador-presentable-requirements.md
status: active
---

# Plan: instalador grafico y app presentable

Requisitos: `docs/brainstorms/2026-11-11-instalador-presentable-requirements.md` (R1-R15).
Producto: `PRODUCT.md` (tratamiento de USTED, sin nombre de estudio, usuario mayor).
Contrato de direccion del instalador: `.impeccable/surfaces/instalador-instalador-cs.md`.
Piso de calidad (leer antes de tocar UI): `C:\Users\Usuario\.claude\skills\impeccable\reference\craft-floor.md`.

## Reglas para quien implementa

- No toques `datos/` salvo leer `datos/ejemplos/`. No llames a Gemini. No ejecutes el
  instalador ni `instalar.ps1` en modo real: solo compilalo y usa `/capturas`.
- El compilador es `C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`: **solo C# 5**.
  Prohibido: interpolacion `$"..."`, `?.`, `?? throw`, miembros `=>`, `nameof`,
  inicializadores de auto-propiedades, `out var`, tuplas, `using static`. Si: lambdas,
  LINQ, `Task`/`async` (NET 4.5).
- Antes de cerrar cada unidad: compilar / `py_compile` y correr la verificacion indicada.
- Si te trabas (dos intentos fallidos en lo mismo, o una decision que el plan no cubre):
  NO improvises. Termina con una seccion `BLOQUEADO` (problema, que probaste, pregunta
  concreta) y espera la respuesta.

---

## U1. Quitar "Ver que se envio a Gemini" (R1)

- `src/app.py`: borrar `ver_enviado()` y `NOMBRES_TIPO`; quitar sus llamadas (charla,
  ficha, borrador) y los `st.container(horizontal=True)` que quedan con un solo hijo; quitar
  `"enviado"`, `"ocultos_por_tipo"`, `"anonimizado"` del dict que se agrega a
  `ss.mensajes`; pasar `meta` tal cual a `historial.guardar_ficha` / `guardar_borrador` (sin
  el filtro `k != "enviado"`).
- `src/preguntar.py`, `src/redactar.py`, `src/ficha.py`: sacar `"enviado"` y
  `"ocultos_por_tipo"` del meta; sacar `resumen` de los imports.
- `src/anonimizar.py`: borrar `resumen()` si queda sin uso (grep).
- `README.md`, `INSTALAR.md`, `PRODUCT.md`: quitar menciones a "Ver que se envio".
- Verificacion: `grep -rn "enviado\|ver_enviado\|ocultos_por_tipo\|resumen(" src` sin
  resultados de UI; `py_compile` de todo `src/`.

## U2. Tratamiento de usted en toda la app (PRODUCT.md)

Reescribir TODO texto visible al usuario en `src/app.py` y `src/estilos.py` (y los mensajes
que llegan a pantalla desde `src/archivo.py`, `src/celular.py`, `src/seguridad.py`) de vos a
usted, sin cambiar el sentido. Ejemplos: Escribi -> Escriba, toca -> toque, Elegi -> Elija,
Conta -> Cuente, Revisa -> Revise, Pega -> Pegue, Proba -> Pruebe, avisa -> avise, Agrega ->
Agregue, podes -> puede, queres -> quiere, tenes -> tiene, Apunta -> Apunte, escanea ->
escanee, ejecuta -> ejecute, "Corregilo aca" -> "Corrijalo aqui", "tu archivo" -> "su
archivo", "tus escritos" -> "sus escritos", "vos ves" -> "usted ve", "Vas a mandar" -> "Va a
enviar", "No cierres" -> "No cierre", "aca" -> "aqui". Incluye placeholders, toasts,
titulos de dialogos, captions, `help=` y mensajes de error. Los comentarios de codigo no.
`INSTALAR.md` queda de vos (es para el hijo).
- Verificacion: grep de formas de vos en strings de UI (`[a-z]a[sz]? |s\b` no sirve; revisar
  a mano: "á " al final de imperativos, "podés", "querés", "tenés", "tu ", "tus ", "vos").

## U3. Pulido visual de la app (R2, craft-floor)

Refinamiento, no rediseno: se conserva todo `src/estilos.py` y `.streamlit/config.toml`.
- Superficies del navegador tematizadas en `CSS`: `::selection` (fondo `--navy-soft`, texto
  `--ink`), `caret-color: var(--navy)`, barras de desplazamiento finas
  (`scrollbar-color: #C9D5EE transparent; scrollbar-width: thin`), `text-underline-offset:
  3px` en enlaces.
- Movimiento: tokens `--ease-out: cubic-bezier(.23,1,.32,1)` y duraciones 260 ms
  (entrada) / 180 ms (salida). Un solo momento autoral: la tarjeta de una respuesta nueva
  (`[class*="st-key-msg_a"]`) entra con opacidad 0->1 y `translateY(6px)->0`, 260 ms. Botones:
  `:active { transform: scale(.98) }` 100 ms. Todo dentro del `@media (prefers-reduced-motion:
  reduce)` existente queda anulado.
- Sin emojis en la UI (grep de emojis en `src/app.py`); sin etiquetas encima de titulos.
- Verificacion: AppTest de las 5 pantallas sin excepciones.

## U4. Motor de instalacion con protocolo de progreso (R4-R13)

`instalar.ps1`:
- `param([switch]$SinInteraccion, [switch]$Celular, [string]$Datos = "", [switch]$ReemplazarDatos)`.
- Al inicio: `[Console]::OutputEncoding = [Text.Encoding]::UTF8`.
- Funcion `Marca($tipo, $texto)` que escribe con `[Console]::Out.WriteLine("@@" + ...)` lineas:
  `@@PASO|n|total|Titulo`, `@@OK|texto`, `@@AVISO|texto`, `@@ERROR|texto`,
  `@@FIN|ok|<cantidad de avisos>` o `@@FIN|error|<motivo>`. Mantener los `Write-Host` para
  el uso por consola. Los avisos en lenguaje llano y de usted ("No se encontro Word: los .doc
  viejos no se van a poder leer").
- Pasos (total 9): 1 Python, 2 Entorno, 3 Dependencias, 4 Tesseract (OCR), 5 Word, 6 Modelos de
  IA, 7 Archivo de causas, 8 Accesos e inscripcion en Windows, 9 Celular. Luego la
  verificacion (`src\verificar.py`) sin numero de paso.
- Con `-SinInteraccion`: ningun `Read-Host` (ni el de "Enter para cerrar" ni el del
  celular); si falta Python y winget falla: `@@FIN|error|...`.
- Paso 7: si `$Datos` viene y existe `$Datos\indice\fragmentos.json`: si ya existe
  `$proj\datos\indice\fragmentos.json` y no viene `-ReemplazarDatos`, `@@AVISO|Se conservo el
  archivo de causas que ya estaba instalado`; si no, `robocopy "$Datos" "$proj\datos" /E
  /NFL /NDL /NJH /NJS /NP` (codigos < 8 = ok). Sin `$Datos`: `@@OK|Sin archivo de causas:
  se agrega despues desde la pestana Archivo`.
- Paso 8: los accesos actuales + clave HKCU
  `Software\Microsoft\Windows\CurrentVersion\Uninstall\AsistenteLegal` con DisplayName
  "Asistente Legal", DisplayIcon `$proj\src\static\icono.ico`, Publisher "Asistente Legal",
  InstallLocation, DisplayVersion `(Get-Date -Format "yyyy.MM.dd")`, NoModify=1, NoRepair=1,
  EstimatedSize (KB de la carpeta sin datos), UninstallString `powershell.exe -NoProfile
  -ExecutionPolicy Bypass -File "$proj\desinstalar.ps1"`.
- Paso 9: solo con `-Celular` (pide administrador como hoy; si se rechaza, `@@AVISO`); sin
  `-Celular`, `@@OK|Omitido`.
- `desinstalar.ps1`: borrar tambien esa clave de registro.
- Verificacion: parsear con `[System.Management.Automation.Language.Parser]::ParseFile` sin
  errores. NO ejecutar.

## U5. Instalador grafico (R3-R15) en `instalador/`

Archivos: `instalador/Instalador.cs` (puede partirse en `Programa.cs`, `Ventana.cs`,
`Controles.cs`), `instalador/app.manifest` (asInvoker + dpiAware true). WinForms,
`/target:winexe`.

**Ventana:** 760x520 logicos, borde fijo, sin maximizar, centrada, `AutoScaleMode.Dpi`
(96). Icono desde recurso `icono.ico`. Fuente base Segoe UI 11 pt; titulos Georgia Bold
(serif del sistema, igual que el fallback de la app).

**Encabezado (signature move):** banda #1E3A8A de 92 px con la balanza dibujada con GDI+
(antialias, trazo crema #FAF8F3, punto dorado #D08A2E arriba, como `src/generar_icono.py`),
"Asistente Legal" en Georgia Bold 20 pt blanco y subtitulo Segoe UI 10 pt #C9D5EE; filete
dorado #B45309 de 3 px abajo. Mientras instala, el brazo de la balanza oscila +-4 grados
(seno, periodo 2,4 s, Timer 30 fps); al terminar se nivela con ease-out en 700 ms. Si
`SystemInformation.UIEffectsEnabled` es false, queda quieta.

**Controles propios (sin estilo gris de Windows):** `BotonPrimario` (fondo #1E3A8A, hover
#172F72, texto blanco Segoe UI Semibold 11 pt, alto 44, radio 8, foco: anillo dorado 2 px),
`BotonSecundario` (blanco, borde #7D8591, texto #1E3A8A), `Tarjeta` (blanca, borde #E4DFD3
1 px, radio 10, sombra suave con desplazamiento). Iconos de estado dibujados (pendiente:
circulo hueco #9AA3B2; en curso: arco marino girando; listo: circulo verde #166534 con
tilde blanca; aviso: circulo #B45309 con "!" dibujado; error: #B91C1C). Nada de emojis ni
glifos Unicode como iconos. Cursor mano en lo clickeable. `AccessibleName` en todo.

**Pantalla 1, Bienvenida:** titulo "Instalar Asistente Legal" (o "Actualizar Asistente
Legal" si existe `%USERPROFILE%\AsistenteLegal\src\app.py`); texto: "Se instalara en
C:\Users\...\AsistenteLegal. La primera vez tarda entre 15 y 30 minutos y descarga unos 2 GB:
necesita conexion a internet." Tarjeta "Su archivo de causas":
- Busqueda (en segundo plano al abrir): `<carpeta del exe>\datos`,
  `<carpeta del exe>\AsistenteLegal\datos`, y en cada `DriveInfo` listo:
  `<raiz>\AsistenteLegal\datos`, `<raiz>\Asistente Legal\datos`, `<raiz>\datos`. Valida si
  tiene `indice\fragmentos.json`. Excluir la carpeta de destino.
- Encontrado: tilde verde + "Encontramos su archivo de causas en E:\AsistenteLegal\datos" +
  "Actualizado el 19/08/2026" (fecha de `fragmentos.json`); si hay mas de uno, combo para
  elegir (por defecto el mas reciente). Boton secundario "Elegir otra carpeta...".
- No encontrado: icono informativo + "No encontramos un archivo de causas en los discos
  conectados." + "Elegir carpeta..." + "Puede continuar sin el archivo y agregarlo despues
  desde la pestana Archivo."
- `FolderBrowserDialog` acepta la carpeta `datos` o la que la contiene; si no es valida:
  "Esa carpeta no tiene un archivo de causas del Asistente Legal."
- Si la instalacion existente ya tiene `datos\indice\fragmentos.json`: casilla "Reemplazar
  el archivo de causas que ya esta instalado" (desmarcada).
Casilla "Usarlo tambien desde el celular (Windows le va a pedir permiso de
administrador)". Botones abajo a la derecha: "Cancelar" (secundario, CancelButton) e
"Instalar" (primario, AcceptButton).

**Pantalla 2, Progreso:** titulo "Instalando..."; "Paso 3 de 10"; lista de 10 pasos (0
"Copiar el programa" + los 9 del motor) con icono de estado, el actual en negrita; barra
general dibujada (pista #E4DFD3, relleno marino, alto 10, redondeada, avance animado con
ease-out 300 ms); linea de actividad actual; enlace "Ver detalle" que despliega un registro
(Consolas 9 pt, solo lectura). Nota: "Puede seguir usando la computadora mientras tanto."
Paso 0 en hilo aparte: extraer el recurso `programa.zip` a `%USERPROFILE%\AsistenteLegal`
(con la proteccion zip-slip actual). Luego `powershell.exe -NoProfile -ExecutionPolicy
Bypass -File instalar.ps1 -SinInteraccion [-Celular] [-Datos "..."] [-ReemplazarDatos]`
con stdout/stderr redirigidos en UTF-8, sin ventana; parsear `@@` y mandar lo demas al
registro. Cerrar la ventana durante la instalacion pide confirmacion.

**Pantalla 3, Final:** icono grande (verde o ambar), titulo "Asistente Legal esta listo"
o "Instalado con avisos"; lista de avisos en lenguaje llano; si no hubo archivo de causas,
recordatorio. Botones: "Cerrar" (secundario) y "Abrir Asistente Legal" (primario, ejecuta
`wscript.exe "<destino>\abrir.vbs"`). Error fatal: "No se pudo completar la instalacion",
motivo, "Ver detalle", "Cerrar".

**Modo `/capturas <carpeta>`:** sin instalar nada, renderiza con `DrawToBitmap` y guarda PNG:
`1-bienvenida-encontrado.png`, `2-bienvenida-sin-datos.png`, `3-progreso.png` (paso 4 en
curso, un aviso, 45 %), `4-final-ok.png`, `5-final-avisos.png`, `6-error.png`; luego sale.
Datos de ejemplo ficticios (rutas `E:\AsistenteLegal\datos`).

**Texto:** de usted, sin jerga ("archivo de causas", no "indice"); los botones nombran su
accion.

## U6. `empaquetar.ps1` y documentacion

- Compilar `instalador\*.cs` con `/target:winexe /optimize+ /win32icon:src\static\icono.ico
  /win32manifest:instalador\app.manifest /resource:<zip>,programa.zip
  /resource:src\static\icono.ico,icono.ico` y referencias `System.Windows.Forms.dll`,
  `System.Drawing.dll`, `System.IO.Compression.dll`, `System.IO.Compression.FileSystem.dll`.
  Borrar el C# embebido en el here-string.
- Mantener el control de datos privados.
- `INSTALAR.md` (de vos, para el hijo): instalador grafico, datos en el disco externo
  (copiar la carpeta `datos` a `E:\AsistenteLegal\datos`), "Agregar o quitar programas",
  sin "Ver que se envio".
- Verificacion: `powershell -File empaquetar.ps1` genera `dist\Instalar Asistente Legal.exe`;
  `"dist\Instalar Asistente Legal.exe" /capturas <scratch>` genera las 6 PNG.

## Entrega del agente

Archivos tocados, verificaciones corridas con su salida resumida, rutas de las capturas, y
cualquier desvio del plan con su motivo.
