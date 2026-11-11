r"""Interfaz web del Asistente Legal: consultar el archivo, resumir causas y redactar escritos.

Correr con:  .\correr_app.ps1     (o)    streamlit run src/app.py
Modo celular (red local, con PIN):  streamlit run src/app.py -- --celular   (ver celular.py)

Criterios de diseno (detalle en estilos.py): ley de Fitts (objetivos grandes y pegados
a lo que los motiva), leyes de UX (Jakob, Hick, Doherty, pico-final, Zeigarnik) y
WCAG 2.2 AA. La privacidad se ve siempre: nada sale a la nube sin decirlo.
"""
import os
import re
import sys
import time
import unicodedata
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from pathlib import Path
import estilos
import causas
import historial
import archivo
from comun import MODELO_GEMINI
from preguntar import generar_respuesta

# Archivos locales (gitignored) para recordar la clave de Gemini y el tamano de letra.
ARCHIVO_CLAVE = Path(__file__).resolve().parent.parent / "datos" / ".clave_gemini"
ARCHIVO_LETRA = Path(__file__).resolve().parent.parent / "datos" / ".tamano_letra"
ICONO = Path(__file__).resolve().parent / "static" / "icono-192.png"

TODOS_LOS_MODOS = {
    "Consultar": ":material/forum:",
    "Resumen de causa": ":material/summarize:",
    "Redactar": ":material/edit_document:",
    "Historial": ":material/history:",
    "Archivo": ":material/inventory_2:",
}
# En el celular no se ofrece Archivo (discos de la PC) y las etiquetas van cortas.
ETIQUETAS_CORTAS = {"Resumen de causa": "Resumen"}
AVATARES = {"user": ":material/person:", "assistant": ":material/balance:"}

# Se decide en cada corrida (ver el final): True si esta es la copia para el celular o si
# la conexion no viene de esta misma PC. En ese caso se pide PIN y se ocultan el
# manejo de discos, la clave y el acceso desde el celular.
REMOTO = False
MODOS = dict(TODOS_LOS_MODOS)

# Ejemplos para no arrancar con la pantalla en blanco (Hick: tres, no mas).
SUGERENCIAS = [
    (":material/gavel:", "¿Dónde planteé una nulidad de allanamiento?"),
    (":material/lock_open:", "Modelos de pedido de excarcelación"),
    (":material/balance:", "¿Qué argumenté sobre la prisión preventiva?"),
]

TIPOS_ESCRITO = [
    "Pedido de excarcelación", "Pedido de eximición de prisión",
    "Pedido de arresto domiciliario", "Planteo de nulidad", "Recurso de apelación",
    "Recurso de casación", "Pedido de sobreseimiento",
]

# Streamlit descarta el estado de los campos que no se dibujan, asi que lo escrito se
# perdia al cambiar de pestana. Reasignarlos al empezar cada corrida los conserva.
# Los ajustes van tambien: en el celular aparecen recien despues del PIN y, sin esto,
# se veian con un valor distinto del que tenian.
CAMPOS_QUE_PERSISTEN = ("red_tipo", "red_desc", "borrador_edit", "causa_sel",
                        "rerank", "k_fuentes", "escala")

MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
SIN_CLAVE = "Falta la clave de Gemini: se carga en **Ajustes** (arriba a la derecha)."


# ------------------------------ preferencias en disco ------------------------------

def leer_escala():
    """Tamano de letra elegido. Se guarda en disco: si alguien necesita letra grande,
    la necesita siempre."""
    try:
        v = ARCHIVO_LETRA.read_text(encoding="utf-8").strip()
        return v if v in estilos.ESCALAS else "Normal"
    except Exception:
        return "Normal"


def guardar_escala(v):
    try:
        ARCHIVO_LETRA.write_text(v, encoding="utf-8")
    except Exception:
        pass


def leer_clave_guardada():
    try:
        return ARCHIVO_CLAVE.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def guardar_clave(clave):
    try:
        ARCHIVO_CLAVE.parent.mkdir(parents=True, exist_ok=True)
        ARCHIVO_CLAVE.write_text(clave.strip(), encoding="utf-8")
    except Exception:
        pass


def borrar_clave():
    try:
        ARCHIVO_CLAVE.unlink()
    except Exception:
        pass


# ------------------------------------ utilidades ------------------------------------

_MD_ESPECIALES = re.compile(r"([\\`*_\[\]<>#|~$:])")
_CITA = re.compile(r"\[Fuente (\d+)\]")
_EXTRACTO = re.compile(r"\[Extracto (\d+)\]")


def md(texto):
    """Escapa nombres de archivo y titulos para que no se interpreten como markdown."""
    return _MD_ESPECIALES.sub(r"\\\1", str(texto or ""))


def con_citas(texto):
    """Las citas [Fuente N] se ven como insignias numeradas, igual que las tarjetas."""
    return _CITA.sub(r":blue-badge[Fuente \1]", texto or "")


def ficha_con_citas(texto):
    return _EXTRACTO.sub(r":blue-badge[Extracto \1]", texto or "")


def ficha_para_exportar(texto, extractos):
    """En el Word/PDF, '[Extracto 3]' no le dice nada al lector: se reemplaza por el
    nombre del documento del que sale."""
    def nombre(m):
        i = int(m.group(1)) - 1
        if extractos and 0 <= i < len(extractos):
            return f"({extractos[i].get('nombre')})"
        return m.group(0)
    return _EXTRACTO.sub(nombre, texto or "")


def fuentes_de_ficha(texto, extractos):
    """Los extractos citados en la ficha, con su numero, para mostrarlos como tarjetas."""
    citados = sorted({int(n) for n in _EXTRACTO.findall(texto or "")})
    fuentes, numeros = [], []
    for n in citados:
        if extractos and 0 < n <= len(extractos):
            fuentes.append(extractos[n - 1])
            numeros.append(n)
    return fuentes, numeros


def miles(n):
    return f"{n:,}".replace(",", ".")


def duracion(minutos):
    minutos = max(1, round(minutos))
    if minutos < 60:
        return f"≈ {minutos} min"
    h, m = divmod(minutos, 60)
    return f"≈ {h} h {m} min" if m else f"≈ {h} h"


def fecha_legible(iso):
    try:
        d = datetime.fromisoformat(iso)
    except Exception:
        return str(iso or "")
    hoy = datetime.now().date()
    if d.date() == hoy:
        return f"Hoy, {d:%H:%M}"
    if (hoy - d.date()).days == 1:
        return f"Ayer, {d:%H:%M}"
    return f"{d:%d/%m/%Y, %H:%M}"


def nombre_archivo(texto):
    s = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return s[:40] or "documento"


def normalizar_letra(texto):
    """'e', 'E', 'e:\\' -> 'E:' (Postel: aceptar lo que escriba el usuario)."""
    m = re.match(r"^\s*([A-Za-z])", texto or "")
    return f"{m.group(1).upper()}:" if m else ""


def armar_carpeta(letra, sub):
    """Si pegaron la ruta completa desde el Explorador (E:\\Casos), se usa tal cual;
    antes quedaba E:\\E:\\Casos y el error culpaba al disco."""
    s = (sub or "").strip().strip('"')
    if re.match(r"^[A-Za-z]:[\\/]", s):
        return s[0].upper() + s[1:]
    return f"{letra}:\\" + s.lstrip("\\/")


