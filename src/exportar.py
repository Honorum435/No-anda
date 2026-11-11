"""Exporta texto a Word (.docx) o PDF en memoria, para descargar desde la app."""
import io
import re


_TITULO = re.compile(r"^(#{1,6})\s+(.*)$")
_VINETA = re.compile(r"^[-*•]\s+")
_NUMERO = re.compile(r"^\d+[.)]\s+")
_SEPARADOR = re.compile(r"^:?-{2,}:?$")


def _celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def _bloques(texto):
    """Parte el texto en lineas sueltas y tablas markdown (| a | b |).
    Devuelve [('linea', str) | ('tabla', [[celdas], ...])]; la fila de guiones se descarta."""
    bloques, tabla = [], []
    for linea in (texto or "").split("\n"):
        if linea.strip().startswith("|") and linea.strip().count("|") >= 2:
            fila = _celdas(linea)
            if not all(_SEPARADOR.match(c) for c in fila if c):
                tabla.append(fila)
            continue
        if tabla:
            bloques.append(("tabla", tabla))
            tabla = []
        bloques.append(("linea", linea))
    if tabla:
        bloques.append(("tabla", tabla))
    return bloques


def _con_negritas(parrafo, texto):
    """Agrega el texto al parrafo convirtiendo **negrita** en negrita de Word."""
    for parte in re.split(r"(\*\*.+?\*\*)", texto):
        if len(parte) > 4 and parte.startswith("**") and parte.endswith("**"):
            parrafo.add_run(parte[2:-2]).bold = True
        elif parte:
            parrafo.add_run(parte)


def texto_a_docx(texto):
    """Convierte texto con markdown liviano (#, -, 1., **negrita**, tablas) a bytes de un .docx.

    Se traduce a formato real de Word (titulos, vinetas, numeracion, negritas y tablas):
    antes los simbolos quedaban a la vista y habia que limpiarlos a mano en cada escrito.
    """
    from docx import Document
    doc = Document()
    bloques = _bloques(texto)
    # El titulo menos profundo pasa a ser "Titulo 1" (la ficha usa ### para sus secciones).
    niveles = [len(m.group(1)) for tipo, l in bloques if tipo == "linea"
               for m in [_TITULO.match(l.strip())] if m]
    base = min(niveles) if niveles else 1
    for tipo, contenido in bloques:
        if tipo == "tabla":
            columnas = max(len(f) for f in contenido)
            tabla = doc.add_table(rows=0, cols=columnas)
            tabla.style = "Table Grid"
            for i, fila in enumerate(contenido):
                celdas = tabla.add_row().cells
                for j in range(columnas):
                    valor = fila[j] if j < len(fila) else ""
                    parrafo = celdas[j].paragraphs[0]
                    if i == 0:  # encabezado
                        parrafo.add_run(valor.replace("**", "")).bold = True
                    else:
                        _con_negritas(parrafo, valor)
            continue
        linea = contenido
        s = linea.strip()
        m = _TITULO.match(s)
        if m:
            doc.add_heading(m.group(2).replace("**", ""), level=min(len(m.group(1)) - base + 1, 4))
        elif _VINETA.match(s):
            _con_negritas(doc.add_paragraph(style="List Bullet"), _VINETA.sub("", s))
        elif _NUMERO.match(s):
            _con_negritas(doc.add_paragraph(style="List Number"), _NUMERO.sub("", s))
        else:
            _con_negritas(doc.add_paragraph(), linea)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _escapar(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)  # **negrita** -> <b>


def texto_a_pdf(texto, titulo=None):
    """Convierte texto (con markdown liviano: #, -, **negrita**, tablas) a bytes de un PDF."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                            topMargin=2.2 * cm, bottomMargin=2.2 * cm)
    base = getSampleStyleSheet()
    cuerpo = ParagraphStyle("cuerpo", parent=base["Normal"], fontName="Helvetica",
                            fontSize=11, leading=16, alignment=TA_JUSTIFY)
    celda = ParagraphStyle("celda", parent=cuerpo, fontSize=9.5, leading=13, alignment=0)
    titulo_st = ParagraphStyle("titulo", parent=base["Heading2"], fontName="Helvetica-Bold",
                               fontSize=13, spaceBefore=10, spaceAfter=4,
                               textColor=colors.HexColor("#1E3A8A"))

    flujo = []
    if titulo:
        flujo.append(Paragraph(_escapar(titulo), titulo_st))
    for tipo, contenido in _bloques(texto):
        if tipo == "tabla":
            columnas = max(len(f) for f in contenido)
            filas = [[Paragraph(_escapar(f[j] if j < len(f) else ""), celda)
                      for j in range(columnas)] for f in contenido]
            t = Table(filas, repeatRows=1, hAlign="LEFT",
                      colWidths=[doc.width / columnas] * columnas)
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9AA3B2")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9EEF9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            flujo.extend([t, Spacer(1, 6)])
            continue
        s = contenido.strip()
        if not s:
            flujo.append(Spacer(1, 6))
        elif s.startswith("#"):
            flujo.append(Paragraph(_escapar(s.lstrip("# ").strip()), titulo_st))
        elif s.startswith(("- ", "* ")):
            flujo.append(Paragraph("&bull; " + _escapar(s[2:]), cuerpo))
        else:
            flujo.append(Paragraph(_escapar(s), cuerpo))
    doc.build(flujo)
    return buf.getvalue()
