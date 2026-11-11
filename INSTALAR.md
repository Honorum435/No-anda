# Instalar el Asistente Legal en la PC de papá

Guía para vos (que lo instalás). Tu papá después solo usa el ícono de la balanza.

## 1. Armar el instalador (en tu PC)

```powershell
powershell -ExecutionPolicy Bypass -File empaquetar.ps1
```

Deja **`dist\Instalar Asistente Legal.exe`** (unos 8 MB; el código de la ventana está en `instalador\`). Lleva **solo el programa**:
nada de causas, índice, historial, PIN ni clave de Gemini. Se puede pasar por pendrive
o por mail sin exponer nada del estudio.

## 2. Instalar (en la PC de papá)

Doble clic en **`Instalar Asistente Legal.exe`**. Se abre una ventana con la balanza (no
hay ventana negra). Si llegó por mail o descarga, Windows puede mostrar *"Windows protegió
tu PC"* porque el instalador no está firmado: **Más información → Ejecutar de todas
formas**. Por pendrive no aparece.

1. **Bienvenida.** Dice dónde se instala, cuánto tarda (15 a 30 minutos la primera vez,
   unos 2 GB de descarga) y busca solo el **archivo de causas** en los discos conectados
   (ver abajo). Tiene una casilla para usarlo también desde el celular (pide permiso de
   administrador) y, si ya había una instalación con datos, otra para reemplazarlos
   (desmarcada: por defecto se conservan). Botón **Instalar**.
2. **Progreso.** Lista de 10 pasos con su estado, barra general y lo que está haciendo.
   **Ver detalle** muestra el registro técnico. Cerrar la ventana pide confirmación.
3. **Final.** "Asistente Legal está listo" o "Instalado con avisos" (con los avisos en
   lenguaje llano), y el botón **Abrir Asistente Legal**.

| Paso | Qué hace | Si falla |
|---|---|---|
| 1 | Copia el programa en `C:\Users\<usuario>\AsistenteLegal` | Error con el motivo |
| 2 | Busca Python; si no está, lo instala con `winget` | Error: hay que bajarlo a mano |
| 3-4 | Crea el entorno e instala las librerías | Aviso |
| 5 | Instala **Tesseract** (leer PDF escaneados) | Aviso: se pierde el OCR |
| 6 | Verifica **Word** (para los `.doc` viejos) | Aviso: se pierden los `.doc` |
| 7 | Descarga los modelos de IA (~2 GB) | Aviso: se bajan solos al usarlos |
| 8 | Copia el archivo de causas elegido | Aviso: se agrega desde la pestaña Archivo |
| 9 | Íconos de la balanza en el **escritorio** y el **menú Inicio**, y la app en **Agregar o quitar programas** | Aviso |
| 10 | (Opcional) Permiso para usarlo desde el **celular** | Aviso: se puede hacer después |

Al final corre una verificación que lista qué quedó andando y qué no.

> **Para actualizar**, armá un instalador nuevo y ejecutalo igual: la ventana dice
> "Actualizar", reemplaza el programa y **no toca la carpeta `datos`** salvo que marques
> reemplazarla.

## 3. Pasar los datos (una vez)

Los datos **nunca viajan dentro del instalador**: van en el disco externo de tu papá.

1. En tu PC, copiá la carpeta **`datos`** a su disco externo, por ejemplo a
   **`E:\AsistenteLegal\datos`** (también sirven `E:\datos` o `E:\Asistente Legal\datos`).
   Lleva:
   - **`indice\`**: el archivo ya procesado (~210 MB). Sin esto hay que procesar todo de
     nuevo y sin placa de video son **horas**.
   - **`drive_casos\`** (y `casos_reales\` si la usás): los originales, para que
     funcione "Abrir original".
   - **`.clave_gemini`**: la clave guardada, así no se la pide a tu papá.
2. En la PC de papá, con el disco conectado, abrí el instalador: en la bienvenida dice
   **"Encontramos su archivo de causas en E:\..."** con la fecha. También busca al lado
   del instalador. Si no lo encuentra, **Elegir carpeta...** (acepta la carpeta `datos` o
   la que la contiene) o seguí sin datos y agregalos después desde la pestaña Archivo.

Al abrir la app, **detecta que la carpeta cambió de lugar y corrige sola las rutas** del
índice. Los documentos que quedan en el disco externo no se tocan (si el disco cambia de
letra, se corrige en la pestaña Archivo).

## Uso diario (tu papá)

Doble clic en el ícono **Asistente Legal** (escritorio o menú Inicio). Se abre en **su
propia ventana**, como cualquier programa, sin pestañas ni barra del navegador. No hay
ventana negra. Para cerrarlo del todo: menú Inicio → *Cerrar Asistente Legal*.

## Usarlo desde el celular

1. En la PC, en la app: **Ajustes → Usar en el celular**.
2. Elegí un **PIN** de 6 a 8 números y tocá **Activar**.
3. Con la cámara del celular, **escaneá el código QR** que aparece. Pide el PIN.
4. Para tenerlo como una app más: en el menú del navegador del celular,
   **"Agregar a la pantalla de inicio"**.

Condiciones: el celular en el **mismo Wi-Fi** que la PC, y la PC prendida con el
asistente abierto. Si el celular no llega a abrirlo, ejecutá una vez **Permitir
celular.bat** (pide permiso de administrador) y fijate que Windows tenga esa red como
**Privada**.

**Seguridad.** Desde el celular:

- **Siempre pide el PIN.** Después de 5 intentos fallidos se bloquea 5 minutos.
- **No deja tocar lo delicado:** discos, clave de Gemini ni el acceso del celular.
- **"Abrir original" pasa a ser "Descargar original".**

La app de la PC escucha solo en la propia PC: nadie más del Wi-Fi puede entrar a esa
copia.

**Desde afuera de casa** (con datos móviles), lo recomendable es instalar **Tailscale**
en la PC y en el celular: arma una red privada y cifrada entre los dos, sin abrir nada a
internet. Con Tailscale conectado, se entra con la misma dirección, cambiando la IP por
la que muestra Tailscale para la PC.

## Agregar casos nuevos

En la app, pestaña **Archivo**:

1. Elegís el disco y, si querés, una subcarpeta. También se puede pegar la ruta completa
   desde el Explorador.
2. **"Buscar documentos nuevos"**: te dice cuántos son y cuánto va a tardar, antes de
   arrancar. También avisa si quedaron PDF escaneados sin leer.
3. **"Agregar al archivo ahora"**: convierte los `.doc` viejos, procesa lo nuevo y lee
   los escaneados con OCR.

Es **incremental**: solo procesa lo que todavía no está.

> **Ojo con el tiempo.** Sin placa de video va ~15 veces más lento. Para una carga
> grande conviene hacerlo en tu PC y pasarle la carpeta `datos\indice` actualizada.

## Desinstalar

**Configuración → Aplicaciones → Asistente Legal → Desinstalar** (o menú Inicio →
**Desinstalar Asistente Legal**). Quita los íconos, la entrada de *Agregar o quitar
programas* y el permiso del celular. **No borra los datos**: la carpeta `AsistenteLegal`
queda, por si la necesitás.

## Requisitos de la PC de papá

- Windows 10/11, ~8 GB de RAM, ~6 GB libres de disco, internet para instalar.
- **Word** si hay documentos `.doc` viejos.
- No necesita placa de video para *consultar*; sí se nota al *agregar documentos*.