def mensaje_error(e, accion):
    """Mensaje para el usuario, en castellano llano y con que hacer."""
    from nube import es_transitorio
    t = str(e).lower()
    if es_transitorio(e):
        return (f"Gemini está saturado y no pudo {accion}. Ya reintenté y probé los modelos "
                "de respaldo. Es temporal: pruebe de nuevo en un par de minutos. La búsqueda "
                "en el archivo sigue funcionando.")
    if any(p in t for p in ("api_key", "api key", "permission_denied", "unauthenticated")):
        return (f"No se pudo {accion}: Google rechazó la clave de Gemini. Revísela en "
                "**Ajustes** (arriba a la derecha).")
    if any(p in t for p in ("connect", "getaddrinfo", "network", "timed out", "resolution")):
        return (f"No se pudo {accion}: no hay conexión a internet. La búsqueda en el "
                "archivo funciona igual, porque es local.")
    return f"No se pudo {accion}. Pruebe de nuevo; si se repite, avise (detalle: {type(e).__name__})."


def aviso_modelo(meta):
    """Si respondio un modelo de respaldo, decirlo (el principal estaba saturado)."""
    usado = (meta or {}).get("modelo")
    if usado and usado != MODELO_GEMINI:
        st.caption(f":material/swap_horiz: Respondió el modelo de respaldo `{usado}` "
                   f"porque `{MODELO_GEMINI}` estaba saturado.")


def nota_privacidad(meta):
    """Texto de la insignia de privacidad que acompana cada resultado."""
    if not meta or not meta.get("anonimizado") or not meta.get("modelo"):
        return ""
    return f"Se ocultaron {meta.get('ocultos', 0)} dato(s) personal(es) antes de enviar a Gemini"


def mostrar_nota(nota):
    limpio = (nota or "").replace("🛡️", "").strip().rstrip(".")
    if not limpio:
        return
    if limpio.startswith("Protección desactivada"):
        st.markdown(f":orange-badge[:material/warning: {limpio}]")
    else:
        st.markdown(f":green-badge[:material/shield: {limpio}]")


def franja_privacidad():
    """Estado de privacidad a la vista, junto a la accion que manda datos (Von Restorff).
    La proteccion es obligatoria: no hay forma de desactivarla."""
    st.caption(":green-badge[:material/shield: Protección de datos siempre activa]  "
               "Usted ve los nombres reales; a Google le llegan ocultos (nombres, DNI, "
               "domicilios). Su archivo queda en esta PC.")


def pasos_en(paso):
    """Devuelve un 'log' que muestra cada paso dentro del st.status (Doherty)."""
    def avisar(m):
        paso.update(label=str(m))
        st.write(f"· {m}")
    return avisar


# ------------------------------- acciones (callbacks) -------------------------------

def ir_a(modo):
    st.session_state.modo = modo
    st.query_params["modo"] = modo


def al_cambiar_escala():
    guardar_escala(st.session_state.escala)


def nueva_consulta():
    st.session_state.mensajes, st.session_state.conv_id = [], None


def usar_sugerencia(texto):
    st.session_state.consulta_pendiente = texto


def retomar(id_conv):
    ss = st.session_state
    ss.mensajes = historial.cargar_conversacion(id_conv)
    ss.conv_id = id_conv
    ir_a("Consultar")


def reintentar():
    """Vuelve a responder la ultima pregunta (tras un error o si quedo sin respuesta)."""
    ss = st.session_state
    if ss.mensajes and ss.mensajes[-1].get("error"):
        ss.mensajes.pop()
    if ss.mensajes and ss.mensajes[-1].get("rol") == "user":
        ss.por_responder = True


def abrir(ruta):
    try:
        os.startfile(ruta)  # se abre en la PC donde corre la app (la del usuario)
        st.toast("Abriendo el documento…", icon=":material/open_in_new:")
    except Exception as e:
        st.toast(f"No se pudo abrir el archivo ({type(e).__name__}).", icon=":material/error:")


def abrir_descargas():
    try:
        os.startfile(Path.home() / "Downloads")
    except Exception:
        st.toast("No encontré la carpeta Descargas.", icon=":material/error:")


def avisar_descarga(formato):
    st.toast(f"Listo: el {formato} quedó en la carpeta Descargas.", icon=":material/download_done:")


# ------------------------------------- dialogos -------------------------------------

@st.dialog("¿Olvidar la clave de Gemini?")
def confirmar_olvidar_clave():
    st.markdown("Se borra la clave guardada en esta PC. Para volver a tener respuestas "
                "redactadas va a tener que pegarla de nuevo en Ajustes.")
    cancelar, olvidar = st.columns(2)
    if cancelar.button("Cancelar", type="primary", width="stretch", key="clave_cancelar"):
        st.rerun()
    if olvidar.button("Olvidar la clave", icon=":material/key_off:", width="stretch",
                      key="del_clave"):
        borrar_clave()
        st.rerun()


@st.dialog("¿Mandar a la papelera?")
def confirmar_borrado(etiqueta, tipo, id_item):
    st.markdown(f"Va a enviar **{md(etiqueta)}** a la papelera. Lo puede recuperar "
                "después desde **Historial → Papelera**.")
    dejar, borrar = st.columns(2)
    if dejar.button("No, dejarlo", type="primary", width="stretch", key="borrar_no"):
        st.rerun()
    if borrar.button("Sí, a la papelera", icon=":material/delete:", width="stretch",
                     key="del_confirmar"):
        historial.borrar(tipo, id_item)
        ss = st.session_state
        if tipo == "conversacion" and ss.get("conv_id") == id_item:
            ss.mensajes, ss.conv_id = [], None
        ss.ultimo_borrado = (tipo, id_item, etiqueta)
        st.rerun()


@st.dialog("¿Vaciar la papelera?")
def confirmar_vaciado(n):
    st.markdown(f"Se van a borrar **para siempre** {n} elemento(s). Esto no se puede deshacer.")
    cancelar, vaciar = st.columns(2)
    if cancelar.button("Cancelar", type="primary", width="stretch", key="vaciar_no"):
        st.rerun()
    if vaciar.button("Vaciar del todo", icon=":material/delete_forever:", width="stretch",
                     key="del_vaciar"):
        historial.vaciar_papelera()
        st.session_state.pop("ultimo_borrado", None)
        st.rerun()


def boton_borrar(etiqueta, tipo, id_item):
    """Borrar va a la derecha, en rojo y sin relleno: lejos y distinto de lo frecuente."""
    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Borrar", icon=":material/delete:", type="tertiary",
                     key=f"del_{tipo}_{id_item}"):
            confirmar_borrado(etiqueta, tipo, id_item)


# --------------------------------- piezas comunes ---------------------------------

def abrir_original(ruta, clave):
    """Abre el documento original en su programa. Si no esta en esta PC, lo dice en vez
    de esconder el boton. Desde el celular, en vez de abrirlo en la PC, se descarga."""
    existe = bool(ruta) and os.path.exists(ruta)
    if REMOTO and existe:
        from extraer_texto import ruta_larga
        st.download_button("Descargar original", data=lambda r=ruta: Path(ruta_larga(r)).read_bytes(),
                           file_name=Path(ruta).name, icon=":material/download:", key=clave,
                           width="stretch", on_click="ignore")
    elif existe and hasattr(os, "startfile"):
        st.button("Abrir original", icon=":material/open_in_new:", key=clave,
                  width="stretch", on_click=abrir, args=(ruta,))
    else:
        st.button("No está en esta PC", icon=":material/link_off:", key=clave,
                  width="stretch", disabled=True)


