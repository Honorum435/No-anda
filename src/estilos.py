"""Estilos visuales del Asistente Legal: papel marfil, tinta, azul marino y dorado.

Colores y tipografias base viven en .streamlit/config.toml (tema nativo). Aca va solo
lo que el tema no cubre, pensado para un abogado mayor que usa mouse:

- Ley de Fitts: todo lo clickeable mide al menos 3rem (~51 px con la letra normal) y las
  acciones principales 3.5rem; como esta en rem, crece con el tamano de letra elegido.
- Jakob: la consulta se escribe en un cuadro abajo, con el microfono y enviar adentro,
  como en ChatGPT, Claude o Gemini.
- Von Restorff: un solo color fuerte (marino) para la accion principal; el dorado queda
  para el foco del teclado y la pestana activa.
- WCAG 2.2 AA: contrastes verificados en config.toml; bordes de controles a 3,5:1.

Uso desde app.py:
    import estilos
    estilos.aplicar_estilos(escala)
    estilos.encabezado()
"""
import streamlit as st

# Balanza (icono Lucide "scale") embebida como data-URI para que no la filtre
# el sanitizador de HTML de Streamlit. Trazo claro sobre fondo navy.
_BALANZA = (
    "data:image/svg+xml,"
    "%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'"
    "%20fill='none'%20stroke='%23F8FAFC'%20stroke-width='1.7'%20stroke-linecap='round'"
    "%20stroke-linejoin='round'%3E"
    "%3Cpath%20d='m16%2016%203-8%203%208c-.87.65-1.92%201-3%201s-2.13-.35-3-1Z'/%3E"
    "%3Cpath%20d='m2%2016%203-8%203%208c-.87.65-1.92%201-3%201s-2.13-.35-3-1Z'/%3E"
    "%3Cpath%20d='M7%2021h10'/%3E"
    "%3Cpath%20d='M12%203v18'/%3E"
    "%3Cpath%20d='M3%207h2c2%200%205-1%207-2%202%201%205%202%207%202h2'/%3E"
    "%3C/svg%3E"
)

