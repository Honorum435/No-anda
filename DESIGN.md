---
name: Asistente Legal
description: Archivo del estudio · consultas, fichas y escritos. Papel marfil, tinta, azul marino y dorado.
colors:
  navy: "#1E3A8A"
  navy-deep: "#172F72"
  navy-pressed: "#11265C"
  navy-soft: "#E9EEF9"
  navy-line: "#C9D5EE"
  gold: "#B45309"
  gold-mark: "#D08A2E"
  paper: "#FAF8F3"
  card: "#FFFFFF"
  line: "#E4DFD3"
  border-theme: "#D9D3C5"
  control: "#7D8591"
  ink: "#0F172A"
  muted: "#475569"
  pending: "#9AA3B2"
  ok: "#166534"
  bad: "#B91C1C"
typography:
  brand:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.85rem"
    fontWeight: 700
    lineHeight: 1.05
  headline:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "2.1rem"
    fontWeight: 700
  title:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.65rem"
    fontWeight: 600
  title-sm:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.35rem"
    fontWeight: 600
  body:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "17px"
    fontWeight: 400
  label:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 700
  document:
    fontFamily: "Source Serif 4, Georgia, serif"
    fontSize: "1.12rem"
    fontWeight: 400
    lineHeight: 1.65
  installer-title:
    fontFamily: "Georgia, serif"
    fontSize: "19pt"
    fontWeight: 700
  installer-brand:
    fontFamily: "Georgia, serif"
    fontSize: "20pt"
    fontWeight: 700
  installer-body:
    fontFamily: "Segoe UI, sans-serif"
    fontSize: "11pt"
    fontWeight: 400
  installer-small:
    fontFamily: "Segoe UI, sans-serif"
    fontSize: "10pt"
    fontWeight: 400
  installer-button:
    fontFamily: "Segoe UI Semibold, Segoe UI, sans-serif"
    fontSize: "11pt"
    fontWeight: 600
rounded:
  checkbox: "5px"
  button-installer: "8px"
  control: "10px"
  tile: "12px"
  brand-icon: "13px"
  card: "16px"
  chat-input: "18px"
  pill: "9999px"
spacing:
  target-min: "3rem"
  target-cta: "3.5rem"
  target-installer: "44px"
  content-max: "53rem"
  installer-gutter: "36px"
  installer-grid: "12px"
components:
  button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.card}"
    rounded: "{rounded.control}"
    padding: "0.45rem 1.1rem"
    height: "{spacing.target-min}"
  button-primary-hover:
    backgroundColor: "{colors.navy-deep}"
  button-secondary:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0.45rem 1.1rem"
    height: "{spacing.target-min}"
  button-secondary-hover:
    backgroundColor: "{colors.navy-soft}"
    textColor: "{colors.navy}"
  button-cta:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.card}"
    rounded: "{rounded.control}"
    height: "{spacing.target-cta}"
  nav-tile:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    rounded: "{rounded.tile}"
    padding: "0.5rem 0.35rem"
    height: "4.2rem"
  nav-tile-active:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.card}"
    rounded: "{rounded.tile}"
  suggestion-card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "4.4rem"
  chat-card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "0.9rem 1.1rem"
  chat-card-user:
    backgroundColor: "{colors.navy-soft}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "{spacing.target-min}"
  chat-input:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.chat-input}"
  installer-button-primary:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.card}"
    typography: "{typography.installer-button}"
    rounded: "{rounded.button-installer}"
    height: "{spacing.target-installer}"
  installer-button-primary-hover:
    backgroundColor: "{colors.navy-deep}"
  installer-button-primary-active:
    backgroundColor: "{colors.navy-pressed}"
  installer-button-secondary:
    backgroundColor: "{colors.card}"
    textColor: "{colors.navy}"
    typography: "{typography.installer-button}"
    rounded: "{rounded.button-installer}"
    height: "{spacing.target-installer}"
  installer-button-secondary-hover:
    backgroundColor: "{colors.navy-soft}"
  installer-card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
  installer-header:
    backgroundColor: "{colors.navy}"
    textColor: "{colors.card}"
    typography: "{typography.installer-brand}"
    height: "95px"
  progress-bar:
    backgroundColor: "{colors.line}"
    rounded: "{rounded.pill}"
---

# Design System: Asistente Legal

## Overview

**Creative North Star: "El expediente en papel marfil"**