def tarjeta_fuente(n, f, prefijo, rotulo="Fuente"):
    """Una fuente: numero (igual que la cita en el texto), documento, causa, pasaje y el
    boton para abrir el original al lado (Fitts, proximidad)."""
    caso = causas.caso_de_ruta(f.get("ruta"))
    extracto = " ".join((f.get("texto") or "").split())
    if len(extracto) > 230:
        extracto = extracto[:230].rsplit(" ", 1)[0].rstrip(".,;:") + "…"
    with st.container(border=True, key=f"fte_{prefijo}_{n}"):
        texto, accion = st.columns([4, 1.45], vertical_alignment="center")
        with texto:
            st.markdown(f":blue-badge[{rotulo} {n}] **{md(f.get('nombre'))}**")
            detalle = f":material/folder: {md(caso)}"
            if extracto:
                detalle += f"  ·  “{md(extracto)}”"
            st.caption(detalle)
        with accion:
            abrir_original(f.get("ruta"), f"abrir_{prefijo}_{n}")


def mostrar_fuentes(fragmentos, prefijo, abiertas=3, titulo="Fuentes citadas",
                    rotulo="Fuente", numeros=None):
    """Tarjetas numeradas igual que las citas del texto. Las primeras a la vista; el
    resto, plegado para no alargar la charla (Miller)."""
    if not fragmentos:
        return
    numeros = numeros or list(range(1, len(fragmentos) + 1))
    pares = list(zip(numeros, fragmentos))
    visibles, resto = pares[:abiertas], pares[abiertas:]
    if visibles:
        st.markdown(f"**{titulo}**")
        for n, f in visibles:
            tarjeta_fuente(n, f, prefijo, rotulo)
    if resto:
        if not visibles:
            etiqueta = f"{titulo} ({len(resto)})"
        elif len(resto) == 1:
            etiqueta = f"Ver 1 {rotulo.lower()} más"
        else:
            etiqueta = f"Ver {len(resto)} más"
        with st.expander(etiqueta, icon=":material/menu_book:"):
            for n, f in resto:
                tarjeta_fuente(n, f, prefijo, rotulo)


def barra_descargas(texto, base, clave, titulo=None):
    """Word (principal) y PDF juntos; al lado, abrir la carpeta donde quedan."""
    from exportar import texto_a_docx, texto_a_pdf
    fecha = datetime.now().strftime("%Y-%m-%d")
    with st.container(horizontal=True, vertical_alignment="center", key=f"descargas_{clave}"):
        st.download_button("Descargar Word", data=lambda: texto_a_docx(texto),
                           file_name=f"{base}_{fecha}.docx", mime=MIME_DOCX, type="primary",
                           icon=":material/download:", key=f"cta_word_{clave}",
                           on_click=avisar_descarga, args=("Word",))
        st.download_button("PDF", data=lambda: texto_a_pdf(texto, titulo=titulo),
                           file_name=f"{base}_{fecha}.pdf", mime="application/pdf",
                           icon=":material/picture_as_pdf:", key=f"pdf_{clave}",
                           on_click=avisar_descarga, args=("PDF",))
        if hasattr(os, "startfile") and not REMOTO:
            st.button("Abrir Descargas", icon=":material/folder_open:", type="tertiary",
                      key=f"carpeta_{clave}", on_click=abrir_descargas)


@st.cache_data(ttl=120, show_spinner=False)
def resumen_indice():
    return archivo.resumen_indice()


@st.cache_data(ttl=30, show_spinner=False)
def discos():
    return archivo.discos()


@st.cache_resource
def candado_indexado():
    """Uno solo a la vez, aunque haya dos pestanas abiertas."""
    return {"activo": False}


# ------------------------------------ Consultar ------------------------------------

def cuadro_consulta():
    """El cuadro de consulta. En la PC trae microfono (dictado local). En el celular no:
    el navegador solo deja grabar en conexiones seguras, y el teclado del telefono ya
    tiene su propio microfono."""
    if REMOTO:
        return st.chat_input("Escriba su consulta (puede dictar con el micrófono del teclado)…",
                             key="entrada")
    return st.chat_input("Escriba su consulta, o toque el micrófono para dictarla…",
                         key="entrada", accept_audio=True)


def bienvenida():
    """Pantalla vacia al estilo de ChatGPT, Claude o Gemini (Jakob): saludo, el cuadro de
    consulta en el medio y los ejemplos justo debajo (Fitts: todo junto). Devuelve lo que
    se haya escrito o dictado en el cuadro."""
    n_docs = resumen_indice()[0]
    n_causas = len(causas.listar_casos())
    with st.container(key="bienvenida"):
        st.markdown("### ¿Qué desea buscar en su archivo?")
        st.caption(f"Pregunte con sus palabras. La respuesta cita de qué escrito sale cada "
                   f"cosa. Se busca en {miles(n_docs)} documentos de {n_causas} causas.")
        # Dentro de un contenedor el cuadro va en linea (no fijo abajo): asi la pantalla
        # no se desplaza sola y el encabezado queda a la vista aun con letra grande.
        entrada = cuadro_consulta()
        franja_privacidad()
        for i, (col, (icono, texto)) in enumerate(zip(st.columns(len(SUGERENCIAS)),
                                                     SUGERENCIAS)):
            col.button(texto, icon=icono, key=f"sug_{i}", width="stretch",
                       on_click=usar_sugerencia, args=(texto,))
        # Al abrir no se muestra la ultima charla (puede ser de otro cliente y haber
        # alguien enfrente): se ofrece retomarla, sin mostrar de que se trataba.
        ultima = historial.listar_conversaciones(limite=1)
        if ultima:
            id_c, _, fecha, _ = ultima[0]
            st.button(f"Retomar la última consulta ({fecha_legible(fecha)})",
                      icon=":material/history:", type="tertiary", key="retomar_ultima",
                      on_click=retomar, args=(id_c,))
    return entrada


def mostrar_mensaje(idx, m, ultimo):
    rol = m.get("rol") or "assistant"
    with st.container(key=f"msg_{'u' if rol == 'user' else 'a'}_{idx}"):
        with st.chat_message(rol, avatar=AVATARES.get(rol)):
            if rol == "user":
                st.markdown(m.get("texto") or "")
                # Pregunta sin respuesta (se corto a mitad o se cambio de pestana).
                if ultimo and not st.session_state.get("por_responder"):
                    st.button("Responder esta pregunta", icon=":material/refresh:",
                              type="tertiary", key=f"reintentar_{idx}", on_click=reintentar)
            elif m.get("error"):
                st.error(m.get("texto") or "", icon=":material/error:")
                if ultimo:
                    st.button("Reintentar", icon=":material/refresh:", key=f"reintentar_{idx}",
                              on_click=reintentar)
            else:
                st.markdown(con_citas(m.get("texto")))
                mostrar_nota(m.get("nota"))
                mostrar_fuentes(m.get("fuentes"), f"h{idx}", abiertas=3 if ultimo else 0)


def responder(consulta, api_key):
    """Genera la respuesta a la ultima pregunta (que ya se ve en la charla)."""
    ss = st.session_state
    error = False
    with st.container(key="msg_a_live"):
        with st.chat_message("assistant", avatar=AVATARES["assistant"]):
            nota = ""
            if not api_key:
                with st.spinner("Buscando en su archivo…"):
                    _, frags, meta = generar_respuesta(consulta, k=ss.k_fuentes, api_key=None,
                                                       rerank=ss.rerank)
                texto = ("Para la respuesta redactada falta la **clave de Gemini** (se carga "
                         "en **Ajustes**, arriba a la derecha). Mientras tanto, estas son las "
                         "fuentes más relevantes de su archivo.")
                st.markdown(texto)
            else:
                t0 = time.time()
                with st.status("Buscando en su archivo…", expanded=True) as paso:
                    st.caption("Suele tardar entre 20 y 60 segundos.")
                    try:
                        texto, frags, meta = generar_respuesta(
                            consulta, k=ss.k_fuentes, api_key=api_key,
                            rerank=ss.rerank, log=pasos_en(paso))
                        paso.update(label=f"Listo en {time.time() - t0:.0f} s · "
                                          f"{len(frags)} fuente(s) consultada(s)",
                                    state="complete", expanded=False)
                    except Exception as e:
                        texto, frags, meta = mensaje_error(e, "responder la consulta"), [], {}
                        error = True
                        paso.update(label="No se pudo completar", state="error", expanded=False)
                if error:
                    st.error(texto, icon=":material/error:")
                else:
                    st.markdown(con_citas(texto))
                    aviso_modelo(meta)
                    nota = nota_privacidad(meta)
                    mostrar_nota(nota)
            mostrar_fuentes(frags, "live")
    ss.mensajes.append({"rol": "assistant", "texto": texto, "nota": nota, "fuentes": frags,
                        "error": error})
    # Los errores no se guardan en el historial: no son una respuesta.
    ss.conv_id = historial.guardar_conversacion(
        ss.get("conv_id"), [m for m in ss.mensajes if not m.get("error")])
    if error:
        st.rerun()  # para que aparezca "Reintentar"