CSS = """
<style>
:root {
  --navy: #1E3A8A;
  --navy-deep: #172F72;
  --navy-soft: #E9EEF9;
  --navy-line: #C9D5EE;
  --ink: #0F172A;
  --muted: #475569;
  --gold: #B45309;
  --paper: #FAF8F3;
  --card: #FFFFFF;
  --line: #E4DFD3;          /* separadores decorativos */
  --control: #7D8591;       /* borde de controles: 3,5:1 sobre el papel (WCAG 1.4.11) */
  --bad: #B91C1C;
  --t-min: 3rem;            /* objetivo minimo con mouse (Fitts) */
  --t-cta: 3.5rem;          /* accion principal y navegacion */
  --ease-out: cubic-bezier(.23, 1, .32, 1);
  --dur-in: 260ms;          /* entradas */
  --dur-out: 180ms;         /* salidas y cambios de estado */
}

/* ---- Superficies del navegador, con la paleta ---- */
::selection { background: var(--navy-soft); color: var(--ink); }
.stApp { caret-color: var(--navy); }
.stApp input, .stApp textarea { caret-color: var(--navy); }
* { scrollbar-color: #C9D5EE transparent; scrollbar-width: thin; }
.stApp a { text-underline-offset: 3px; }

/* ---- Base ---- */
/* Ancho en rem: crece con la letra y el cuadro de consulta queda alineado al contenido. */
.block-container, [data-testid="stBottomBlockContainer"] { max-width: 53rem; }
.block-container { padding-top: 1rem; padding-bottom: 7rem; }
/* La franja superior de Streamlit tapaba clics; el indicador "trabajando" y su boton
   para detener quedan visibles (Doherty, controlabilidad). */
[data-testid="stHeader"] { background: transparent; pointer-events: none; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stAppDeployButton"] { visibility: hidden; }
[data-testid="stStatusWidget"] { visibility: visible; pointer-events: auto; }
/* El icono de "enlace a este titulo" de Streamlit no le sirve a nadie aca. */
[data-testid="stHeaderActionElements"] { display: none; }
/* Leyendas en gris oscuro y sin transparencia: 7,1:1 (Streamlit las atenua a ~4,6:1). */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: var(--muted) !important; opacity: 1 !important;
}

/* ---- Encabezado de marca ---- */
.st-key-cabecera { border-bottom: 2px solid var(--gold); padding-bottom: .75rem; }
.al-brand { display: flex; align-items: center; gap: .85rem; }
.al-icon {
  flex: 0 0 auto; width: 50px; height: 50px; border-radius: 13px;
  background: var(--navy) url("%BALANZA%") center / 28px 28px no-repeat;
  box-shadow: 0 4px 12px rgba(30,58,138,.25);
}
.al-title {
  font-family: 'Source Serif', Georgia, serif;
  font-size: 1.85rem; font-weight: 700; color: var(--navy); line-height: 1.05;
}
.al-subtitle { font-size: .92rem; color: var(--muted); margin-top: .15rem; }

/* ---- Botones: blancos grandes (Fitts) ---- */
.stApp .stButton > button, .stApp .stDownloadButton > button,
.stApp [data-testid="stPopoverButton"] {
  min-height: var(--t-min); padding: .45rem 1.1rem; font-weight: 700;
  transition: background-color var(--dur-out) var(--ease-out), border-color var(--dur-out) var(--ease-out),
    color var(--dur-out) var(--ease-out), transform 100ms var(--ease-out);
}
.stApp .stButton > button:active, .stApp .stDownloadButton > button:active { transform: scale(.98); }
.stApp [data-testid="stBaseButton-secondary"], .stApp [data-testid="stPopoverButton"] {
  background: var(--card); border: 1.5px solid var(--control); color: var(--ink);
}
.stApp [data-testid="stBaseButton-secondary"]:hover, .stApp [data-testid="stPopoverButton"]:hover {
  background: var(--navy-soft); border-color: var(--navy); color: var(--navy);
}
.stApp [data-testid="stBaseButton-primary"] { box-shadow: 0 2px 8px rgba(30,58,138,.22); }
.stApp [data-testid="stBaseButton-primary"]:hover { background: var(--navy-deep); border-color: var(--navy-deep); }
/* El texto del boton principal siempre blanco (10,4:1). */
.stApp [data-testid="stBaseButton-primary"] p,
.stApp [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] { color: #FFFFFF; }
.stApp [data-testid="stBaseButton-tertiary"] { min-height: var(--t-min); color: var(--navy); }
.stApp [data-testid="stBaseButton-tertiary"]:hover { text-decoration: underline; }
/* Acciones principales de cada pantalla. */
[class*="st-key-cta_"] button { min-height: var(--t-cta); font-size: 1.06rem; }
/* Lo destructivo se distingue y queda lejos de lo frecuente. */
[class*="st-key-del_"] button, [class*="st-key-del_"] button p,
[class*="st-key-del_"] [data-testid="stIconMaterial"] { color: var(--bad) !important; }
.st-key-frenar button { border-color: var(--bad) !important; color: var(--bad) !important; }
.st-key-frenar button p, .st-key-frenar [data-testid="stIconMaterial"] { color: var(--bad) !important; }
/* Sugerencias de la pantalla de inicio: tarjetas grandes, texto a la izquierda. */
[class*="st-key-sug_"] button {
  min-height: 4.4rem; justify-content: flex-start; text-align: left;
  background: var(--card); border: 1.5px solid var(--line); font-weight: 600;
}
[class*="st-key-sug_"] button:hover { border-color: var(--navy); background: var(--navy-soft); }
[class*="st-key-sug_"] [data-testid="stIconMaterial"] { color: var(--gold); font-size: 1.4rem; }

/* ---- Navegacion: 5 baldosas iguales, icono arriba y texto abajo ---- */
.st-key-navbar {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  padding: 6px; box-shadow: 0 1px 2px rgba(15,23,42,.05);
}
.st-key-navbar [data-testid="stHorizontalBlock"] { gap: 6px; align-items: stretch; }
.st-key-navbar [data-testid="stColumn"] > div,
.st-key-navbar .stElementContainer, .st-key-navbar .stButton { height: 100%; }
/* Archivo es de mantenimiento: va ultimo y apartado (posicion serial). */
.st-key-navbar [data-testid="stColumn"]:has(.st-key-nav_4) { border-left: 1px solid var(--line); padding-left: 6px; }
.st-key-navbar .stButton > button {
  height: 100%; min-height: 4.2rem; padding: .5rem .35rem;
  border: 0; border-radius: 12px; background: transparent; color: var(--muted); box-shadow: none;
}
.st-key-navbar .stButton > button > div > span {
  flex-direction: column; align-items: center; gap: .15rem; text-align: center;
}
.st-key-navbar .stButton > button p { font-size: .95rem; line-height: 1.15; }
.st-key-navbar [data-testid="stIconMaterial"] { font-size: 1.6rem; }
.st-key-navbar [data-testid="stBaseButton-secondary"]:hover {
  background: var(--navy-soft); color: var(--navy); border: 0;
}
/* Activa: relleno + filete dorado, no solo color. */
.st-key-navbar .stButton > button[data-testid="stBaseButton-primary"],
.st-key-navbar .stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--navy); color: #FFFFFF;
  box-shadow: inset 0 -4px 0 var(--gold), 0 2px 8px rgba(30,58,138,.25);
}

/* ---- Campos: fondo blanco y borde visible ---- */
/* (El cuadro de consulta tiene su propio borde: no se le suma otro adentro.) */
.stTextInput [data-baseweb="input"], .stTextArea [data-baseweb="textarea"],
.stSelectbox [data-baseweb="select"] > div {
  border: 1.5px solid var(--control) !important; border-radius: 10px !important;
  background: var(--card) !important;
}
.stTextInput [data-baseweb="input"]:focus-within, .stTextArea [data-baseweb="textarea"]:focus-within,
.stSelectbox [data-baseweb="select"] > div:focus-within {
  border-color: var(--navy) !important; box-shadow: 0 0 0 3px rgba(30,58,138,.15);
}
.stSelectbox [data-baseweb="select"] > div, .stTextInput [data-baseweb="input"] { min-height: var(--t-min); }
[data-testid="stChatInput"] [data-baseweb="textarea"], [data-testid="stChatInput"] textarea {
  border: 0 !important; box-shadow: none !important; background: transparent !important;
}

/* ---- Tarjetas y paneles ---- */
[class*="st-key-panel_"], [class*="st-key-fte_"], [class*="st-key-item_"],
[data-testid="stMetric"] { background: var(--card); }
[data-testid="stExpander"] details { background: var(--card); border-radius: 12px; }
[data-testid="stExpander"] summary { min-height: var(--t-min); }
[data-baseweb="tab"] { min-height: var(--t-min); font-size: 1rem; }
[data-testid="stPopoverBody"] { min-width: 380px; }

/* Hoja: la ficha y el borrador se ven como un escrito, en serif y con aire. */
.st-key-hoja_ficha { background: var(--card); box-shadow: 0 1px 3px rgba(15,23,42,.06); }
.st-key-borrador_edit textarea {
  font-family: 'Source Serif', Georgia, serif !important;
  font-size: 1.12rem !important; line-height: 1.65 !important; padding: 1.1rem 1.3rem !important;
}

/* ---- Charla ---- */
[data-testid="stChatMessage"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  padding: .9rem 1.1rem; margin-bottom: .6rem; box-shadow: 0 1px 2px rgba(15,23,42,.04);
}
/* Lo que pregunta el usuario va a la derecha, como en todos los chats (Jakob). */
[class*="st-key-msg_u"] [data-testid="stChatMessage"] {
  background: var(--navy-soft); border-color: var(--navy-line);
  flex-direction: row-reverse; width: fit-content; max-width: 85%; margin-left: auto;
}
/* Cuadro de consulta: blanco, grande y con el microfono y enviar adentro. */
[data-testid="stChatInput"] {
  border: 1.5px solid var(--control) !important; border-radius: 18px !important;
  background: var(--card) !important; box-shadow: 0 8px 26px rgba(15,23,42,.10);
}
[data-testid="stChatInput"]:focus-within { border-color: var(--navy) !important; }
[data-testid="stChatInput"] textarea { font-size: 1.05rem !important; }
[data-testid="stChatInputSubmitButton"], [data-testid="stChatInputMicButton"] {
  min-width: 3rem; min-height: 3rem; margin-left: .35rem;
}

/* ---- Foco visible (WCAG 2.4.7): es la unica pista para quien usa el teclado ---- */
.stApp :is(button, input, textarea, select, a, summary, [role="button"], [role="tab"],
  [role="option"], [role="switch"]):focus-visible,
.stApp label:has(input:focus-visible) {
  outline: 3px solid var(--gold) !important; outline-offset: 2px !important;
}

/* Un solo momento de movimiento: la respuesta nueva entra con suavidad. */
@keyframes al-entra {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}
[class*="st-key-msg_a"] { animation: al-entra var(--dur-in) var(--ease-out) both; }

@media (prefers-reduced-motion: reduce) {
  .stApp * { transition: none !important; animation: none !important; }
}

/* ---- Celular (pantallas angostas) ----
   Streamlit apila las columnas en pantallas chicas: la barra de navegacion quedaba como
   una lista de 5 botones que ocupaba media pantalla. Se mantiene en una fila. */
@media (max-width: 640px) {
  .block-container { padding: .6rem .8rem 6rem; }
  .al-subtitle { display: none; }
  .al-icon { width: 40px; height: 40px; background-size: 22px 22px; border-radius: 11px; }
  .al-title { font-size: 1.3rem; }
  .st-key-cabecera [data-testid="stHorizontalBlock"],
  .st-key-navbar [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
  .st-key-cabecera [data-testid="stColumn"],
  .st-key-navbar [data-testid="stColumn"] { min-width: 0 !important; width: auto !important; flex: 1 1 0 !important; }
  .st-key-cabecera [data-testid="stColumn"]:first-child { flex: 2.3 1 0 !important; }
  .st-key-cabecera [data-testid="stColumn"]:last-child { flex: 0 0 auto !important; }
  .st-key-cabecera [data-testid="stPopoverButton"] { white-space: nowrap; padding: .45rem .8rem; }
  .st-key-navbar .stButton > button { min-height: 3.6rem; padding: .35rem .1rem; }
  .st-key-navbar .stButton > button p { font-size: .8rem; }
  .st-key-navbar [data-testid="stIconMaterial"] { font-size: 1.35rem; }
  [data-testid="stPopoverBody"] { min-width: 0; max-width: 94vw; }
  [class*="st-key-msg_u"] [data-testid="stChatMessage"] { max-width: 92%; }
  [data-testid="stChatMessage"] { padding: .7rem .8rem; }
  [class*="st-key-sug_"] button { min-height: 3.4rem; }
}

/* ---- Encabezado de la PC en ventanas angostas (media pantalla, letra A++) ----
   La marca va en su propia fila y debajo el tamano de letra junto a Ajustes; ningun
   boton parte su texto en dos renglones. */
.st-key-cabecera [data-testid="stPopoverButton"] { white-space: nowrap; }
.st-key-cabecera [data-baseweb="button-group"] { flex-wrap: nowrap; }
@media (max-width: 900px) {
  .st-key-cabecera [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)) {
    flex-wrap: wrap !important; row-gap: 1rem !important;
  }
  .st-key-cabecera [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3))
    > [data-testid="stColumn"]:first-child {
    flex: 1 1 100% !important; width: 100% !important; min-width: 100% !important;
  }
  .st-key-cabecera [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3))
    > [data-testid="stColumn"]:nth-child(2) {
    flex: 1 1 0 !important; width: auto !important; min-width: 0 !important;
  }
  .st-key-cabecera [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3))
    > [data-testid="stColumn"]:nth-child(3) {
    flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
  }
}
</style>
""".replace("%BALANZA%", _BALANZA)