El Asistente Legal se ve como un escrito bien presentado sobre el escritorio del estudio: papel marfil, tinta casi negra, el azul marino de la acción y un filete dorado que marca lo importante. Es una herramienta de trabajo para un abogado mayor que usa mouse, así que la densidad es baja, los objetivos son grandes y cada pantalla tiene una sola acción fuerte. Los titulares van en serif (el registro del escrito); el texto de trabajo, en sans legible.

El sistema vive en dos superficies del mismo mundo: la app Streamlit (Operate) y el instalador de Windows (WinForms). El instalador es una adaptación deliberada, no un mundo aparte: misma paleta, misma balanza, mismo foco dorado, pero sólo fuentes del sistema (Georgia y Segoe UI) y controles dibujados con GDI+ en vez del gris de Windows. Se rechaza la ventana de consola y el wizard gris genérico.

La marca es la balanza: en la app como trazo crema sobre una baldosa marino; en el ícono y en el instalador, la misma balanza con un punto dorado arriba. Todo el texto trata de usted.

**Key Characteristics:**
- Papel marfil de fondo, tarjetas blancas con borde cálido y sombras apenas perceptibles.
- Un solo color fuerte (marino) para la acción principal; dorado para foco, pestaña activa y filete de marca.
- Serif en títulos y documentos, sans en interfaz.
- Objetivos de 48 px o más en la app (3rem, 3.5rem en acciones principales) y 44 px en el instalador.
- Un solo momento de movimiento por superficie.
- Íconos de Material Symbols (app) o dibujados (instalador); nunca emoji.

## Colors

Paleta cálida y sobria: papel y tinta con un marino institucional y un dorado ocre usado con mesura.

### Primary
- **Marino institucional** (navy): acción principal (botón primario, baldosa activa, relleno de la barra de avance, casilla marcada), títulos de marca y de página, enlaces, cursor de texto, `theme-color` del manifiesto. Blanco encima da 10,4:1.
- **Marino profundo** (navy-deep): hover del primario en ambas superficies; también el extremo oscuro del degradé del ícono.
- **Marino presionado** (navy-pressed): sólo instalador, estado presionado del primario.
- **Marino suave** (navy-soft): hover de secundarios y baldosas, burbuja de la pregunta del usuario, selección de texto.
- **Línea marina** (navy-line): borde de la burbuja del usuario, scrollbar, subtítulo sobre la banda marino del instalador, pista del ícono "en curso".

### Secondary
- **Dorado ocre** (gold): anillo de foco del teclado, filete inferior de la cabecera (2 px app, 3 px instalador), filete interno de la baldosa activa, íconos de las tarjetas de sugerencia, estado "aviso" (también es el `orangeColor` del tema).
- **Dorado de la marca** (gold-mark): exclusivo del punto dorado de la balanza (ícono generado y encabezado del instalador). Más claro para leerse sobre marino a 16 px; no se usa en interfaz.

### Neutral
- **Papel marfil** (paper): fondo de la app y del cuerpo del instalador.
- **Blanco tarjeta** (card): tarjetas, campos, botones secundarios, mensajes de la charla.
- **Filete cálido** (line): borde de tarjetas, barra de navegación, sugerencias, separadores, pista de la barra de avance. Decorativo.
- **Borde del tema** (border-theme): `borderColor` de Streamlit para los separadores nativos.
- **Borde de control** (control): borde de campos, botones secundarios y casillas; 3,5:1 sobre papel (WCAG 1.4.11). Todo lo que se puede tocar lleva este borde, no el filete cálido.
- **Tinta** (ink): texto principal, 16,8:1 sobre papel.
- **Gris pizarra** (muted): leyendas, subtítulos, baldosas inactivas; 7,1:1 sobre papel, sin transparencia.
- **Pendiente** (pending): sólo instalador, círculo de paso pendiente y texto deshabilitado.

### Estados
- **Verde** (ok), **ámbar** (gold) y **rojo** (bad): siempre con ícono y texto; el color nunca es la única pista. Rojo también marca acciones destructivas ("Borrar", "Frenar").

### Named Rules
**La Regla de la Voz Única.** El marino es el único color fuerte de acción; en cada pantalla hay un solo botón primario. El dorado no es un segundo acento de acción: es foco, marca y aviso.