def pie_consulta():
    """Debajo del cuadro de consulta: 'Nueva consulta' y el estado de privacidad, a un
    paso de donde se escribe (Fitts)."""
    izq, der = st.columns([1.25, 4], vertical_alignment="center")
    with izq:
        st.button("Nueva consulta", icon=":material/add_comment:", type="tertiary",
                  key="nueva_consulta", on_click=nueva_consulta)
    with der:
        franja_privacidad()


def pantalla_consultar(api_key):
    ss = st.session_state
    ss.setdefault("mensajes", [])
    ss.setdefault("conv_id", None)

    # El texto dictado va al cuadro de consulta para revisarlo antes de enviar. Tiene
    # que asignarse antes de crear el widget.
    if "a_cuadro" in ss:
        ss.entrada = ss.pop("a_cuadro")
        st.toast("Revise el texto dictado y presione Enter para enviarlo.", icon=":material/mic:")

    if not ss.mensajes:
        entrada = bienvenida()
    else:
        for idx, m in enumerate(ss.mensajes):
            mostrar_mensaje(idx, m, ultimo=(idx == len(ss.mensajes) - 1))
        entrada = cuadro_consulta()
        with st.bottom:
            pie_consulta()

    consulta = None
    if entrada is not None:
        texto = (entrada if isinstance(entrada, str) else getattr(entrada, "text", "")) or ""
        audio = None if isinstance(entrada, str) else getattr(entrada, "audio", None)
        if audio is not None:
            with st.spinner("Pasando el audio a texto (en esta PC)…"):
                try:
                    from transcribir import transcribir
                    dictado = transcribir(audio.getvalue())
                except Exception as e:
                    dictado = ""
                    st.error(f"No pude pasar el audio a texto ({type(e).__name__}). Pruebe de "
                             "nuevo o escriba la consulta.", icon=":material/mic_off:")
            if dictado:
                ss.a_cuadro = " ".join(x for x in (texto.strip(), dictado) if x)
                st.rerun()
        else:
            consulta = texto.strip() or None
    consulta = consulta or ss.pop("consulta_pendiente", None)
    if consulta:
        # Primero se muestra la pregunta en la charla (eco inmediato, Doherty) y
        # recien despues se busca y redacta.
        ss.mensajes.append({"rol": "user", "texto": consulta})
        ss.por_responder = True
        st.rerun()
    if ss.pop("por_responder", False) and ss.mensajes and ss.mensajes[-1].get("rol") == "user":
        responder(ss.mensajes[-1].get("texto"), api_key)


# -------------------------------- Resumen de causa --------------------------------

def pantalla_resumen(api_key):
    ss = st.session_state
    st.caption("Elija una causa y la IA arma una ficha con carátula, partes, estado procesal "
               "y una línea de tiempo, usando solo lo que figura en los documentos. Cada "
               "dato dice de qué documento sale.")
    casos = causas.listar_casos()
    if not casos:
        st.info("Todavía no hay causas con carpeta propia en el archivo. Se agregan desde "
                "**Archivo**.", icon=":material/folder_off:")
        return
    etiquetas = {c: f"{c}  ·  {n} documento(s)" for c, n, _ in casos}
    with st.container(border=True, key="panel_ficha"):
        caso = st.selectbox("Causa", list(etiquetas), format_func=etiquetas.get, index=None,
                            key="causa_sel",
                            placeholder="Escriba el apellido o elíjala de la lista…")
        franja_privacidad()
        if st.button("Generar ficha", type="primary", icon=":material/summarize:",
                     width="stretch", key="cta_ficha"):
            if not caso:
                st.warning("Primero elija una causa de la lista.", icon=":material/arrow_upward:")
            elif not api_key:
                st.warning(SIN_CLAVE, icon=":material/key:")
            else:
                from ficha import generar_ficha
                with st.status("Leyendo la causa…", expanded=True) as paso:
                    st.caption("Suele tardar entre 30 y 60 segundos.")
                    try:
                        texto_f, docs_f, meta_f = generar_ficha(
                            caso, api_key=api_key, log=pasos_en(paso))
                        paso.update(label="Ficha lista", state="complete", expanded=False)
                    except Exception as e:
                        paso.update(label="No se pudo completar", state="error")
                        texto_f, docs_f, meta_f = None, {}, {}
                        st.error(mensaje_error(e, "generar la ficha"), icon=":material/error:")
                if texto_f:
                    historial.guardar_ficha(caso, texto_f, docs_f, meta_f)
                    ss.ficha, ss.ficha_caso = texto_f, caso
                    ss.ficha_docs, ss.ficha_meta = docs_f, meta_f
                    st.toast("Ficha lista. También quedó guardada en el Historial.",
                             icon=":material/task_alt:")

    if ss.get("ficha"):
        caso = ss.get("ficha_caso", "")
        meta = ss.get("ficha_meta", {})
        extractos = meta.get("extractos") or []
        with st.container(border=True, key="hoja_ficha"):
            st.markdown(f"### Ficha · {md(caso)}")
            st.markdown(ficha_con_citas(ss.ficha))
        mostrar_nota(nota_privacidad(meta))
        aviso_modelo(meta)
        barra_descargas(ficha_para_exportar(ss.ficha, extractos),
                        f"ficha_{nombre_archivo(caso)}", "ficha", titulo=f"Ficha — {caso}")
        fuentes, numeros = fuentes_de_ficha(ss.ficha, extractos)
        mostrar_fuentes(fuentes, "ficha", abiertas=3, titulo="De dónde sale cada dato",
                        rotulo="Extracto", numeros=numeros)
        docs = ss.get("ficha_docs", {})
        if docs:
            with st.expander(f"Documentos de la causa ({len(docs)})", icon=":material/folder_open:"):
                for j, (nombre, ruta) in enumerate(docs.items()):
                    c1, c2 = st.columns([4, 1.45], vertical_alignment="center")
                    c1.markdown(f":material/description: {md(nombre)}")
                    with c2:
                        abrir_original(ruta, f"fichadoc_{j}")


# ------------------------------------ Redactar ------------------------------------

def pasos_redaccion(actual):
    """Donde esta parado y cuanto falta (gradiente de meta)."""
    nombres = ["Contar el caso", "Revisar el borrador", "Descargar en Word"]
    partes = []
    for i, nombre in enumerate(nombres, 1):
        if i < actual:
            partes.append(f":green-badge[:material/check: {i}. {nombre}]")
        elif i == actual:
            partes.append(f":blue-badge[{i}. {nombre}]")
        else:
            partes.append(f":gray-badge[{i}. {nombre}]")
    st.markdown("  →  ".join(partes))