# Tamanos de letra ofrecidos (ISO 9241-171: el texto tiene que poder agrandarse sin
# romper la interfaz). Valor = font-size raiz en % de la letra del navegador (16 px
# de fabrica): asi se respeta tambien la letra grande que la persona haya puesto en
# Windows o en el navegador, cosa que el px fijo de Streamlit ignora. Como Streamlit
# dimensiona en rem, crecen tambien botones, campos y espaciados.
ESCALAS = {"Normal": 106.25, "Grande": 121.875, "Muy grande": 137.5}   # 17 / 19,5 / 22 px
ETIQUETAS_ESCALA = {"Normal": "A", "Grande": "A+", "Muy grande": "A++"}


def aplicar_estilos(escala="Normal"):
    """Inyecta la hoja de estilos. Llamar una vez, despues de set_page_config."""
    st.markdown(CSS, unsafe_allow_html=True)
    pct = ESCALAS.get(escala, ESCALAS["Normal"])
    st.markdown(f"<style>html {{ font-size: {pct}%; }}</style>", unsafe_allow_html=True)


_META_APP = """<script>
(function () {
  var h = document.head;
  if (!h || h.querySelector('link[rel="manifest"]')) return;
  function agregar(tag, attrs) {
    var e = document.createElement(tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    h.appendChild(e);
  }
  agregar('link', {rel: 'manifest', href: 'app/static/manifest.json'});
  agregar('link', {rel: 'apple-touch-icon', href: 'app/static/icono-180.png'});
  agregar('meta', {name: 'theme-color', content: '#1E3A8A'});
  agregar('meta', {name: 'apple-mobile-web-app-title', content: 'Asistente Legal'});
  agregar('meta', {name: 'mobile-web-app-capable', content: 'yes'});
})();
</script>"""


def metadatos_app():
    """Agrega al <head> el manifiesto y el icono, para que el navegador ofrezca instalarla
    como app (en la PC) o agregarla a la pantalla de inicio (en el celular)."""
    st.html(_META_APP, unsafe_allow_javascript=True)


def encabezado(titulo="Asistente Legal",
               subtitulo="Archivo del estudio · consultas, fichas y escritos"):
    """Marca: la balanza, el titulo serif y la bajada."""
    st.markdown(
        '<div class="al-brand"><div class="al-icon"></div>'
        f'<div><div class="al-title">{titulo}</div>'
        f'<div class="al-subtitle">{subtitulo}</div></div></div>',
        unsafe_allow_html=True,
    )