**La Regla del Borde que se Ve.** Lo interactivo lleva borde de control (#7D8591, 3,5:1); el filete cálido es sólo para contenedores y separadores.

## Typography

**Display Font (app):** Source Serif 4, embebida en Streamlit (con Georgia, serif)
**Body Font (app):** Source Sans 3, embebida en Streamlit
**Display Font (instalador):** Georgia Bold
**Body Font (instalador):** Segoe UI (Semibold en botones); Consolas 9 pt sólo en el registro técnico

**Character:** Serif de escrito jurídico para títulos y documentos, sans humanista clara para trabajar. Ninguna fuente se descarga de internet: la app usa las que trae Streamlit y el instalador sólo fuentes de Windows.

### Hierarchy
- **Marca** (700, 1.85rem, 1.05; 1.3rem en celular): "Asistente Legal" en la cabecera, marino. Bajada en sans .92rem gris pizarra.
- **Headline / Title** (h1 700 2.1rem; h2 600 1.65rem; h3 600 1.35rem; h4 600 1.18rem; h5 1.05rem; h6 1rem): serif, vía `headingFontSizes` del tema.
- **Body** (400, 17 px base): Streamlit trae 16; aquí 17 porque el usuario es mayor. El control A / A+ / A++ cambia el tamaño raíz a 106,25 % / 121,875 % / 137,5 % (17 / 19,5 / 22 px) y, como todo está en rem, crecen también botones, campos y anchos.
- **Label** (700, botones; .95rem en baldosas de navegación, .8rem en celular): sentence case, sin mayúsculas sostenidas.
- **Documento** (serif 1.12rem, 1.65): ficha y borrador se leen como un escrito.
- **Instalador:** marca Georgia Bold 20 pt blanca sobre marino; títulos de pantalla Georgia Bold 19 pt marino ("Instalar Asistente Legal", "Instalando..."); texto Segoe UI 11 pt tinta; detalle Segoe UI 10 pt gris pizarra; botones Segoe UI Semibold 11 pt.

### Named Rules
**La Regla del Escrito.** Serif para lo que el abogado leería en papel (títulos, ficha, borrador); sans para todo lo que se opera.

**La Regla de la Letra que Crece.** En la app los tamaños van en rem, nunca en px fijos, para que A+ y A++ (y la letra grande de Windows) agranden toda la interfaz sin romperla.

## Layout

- **App, columna única centrada** (`layout="centered"`, ancho máximo 53rem, en rem para que crezca con la letra). El cuadro de consulta abajo se alinea al mismo ancho. Margen inferior 7rem para que el cuadro fijo no tape contenido.
- **Orden de la pantalla:** cabecera (marca · tamaño de letra · Ajustes) con filete dorado debajo; barra de navegación de 5 baldosas iguales; contenido del modo; cuadro de consulta fijo abajo con micrófono y enviar adentro (patrón de los chats conocidos).
- **Ventana angosta de PC (≤ 900 px):** si la cabecera tiene tres columnas, la marca pasa a su propia fila (100 %) y debajo quedan el selector A / A+ / A++ (flexible) y Ajustes (ancho natural), con 1rem entre filas. Ningún botón parte su texto en dos renglones (`nowrap`).
- **Celular (≤ 640 px):** márgenes .6rem/.8rem; se oculta la bajada; ícono de marca 40 px; cabecera y navegación se mantienen en una fila (no se apilan): la marca toma 2,3 partes y Ajustes su ancho natural; baldosas de 3.6rem con etiquetas cortas; burbuja del usuario hasta 92 %; sugerencias de 3.4rem; el popover ocupa hasta 94vw. En celular el selector de letra vive dentro de Ajustes.
- **Instalador:** ventana fija de 760×520 a 100 % de DPI, todo multiplicado por la escala del sistema (`Ui.S`). Banda de 95 px (incluye el filete dorado de 3 px); márgenes laterales de 36 px y ancho útil de 688 px; ritmo de 12 / 24 px. Acciones abajo a la derecha (secundaria a la izquierda del primario); casilla de opción abajo a la izquierda; el primario responde a Enter.

## Elevation & Depth

Sistema plano con sombras ambientales mínimas y frías (tinta o marino a baja opacidad). La profundidad se marca por el contraste blanco sobre marfil y el filete cálido; las sombras sólo despegan apenas lo que flota o lo que es acción.

### Shadow Vocabulary
- **Reposo** (`box-shadow: 0 1px 2px rgba(15,23,42,.05)`; .04 en mensajes, `0 1px 3px rgba(15,23,42,.06)` en la hoja de ficha): barra de navegación, tarjetas de charla, hoja.
- **Acción** (`box-shadow: 0 2px 8px rgba(30,58,138,.22)`): botón primario y baldosa activa (.25).
- **Marca** (`box-shadow: 0 4px 12px rgba(30,58,138,.25)`): baldosa del ícono en la cabecera.
- **Flotante** (`box-shadow: 0 8px 26px rgba(15,23,42,.10)`): cuadro de consulta fijo abajo.
- **Tarjeta del instalador:** 4 capas de tinta al 3,5 % desplazadas hacia abajo hasta 6 px; borde filete cálido de 1 px.

### Named Rules
**La Regla del Papel Plano.** Ninguna sombra dura ni desplazada; si hay que separar algo, primero borde y blanco sobre marfil, después una sombra difusa.

## Shapes

Esquinas suavemente redondeadas, más generosas cuanto más grande el contenedor: 5 px casilla del instalador, 8 px botones del instalador, 10 px controles de la app y tarjetas del instalador (`baseRadius`/`buttonRadius` del tema), 12 px baldosas y expansores, 13 px baldosa del ícono, 16 px barra de navegación y mensajes, 18 px cuadro de consulta, píldora para la barra de avance. El ícono de la app es un cuadrado redondeado al 22 % con un leve degradé vertical marino → marino profundo. Bordes de 1 px (decorativos) o 1,5 px (controles).

## Components

### Buttons
- **Forma:** redondeada (10 px app, 8 px instalador).
- **Primario:** marino con texto blanco 700; mínimo 3rem; acciones principales de cada pantalla (`cta_`) 3.5rem y 1.06rem. Hover marino profundo; presionado `scale(.98)` en la app, marino presionado en el instalador.
- **Secundario:** blanco con borde de control de 1,5 px y texto tinta (app) o marino (instalador); hover fondo marino suave y borde marino.
- **Terciario / enlace:** texto marino, subrayado en hover (app); en el instalador, texto subrayado con objetivo de 44 px y foco dorado.
- **Destructivo:** texto e ícono rojo, apartado de lo frecuente; siempre con confirmación o papelera.
- **Deshabilitado (instalador):** primario marino lavado (#A8B4D2) con texto blanco; secundario #F3F1EC con texto pendiente.
- **Foco:** contorno dorado de 3 px con 2 px de separación (app); anillo dorado de 2 px a 4 px del botón (instalador).
- **Transición:** colores en `--dur-out` con `--ease-out`; nada más se anima.

### Cards / Containers
- **Tarjeta:** blanca sobre marfil, filete cálido de 1 px, sombra de reposo; 16 px en la charla, 10 px en el instalador.
- **Mensajes de la charla:** la respuesta a la izquierda con avatar de balanza; la pregunta del usuario a la derecha en marino suave con borde línea marina, ancho natural hasta 85 %.
- **Sugerencias de inicio:** botones-tarjeta blancos de 4.4rem, texto a la izquierda en 600, ícono Material en dorado 1.4rem; hover borde marino y fondo marino suave.
- **Hoja:** ficha y borrador en blanco con serif 1.12rem / 1.65, como un escrito.

### Inputs / Fields
- **Estilo:** blanco, borde de control 1,5 px, 10 px, mínimo 3rem.
- **Foco:** borde marino + halo `0 0 0 3px rgba(30,58,138,.15)` y el contorno dorado de teclado.
- **Cuadro de consulta:** blanco, 18 px, sombra flotante, texto 1.05rem, micrófono y enviar adentro (3rem).
- **Casilla (instalador):** 26 px, 5 px de radio, borde de control; marcada en marino con tilde blanca; fila mínima de 44 px; espacio o clic.

### Navigation
- **Barra de 5 baldosas iguales** (Consultar, Resumen de causa, Redactar, Historial, Archivo) en una tarjeta blanca de 16 px con 6 px de relleno. Ícono Material arriba (1.6rem), texto abajo (.95rem), gris pizarra.
- **Hover:** marino suave con texto marino.
- **Activa:** relleno marino, texto blanco y filete dorado interno de 4 px abajo (`inset 0 -4px 0` dorado): no se indica sólo con color.
- **Archivo** (mantenimiento) va último y separado por un filete vertical.

### Cabecera de marca
Baldosa marino de 50 px (40 px en celular) con la balanza en trazo crema, título serif marino y bajada "Archivo del estudio · consultas, fichas y escritos". A la derecha el selector de letra A / A+ / A++ (control segmentado, a la vista porque es lo primero que necesita un usuario mayor) y el popover **Ajustes** con texto e ícono (no un engranaje solo). Debajo, filete dorado de 2 px.

### Insignia de privacidad
Insignia verde con ícono de escudo "Protección de datos siempre activa", junto a cada acción que manda datos y debajo de cada resultado; ámbar con ícono de advertencia cuando algo requiere atención. Es un estado fijo, no un interruptor.

### Encabezado del instalador
Banda marino de 95 px con la balanza vectorial en crema y el punto dorado de marca (caja de 72×68 px a la izquierda), "Asistente Legal" en Georgia Bold 20 pt blanco, la bajada en Segoe UI 10 pt línea marina y el filete dorado de 3 px abajo.

### Pasos e íconos de estado (instalador)
Lista de 10 pasos en dos columnas dentro de una tarjeta, como un índice de fojas; el paso en curso en negrita. Íconos dibujados con GDI+ de 24 px: círculo hueco pendiente, arco marino de 120° que gira sobre pista línea marina (en curso), disco verde con tilde (listo), disco ámbar con "!" (aviso), disco rojo con "x" (error), disco marino con "i" (información). Cada uno con nombre accesible. Barra general en píldora: pista filete cálido, relleno marino que se acerca al objetivo con ease-out (20 % por cuadro de 33 ms).

### Movimiento
- **App:** un solo momento autoral. La respuesta nueva entra con opacidad 0 → 1 y sube 6 px en `--dur-in` (260 ms) con `--ease-out` (`cubic-bezier(.23, 1, .32, 1)`). Los cambios de estado usan `--dur-out` (180 ms). Con `prefers-reduced-motion: reduce` se anulan todas las transiciones y animaciones.
- **Instalador:** un solo gesto. Mientras trabaja, el brazo de la balanza (con los platillos colgando siempre derechos) oscila ±4° con período de 2,4 s; al terminar se nivela en 700 ms con ease-out cúbico. Si Windows tiene los efectos visuales desactivados (`UIEffectsEnabled`), la balanza queda quieta y nivelada. El poste, la base y el punto dorado no se mueven.

### Voz del texto
De usted, formal y claro, en castellano rioplatense sin voseo: "Escriba su consulta", "Elija una causa", "Pegue la clave de Gemini", "Puede seguir usando la computadora mientras tanto". Botones con verbo y objeto ("Abrir Asistente Legal", "Volver a intentar", "Copiar el detalle", "Seguir sin el archivo"). Sin jerga técnica en lo visible; lo técnico queda plegado ("Avanzado", "Ver detalle"). Los mensajes de error dicen qué pasó y qué hacer.

### Rasters y su procedencia
Todos los rasters que se distribuyen se generan por código; no hay imágenes dibujadas a mano ni de terceros.
- `src/static/icono-512.png`, `icono-192.png`, `icono-180.png` y `icono.ico` (16–256 px): generados por `src/generar_icono.py` (Pillow) a partir de un dibujo de 1024 px; regenerar con `python src/generar_icono.py`. El `.ico` se embebe en el instalador (`empaquetar.ps1`, recurso `icono.ico`) como ícono de ventana.
- La balanza de la cabecera de la app es el ícono Lucide "scale" como SVG embebido (trazo crema #F8FAFC de 1,7).
- La balanza del encabezado del instalador se dibuja en vectores GDI+ con la misma geometría que `generar_icono.py`; no es un raster.

## Do's and Don'ts

### Do:
- **Do** usar un solo botón primario marino por pantalla y dejar el dorado para foco, marca y aviso.
- **Do** dar a todo lo clickeable al menos 3rem en la app (3.5rem en acciones principales) y 44 px en el instalador.
- **Do** mostrar el foco del teclado con el contorno dorado (3 px a 2 px en la app; anillo de 2 px en el instalador).
- **Do** acompañar cada estado de color con ícono y texto.
- **Do** dimensionar en rem en la app para que A / A+ / A++ agranden todo.
- **Do** usar Material Symbols en la app e íconos dibujados con GDI+ en el instalador.
- **Do** escribir de usted, con verbos claros en los botones.
- **Do** generar por código todo raster nuevo y anotar su procedencia.
- **Do** desactivar el movimiento con `prefers-reduced-motion` (app) o con los efectos visuales de Windows apagados (instalador).

### Don't:
- **Don't** usar emoji como íconos.
- **Don't** agregar un segundo color de acción ni usar el dorado en botones.
- **Don't** usar el filete cálido (#E4DFD3) como borde de un control interactivo.
- **Don't** descargar fuentes de internet; en el instalador, sólo fuentes de Windows.
- **Don't** sumar movimiento decorativo más allá de la respuesta que entra (app) y la balanza que oscila (instalador).
- **Don't** usar sombras duras o desplazadas.
- **Don't** dejar fijo en la interfaz nada personal del abogado ni del estudio: la marca es "Asistente Legal" y la balanza.
- **Don't** apilar la navegación en celular: las 5 baldosas quedan en una fila.