def revision(texto, tipo):
    """Revision antes de descargar, a la vista (Zeigarnik): lo que falta, no lo que esta."""
    import checklist as chk
    rev = chk.evaluar(texto, tipo)
    partes = rev["partes"]
    n_ok = sum(1 for _, presente in partes if presente)
    with st.container(border=True, key="panel_revision"):
        st.markdown("#### Revisión antes de descargar")
        detalle = f" · tipo detectado: {rev['categoria']}" if rev["categoria"] else ""
        st.progress(n_ok / len(partes) if partes else 0.0,
                    text=f"Partes típicas del escrito: {n_ok} de {len(partes)}{detalle}")
        for nombre, presente in partes:
            if not presente:
                st.markdown(f":orange[:material/error:] Revise si falta: **{nombre}**")
        completar = rev["faltan_completar"]
        if completar:
            muestra = ", ".join(f"`{c}`" for c in completar[:8])
            st.warning(f"Faltan completar {len(completar)} dato(s): {muestra}"
                       + ("…" if len(completar) > 8 else ""), icon=":material/edit_note:")
        else:
            st.markdown(":green[:material/check_circle:] No quedan datos marcados para completar.")
        st.caption("Guía automática por palabras clave, no un control jurídico. Revise "
                   "siempre el escrito.")


def pantalla_redactar(api_key):
    ss = st.session_state
    hay_borrador = bool(ss.get("borrador"))
    pasos_redaccion(2 if hay_borrador else 1)
    st.caption("Cuente el caso y la IA redacta un borrador con el estilo de sus escritos. "
               "Después lo revisa aquí y lo baja en Word.")
    with st.container(border=True, key="panel_redactar"):
        st.selectbox("Tipo de escrito", TIPOS_ESCRITO, index=None, key="red_tipo",
                     accept_new_options=True,
                     placeholder="Elija uno de la lista o escriba otro…")
        st.text_area("Hechos del caso y qué se pide", key="red_desc", height=200,
                     placeholder="Ej.: detenido el 3/9 en un allanamiento sin orden en su casa. "
                                 "Sin antecedentes, trabaja y vive con su familia. "
                                 "Pedir la excarcelación.")
        franja_privacidad()
        if st.button("Redactar borrador", type="primary", icon=":material/edit_document:",
                     width="stretch", key="cta_redactar"):
            tipo = ss.get("red_tipo") or ""
            descripcion = ss.get("red_desc") or ""
            if not api_key:
                st.warning(SIN_CLAVE, icon=":material/key:")
            elif not descripcion.strip():
                st.warning("Primero cuente los hechos del caso.", icon=":material/arrow_upward:")
            else:
                from redactar import redactar
                with st.status("Buscando escritos parecidos…", expanded=True) as paso:
                    st.caption("Suele tardar entre 30 y 90 segundos.")
                    try:
                        borrador, frags, meta = redactar(
                            descripcion, tipo, k=8, api_key=api_key,
                            rerank=ss.rerank, log=pasos_en(paso))
                        paso.update(label="Borrador listo", state="complete", expanded=False)
                    except Exception as e:
                        paso.update(label="No se pudo completar", state="error")
                        borrador = None
                        st.error(mensaje_error(e, "redactar el borrador"), icon=":material/error:")
                if borrador:
                    historial.guardar_borrador(tipo, descripcion, borrador, frags, meta)
                    ss.borrador, ss.borrador_tipo = borrador, tipo
                    ss.borrador_meta, ss.borrador_frags = meta, frags
                    # Sin esto el editor seguia mostrando (y descargando) el borrador anterior.
                    ss.borrador_edit = borrador
                    st.toast("Borrador listo. También quedó guardado en el Historial.",
                             icon=":material/task_alt:")
                    st.rerun()

    if not hay_borrador:
        return
    ss.setdefault("borrador_edit", ss.borrador)
    st.markdown("### Borrador")
    st.caption("Corríjalo aquí mismo antes de bajarlo. Lo que falta quedó marcado como "
               "[COMPLETAR: …].")
    st.text_area("Borrador", key="borrador_edit", height=520, label_visibility="collapsed")
    texto = ss.get("borrador_edit") or ss.borrador
    revision(texto, ss.get("borrador_tipo", ""))
    meta = ss.get("borrador_meta", {})
    mostrar_nota(nota_privacidad(meta))
    aviso_modelo(meta)
    if meta.get("de_otras_causas"):
        st.caption(f":material/lock: {meta['de_otras_causas']} dato(s) de otras causas del "
                   "estudio NO se volcaron al borrador: quedaron como **[COMPLETAR: …]** "
                   "para que usted los complete (secreto profesional).")
    mostrar_fuentes(ss.get("borrador_frags"), "red", abiertas=0,
                    titulo="Escritos usados como modelo")
    # La descarga queda fija abajo: siempre a mano aunque el escrito sea largo (Fitts).
    with st.bottom:
        barra_descargas(texto, nombre_archivo(ss.get("borrador_tipo") or "escrito"), "borrador")


# ------------------------------------ Historial ------------------------------------

def aviso_deshacer():
    """Despues de borrar, deshacer esta a un clic (pico-final, tolerancia a errores)."""
    ub = st.session_state.get("ultimo_borrado")
    if not ub:
        return
    with st.container(border=True, key="panel_deshacer"):
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        c1.markdown(f":material/delete: **{md(ub[2])}** está en la papelera.")
        if c2.button("Deshacer", icon=":material/undo:", width="stretch", key="deshacer"):
            historial.restaurar(ub[0], ub[1])
            st.session_state.pop("ultimo_borrado", None)
            st.rerun()


def lista_conversaciones(filtro):
    convs = [c for c in historial.listar_conversaciones() if filtro in (c[1] or "").lower()]
    if not convs:
        st.info("No hay consultas guardadas" + (" con esa palabra." if filtro else " todavía."),
                icon=":material/forum:")
    for id_c, titulo, fecha, n in convs:
        with st.container(border=True, key=f"item_conv_{id_c}"):
            st.markdown(f"**{md(titulo)}**")
            st.caption(f":material/schedule: {fecha_legible(fecha)} · {n} pregunta(s)")
            izq, der = st.columns([3, 1], vertical_alignment="center")
            izq.button("Retomar esta consulta", icon=":material/replay:", key=f"ret_{id_c}",
                       on_click=retomar, args=(id_c,))
            with der:
                boton_borrar(titulo, "conversacion", id_c)


def lista_fichas(filtro):
    fichas = [f for f in historial.listar_fichas() if filtro in (f[1] or "").lower()]
    if not fichas:
        st.info("No hay fichas guardadas" + (" con esa palabra." if filtro else " todavía."),
                icon=":material/summarize:")
    for id_f, caso, fecha in fichas:
        with st.expander(f"{caso}  ·  {fecha_legible(fecha)}", icon=":material/summarize:"):
            d = historial.cargar_ficha(id_f)
            extractos = (d.get("meta") or {}).get("extractos") or []
            st.markdown(ficha_con_citas(d.get("texto", "")))
            fuentes, numeros = fuentes_de_ficha(d.get("texto", ""), extractos)
            mostrar_fuentes(fuentes, f"hf_{id_f}", abiertas=0, titulo="De dónde sale cada dato",
                            rotulo="Extracto", numeros=numeros)
            izq, der = st.columns([3, 1], vertical_alignment="center")
            with izq:
                barra_descargas(ficha_para_exportar(d.get("texto", ""), extractos),
                                f"ficha_{nombre_archivo(caso)}", f"f_{id_f}",
                                titulo=f"Ficha — {caso}")
            with der:
                boton_borrar(f"la ficha de {caso}", "ficha", id_f)


def lista_borradores(filtro):
    borradores = [b for b in historial.listar_borradores()
                  if filtro in f"{b[1]} {b[2]}".lower()]
    if not borradores:
        st.info("No hay borradores guardados" + (" con esa palabra." if filtro else " todavía."),
                icon=":material/edit_document:")
    for id_b, tipo_b, desc_b, fecha in borradores:
        etiqueta = tipo_b or "Escrito sin tipo"
        resumen = " ".join((desc_b or "").split())[:60]
        with st.expander(f"{etiqueta}  ·  {resumen}…  ·  {fecha_legible(fecha)}",
                         icon=":material/edit_document:"):
            d = historial.cargar_borrador(id_b)
            st.caption("**Caso descrito:** " + md(d.get("descripcion") or ""))
            st.markdown(d.get("texto", ""))
            izq, der = st.columns([3, 1], vertical_alignment="center")
            with izq:
                barra_descargas(d.get("texto", ""), nombre_archivo(tipo_b or "escrito"),
                                f"b_{id_b}")
            with der:
                boton_borrar(f"el borrador «{etiqueta}»", "borrador", id_b)


def papelera():
    items = historial.listar_papelera()
    if not items:
        return
    nombres = {"conversacion": "consulta", "ficha": "ficha", "borrador": "borrador"}
    with st.expander(f"Papelera ({len(items)}) · se puede recuperar", icon=":material/delete:"):
        for tipo_p, id_p, titulo_p in items:
            c1, c2 = st.columns([3, 1], vertical_alignment="center")
            c1.markdown(f"**{md(titulo_p)}** · _{nombres.get(tipo_p, tipo_p)}_")
            c2.button("Recuperar", icon=":material/restore_from_trash:", width="stretch",
                      key=f"rec_{tipo_p}_{id_p}",
                      on_click=lambda t=tipo_p, i=id_p: historial.restaurar(t, i))
        with st.container(horizontal=True, horizontal_alignment="right"):
            if st.button("Vaciar la papelera", icon=":material/delete_forever:", type="tertiary",
                         key="del_papelera"):
                confirmar_vaciado(len(items))


def pantalla_historial():
    st.caption("Todo lo que consultó, las fichas y los borradores quedan guardados en "
               "esta PC. No se sube a ningún lado.")
    aviso_deshacer()
    n_conv, n_fic, n_bor, megas = historial.estadisticas()
    c1, c2, c3 = st.columns(3)
    c1.metric("Consultas", n_conv, border=True)
    c2.metric("Fichas", n_fic, border=True)
    c3.metric("Borradores", n_bor, border=True)
    buscar = st.text_input("Buscar en el historial", key="hist_buscar", icon=":material/search:",
                           placeholder="Una palabra: un apellido, un tipo de escrito…")
    filtro = (buscar or "").strip().lower()
    tab_c, tab_f, tab_b = st.tabs([":material/forum: Consultas", ":material/summarize: Fichas",
                                   ":material/edit_document: Borradores"])
    with tab_c:
        lista_conversaciones(filtro)
    with tab_f:
        lista_fichas(filtro)
    with tab_b:
        lista_borradores(filtro)
    papelera()
    st.caption(f"Ocupan {megas:.1f} MB en disco.".replace(".", ",", 1))


# ------------------------------------- Archivo -------------------------------------

_AVANCE = re.compile(r"\.\.\.\s*(\d+)\s*/\s*(\d+)")


def avance(lineas):
    """(fraccion o None, ultima linea) a partir del registro del indexado."""
    for linea in reversed(lineas):
        m = _AVANCE.search(linea)
        if m and int(m.group(2)):
            return min(int(m.group(1)) / int(m.group(2)), 1.0), linea.strip()
    return None, (lineas[-1].strip() if lineas else "Preparando…")


def mostrar_avance(trabajo):
    st.markdown("#### Agregando documentos")
    if not trabajo["listo"]:
        @st.fragment(run_every=2)
        def _avance():
            frac, linea = avance(trabajo["lineas"])
            texto = linea
            if frac:
                pasado = time.time() - trabajo["inicio"]
                if frac > 0.05:
                    texto += f"  ·  faltan {duracion((pasado / frac - pasado) / 60)}"
            st.progress(frac or 0.0, text=texto)
            if trabajo["listo"]:
                st.rerun()

        _avance()
        st.caption("No cierre esta ventana mientras trabaja. Lo ya procesado se guarda "
                   "aunque lo frene.")
        if st.button("Frenar", icon=":material/stop_circle:", key="frenar"):
            trabajo["parar"].set()
            st.warning("Frenando… termina el documento en curso y guarda lo hecho.",
                       icon=":material/hourglass_top:")
        return
    if trabajo["error"]:
        st.error(f"No se pudo terminar: {trabajo['error']}", icon=":material/error:")
    else:
        st.success(f"Listo: se agregaron {miles(trabajo['docs'])} documento(s) al archivo.",
                   icon=":material/task_alt:")
    with st.expander("Ver el detalle de lo que hizo", icon=":material/receipt_long:"):
        st.code("\n".join(trabajo["lineas"]))
    if st.button("Entendido", key="indexado_ok"):
        st.session_state.pop("indexado", None)
        st.session_state.pop("estimacion", None)
        st.rerun()


def empezar_indexado(carpeta, convertir, ocr):
    import threading
    candado = candado_indexado()
    if candado["activo"]:
        st.warning("Ya se están agregando documentos. Espere a que termine.",
                   icon=":material/hourglass_top:")
        return
    candado["activo"] = True
    # Corre en un hilo aparte para que la pantalla siga respondiendo y se pueda frenar
    # (ISO 9241-110: controlabilidad).
    estado = {"lineas": [], "listo": False, "error": None, "docs": 0, "frags": 0,
              "parar": threading.Event(), "inicio": time.time()}

    def trabajar():
        try:
            d, f = archivo.indexar_carpeta(carpeta, log=lambda m: estado["lineas"].append(str(m)),
                                           convertir=convertir, ocr=ocr,
                                           parar=estado["parar"].is_set)
            estado["docs"], estado["frags"] = d, f
            causas.refrescar()
            resumen_indice.clear()
        except Exception as e:
            estado["error"] = f"{type(e).__name__}: {e}"
        finally:
            estado["listo"] = True
            candado["activo"] = False

    threading.Thread(target=trabajar, daemon=True).start()
    st.session_state.indexado = estado
    st.rerun()


def pantalla_archivo():
    ss = st.session_state
    st.caption("Agregue documentos al archivo desde una carpeta de la PC o un disco externo. "
               "Todo se procesa aquí, sin subir nada.")
    n_docs, _, raices = resumen_indice()
    m1, m2 = st.columns(2)
    m1.metric("Documentos en el archivo", miles(n_docs), border=True)
    m2.metric("Causas con carpeta propia", len(causas.listar_casos()), border=True)
    if raices:
        with st.expander("¿De dónde salen los documentos?", icon=":material/folder:"):
            for r, n in raices:
                st.markdown(f"- `{r}` — {n} documento(s)")

    trabajo = ss.get("indexado")
    en_curso = bool(trabajo) and not trabajo["listo"]

    st.markdown("#### 1. Elija de dónde traerlos")
    with st.container(border=True, key="panel_origen"):
        unidades = discos()
        etiquetas = {l: f"{l}:  {e or 'Disco sin nombre'}  ·  {libre:.0f} GB libres"
                     for l, e, libre, _ in unidades}
        cu, cr = st.columns([1, 1.6])
        letra = cu.selectbox("Disco", list(etiquetas), format_func=etiquetas.get,
                             key="disco_sel", disabled=en_curso)
        sub = cr.text_input("Carpeta dentro del disco (opcional)", key="disco_sub",
                            disabled=en_curso,
                            placeholder="Ej.: Casos\\2026  ·  vacío = todo el disco")
        carpeta = armar_carpeta(letra, sub)
        st.caption(f"Se va a revisar: `{carpeta}`")
        if st.button("Buscar documentos nuevos", icon=":material/search:", key="ver_indexar",
                     disabled=en_curso):
            with st.spinner("Revisando la carpeta…"):
                ss.estimacion = archivo.estimar(carpeta)
                ss.estimacion_carpeta = carpeta

    est = ss.get("estimacion")
    if est and ss.get("estimacion_carpeta") == carpeta and not trabajo:
        if est.get("error"):
            st.error(est["error"], icon=":material/usb_off:")
        elif est["nuevos"] == 0 and not est.get("pendientes_ocr"):
            st.success(f"Todo al día: los {miles(est['total'])} documentos de esa carpeta ya "
                       "están en el archivo.", icon=":material/task_alt:")
        else:
            st.markdown("#### 2. Revise antes de arrancar")
            with st.container(border=True, key="panel_estimacion"):
                e1, e2, e3 = st.columns(3)
                e1.metric("Documentos nuevos", miles(est["nuevos"]))
                e2.metric("Ya estaban", miles(est["ya_indexados"]))
                e3.metric("Tiempo estimado", duracion(est["minutos"]))
                if est["por_extension"]:
                    st.caption("Por tipo: " + ", ".join(f"**{k}**: {v}"
                                                        for k, v in est["por_extension"].items()))
                if est.get("pendientes_ocr"):
                    st.caption(f":material/document_scanner: Además hay {est['pendientes_ocr']} "
                               "PDF escaneado(s) de antes que todavía no se leyeron.")
                if est["gpu"]:
                    st.caption(":material/memory: Esta PC tiene placa de video: va rápido.")
                else:
                    st.warning("Esta PC no tiene placa de video compatible: el proceso usa el "
                               "procesador y va unas 15 veces más lento. Puede dejarlo "
                               "trabajando y volver más tarde.", icon=":material/schedule:")
                if est["a_convertir"]:
                    st.caption(f":material/description: {est['a_convertir']} documento(s) viejos "
                               "(.doc) se convierten primero. Necesita Word instalado.")
                op1, op2 = st.columns(2)
                ocr = op1.toggle("Leer también los PDF escaneados", value=True, key="op_ocr",
                                 help="Más lento, pero recupera el texto de documentos que son "
                                      "solo una foto o un escaneo.")
                conv = op2.toggle("Convertir los .doc viejos", value=True, key="op_conv")
                if st.button("Agregar al archivo ahora", type="primary",
                             icon=":material/library_add:", width="stretch", key="cta_indexar"):
                    empezar_indexado(carpeta, conv, ocr)

    if trabajo:
        mostrar_avance(trabajo)

    st.space("medium")
    with st.expander("El disco externo aparece con otra letra", icon=":material/usb:"):
        st.caption("Windows le pone la letra según qué haya conectado: el mismo disco puede "
                   "ser E: un día y G: otro. Si pasa, el asistente no encuentra los originales "
                   "y volvería a procesar todo. Aquí se corrige sin volver a procesar.")
        r1, r2 = st.columns(2)
        viejo = r1.text_input("Letra que tenía antes", placeholder="Ej.: E", max_chars=3,
                              key="remap_viejo")
        nuevo = r2.selectbox("Letra que tiene ahora", [l for l, *_ in discos()], index=None,
                             placeholder="Elija el disco", key="remap_nuevo")
        if st.button("Corregir las rutas", icon=":material/sync_alt:", key="remap"):
            v, n = normalizar_letra(viejo), normalizar_letra(nuevo)
            if not v or not n:
                st.warning("Complete las dos letras (por ejemplo, E y G).",
                           icon=":material/arrow_upward:")
            elif v == n:
                st.info("Las dos letras son iguales: no hay nada que corregir.")
            else:
                cambiados = archivo.remapear(v, n)
                if cambiados:
                    causas.refrescar()
                    resumen_indice.clear()
                    st.success(f"Listo: se corrigieron {miles(cambiados)} referencias de {v} a {n}.",
                               icon=":material/task_alt:")
                else:
                    st.info(f"No había documentos guardados con la letra {v}.")


# ------------------------------------ encabezado ------------------------------------

def iniciar_estado():
    ss = st.session_state
    for k in CAMPOS_QUE_PERSISTEN:
        if k in ss:
            ss[k] = ss[k]
    ss.setdefault("k_fuentes", 6)
    ss.setdefault("rerank", False)
    ss.setdefault("escala", leer_escala())
    if "modo" not in ss or ss.modo not in MODOS:
        # El modo va en la direccion (?modo=...): F5 y "Atras" no lo pierden (Jakob).
        pedido = st.query_params.get("modo")
        ss.modo = pedido if pedido in MODOS else "Consultar"


def selector_letra(con_etiqueta=True):
    st.segmented_control("Tamaño de letra", list(estilos.ESCALAS), key="escala",
                         required=True, format_func=estilos.ETIQUETAS_ESCALA.get,
                         on_change=al_cambiar_escala, width="stretch",
                         label_visibility="visible" if con_etiqueta else "collapsed")


def panel_ajustes(clave_fija):
    """Ajustes con texto (no un engranaje solo) y agrupados; lo tecnico, plegado (Hick).
    Desde el celular solo se muestra lo que no compromete la seguridad."""
    ss = st.session_state
    api_key = clave_fija
    with st.popover("Ajustes", icon=":material/settings:", width="stretch", key="ajustes"):
        if REMOTO:
            st.markdown("**Tamaño de letra**")
            selector_letra(con_etiqueta=False)
        st.markdown("**Protección de datos**")
        st.markdown(":green-badge[:material/lock: Siempre activa]")
        st.caption("Antes de enviar a Gemini se ocultan nombres, DNI, domicilios, teléfonos, "
                   "CBU, patentes y los apellidos de las carpetas de causas. Usted los ve "
                   "completos aquí. No se puede desactivar.")
        if not REMOTO:
            st.markdown("**Clave de Gemini**")
            if clave_fija:
                st.markdown(":green-badge[:material/check: Clave cargada]")
                if st.button("Olvidar la clave guardada", icon=":material/key_off:",
                             type="tertiary", key="olvidar_clave"):
                    ss.pedir_olvidar_clave = True
            else:
                api_key = st.text_input("Pegue la clave de Gemini", type="password",
                                        key="clave_nueva")
                st.caption("Se consigue en aistudio.google.com/apikey. Para causas reales "
                           "conviene una clave de plan pago: con el plan gratuito, Google puede "
                           "usar lo que se envía para mejorar sus productos.")
                if api_key:
                    guardar_clave(api_key)
            st.markdown("**Celular**")
            if st.button("Usar en el celular", icon=":material/smartphone:", width="stretch",
                         key="abrir_celular"):
                ss.pedir_celular = True
        with st.expander("Avanzado", icon=":material/tune:"):
            st.slider("Cuántas fuentes usar por respuesta", 2, 10, key="k_fuentes")
            st.toggle("Máxima precisión (reordena los resultados; un poco más lento)",
                      key="rerank")
            st.caption(f"Modelo de Gemini: `{MODELO_GEMINI}`")
    return api_key


def navegacion():
    """Baldosas grandes e iguales: icono + texto, la activa con relleno."""
    modo = st.session_state.modo
    with st.container(key="navbar"):
        for i, (col, (m, icono)) in enumerate(zip(st.columns(len(MODOS)), MODOS.items())):
            col.button(ETIQUETAS_CORTAS.get(m, m) if REMOTO else m, icon=icono,
                       key=f"nav_{i}", width="stretch",
                       type="primary" if modo == m else "secondary",
                       on_click=ir_a, args=(m,))


# ------------------------------------- celular -------------------------------------

@st.cache_resource
def intentos_pin():
    """Intentos fallidos, compartidos por todas las conexiones: frena la adivinanza."""
    return {"fallos": 0, "hasta": 0.0}


def puerta_pin():
    """Desde el celular (o cualquier otro equipo de la red) no se ve nada sin el PIN."""
    import seguridad
    ss = st.session_state
    if ss.get("autorizado"):
        return
    with st.container(key="cabecera"):
        estilos.encabezado()
    if not seguridad.hay_pin():
        st.error("El acceso desde otros equipos no está habilitado. Se activa desde la PC del "
                 "estudio: Ajustes → Usar en el celular.", icon=":material/lock:")
        st.stop()
    st.markdown("### Ingrese su PIN")
    st.caption("Es el PIN que eligió en la PC del estudio (Ajustes → Usar en el celular).")
    with st.form("form_pin", border=False):
        pin = st.text_input("PIN", type="password", max_chars=8, placeholder="6 a 8 números")
        entrar = st.form_submit_button("Entrar", type="primary", icon=":material/lock_open:",
                                       width="stretch")
    if entrar:
        control = intentos_pin()
        restante = control["hasta"] - time.time()
        if restante > 0:
            st.error(f"Demasiados intentos. Pruebe de nuevo en {int(restante // 60) + 1} min.",
                     icon=":material/timer:")
        elif seguridad.verificar_pin(pin):
            control["fallos"] = 0
            ss.autorizado = True
            st.rerun()
        else:
            control["fallos"] += 1
            if control["fallos"] >= seguridad.MAX_FALLOS:
                control["fallos"], control["hasta"] = 0, time.time() + seguridad.BLOQUEO_SEGUNDOS
            st.error("PIN incorrecto.", icon=":material/error:")
    st.stop()


@st.dialog("Usar el asistente en el celular", width="medium")
def dialogo_celular():
    import celular
    import seguridad
    st.caption("El celular tiene que estar en el mismo Wi-Fi que esta PC, y la PC prendida con "
               "el asistente abierto. Para entrar, el celular pide un PIN.")
    if not seguridad.hay_pin():
        st.markdown("**1. Elija un PIN** de 6 a 8 números.")
        c1, c2 = st.columns(2)
        p1 = c1.text_input("PIN", type="password", max_chars=8, key="pin_nuevo")
        p2 = c2.text_input("Repítalo", type="password", max_chars=8, key="pin_repetido")
        if st.button("Guardar el PIN", type="primary", width="stretch", key="guardar_pin"):
            if not seguridad.pin_valido(p1):
                st.warning("El PIN tiene que tener entre 6 y 8 números, sin letras.")
            elif p1 != p2:
                st.warning("Los dos PIN no coinciden.")
            else:
                seguridad.guardar_pin(p1)
                st.rerun(scope="fragment")
        return
    if not celular.activo():
        st.markdown(":green-badge[:material/check: PIN guardado]  **2. Active el acceso**")
        if st.button("Activar el acceso desde el celular", type="primary", width="stretch",
                     icon=":material/smartphone:", key="celular_on"):
            with st.spinner("Preparando el acceso (unos segundos)…"):
                ok = celular.iniciar()
            if ok:
                st.rerun(scope="fragment")
            st.error("No se pudo activar. Pruebe de nuevo; si sigue, cierre y vuelva a abrir el "
                     "asistente.", icon=":material/error:")
    else:
        direccion = celular.url()
        st.markdown(":green-badge[:material/check_circle: Acceso activado]")
        if direccion.startswith("http://127."):
            st.warning("Esta PC no parece estar conectada a una red Wi-Fi o cableada.",
                       icon=":material/wifi_off:")
        qr, texto = st.columns([1, 1.35], vertical_alignment="center")
        qr.image(celular.qr_png(direccion), width=210)
        with texto:
            st.markdown("**Apunte la cámara del celular a este código**, o escriba la "
                        "dirección en el navegador:")
            st.code(direccion, language=None)
            st.caption("Le va a pedir el PIN. Para tenerlo como una app más: en el menú del "
                       "navegador, «Agregar a la pantalla de inicio».")
        st.caption(":material/shield: Si el celular no llega a abrirlo, Windows lo está "
                   "bloqueando: ejecute una vez **Permitir celular.bat**, en la carpeta del "
                   "asistente (pide permiso de administrador).")
        if st.button("Desactivar el acceso desde el celular", icon=":material/phonelink_off:",
                     key="del_celular"):
            with st.spinner("Desactivando…"):
                celular.detener()
            st.rerun(scope="fragment")
    with st.expander("Cambiar el PIN", icon=":material/password:"):
        st.caption("Se borra el PIN actual y elige uno nuevo.")
        if st.button("Borrar el PIN actual", icon=":material/delete:", key="del_pin"):
            seguridad.borrar_pin()
            st.rerun(scope="fragment")


@st.cache_resource(show_spinner=False)
def reubicar_indice():
    """Una vez por arranque: si la carpeta se copio a otra PC, corrige las rutas."""
    try:
        n = archivo.reubicar_si_se_movio()
    except Exception:
        n = 0
    if n:
        causas.refrescar()
    return n


# ------------------------------------- arranque -------------------------------------

st.set_page_config(page_title="Asistente Legal",
                   page_icon=str(ICONO) if ICONO.exists() else ":material/balance:",
                   layout="centered", initial_sidebar_state="collapsed")
# Copia para el celular, o conexion que no viene de esta misma PC (la IP la da la
# conexion y no se puede falsificar desde otro equipo): se pide PIN.
_ip = st.context.ip_address
REMOTO = "--celular" in sys.argv or (isinstance(_ip, str) and _ip not in ("127.0.0.1", "::1"))
if REMOTO:
    MODOS = {m: i for m, i in TODOS_LOS_MODOS.items() if m != "Archivo"}
iniciar_estado()
estilos.aplicar_estilos(st.session_state.escala)
if REMOTO:
    puerta_pin()
else:
    reubicar_indice()

clave_fija = os.environ.get("GEMINI_API_KEY", "") or leer_clave_guardada()
with st.container(key="cabecera"):
    if REMOTO:
        marca, ajustes = st.columns([3.2, 1.2], vertical_alignment="center")
    else:
        marca, letra, ajustes = st.columns([3.2, 1.45, 1.2], vertical_alignment="bottom")
        with letra:
            # A la vista y no dentro de Ajustes: el tamano de letra es lo primero que
            # necesita un usuario mayor.
            selector_letra()
    with marca:
        estilos.encabezado()
    with ajustes:
        api_key = panel_ajustes(clave_fija)

navegacion()

if st.session_state.pop("pedir_olvidar_clave", False):
    confirmar_olvidar_clave()
if st.session_state.pop("pedir_celular", False):
    dialogo_celular()
if not api_key:
    st.info("Para las respuestas redactadas falta la **clave de Gemini**: se carga en "
            + ("la PC del estudio, en **Ajustes**." if REMOTO
               else "**Ajustes**, arriba a la derecha."), icon=":material/key:")

modo = st.session_state.modo
if modo == "Consultar":
    pantalla_consultar(api_key)
elif modo == "Resumen de causa":
    pantalla_resumen(api_key)
elif modo == "Redactar":
    pantalla_redactar(api_key)
elif modo == "Historial":
    pantalla_historial()
else:
    pantalla_archivo()

# Icono y manifiesto: permiten instalarla como app (Edge: "Instalar este sitio como
# aplicacion"; celular: "Agregar a la pantalla de inicio").
estilos.metadatos_app()
