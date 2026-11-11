"""Extrae texto plano de documentos .docx, .pdf y .txt."""
from pathlib import Path

EXTENSIONES = {".docx", ".pdf", ".txt"}

def ruta_larga(ruta):
    """Ruta apta para abrir en Windows aunque supere los 260 caracteres (MAX_PATH).

    El archivo del estudio tiene carpetas anidadas de exportaciones de WhatsApp/Drive
    que pasan ese limite: el archivo aparece al listar la carpeta pero no se puede abrir.
    El prefijo \\\\?\\ desactiva ese limite. En otros sistemas devuelve la ruta tal cual.
    """
    import os
    s = os.path.abspath(str(ruta))
    if os.name == "nt" and not s.startswith("\\\\?\\\\"):
        return "\\\\?\\\\" + s
    return s



def _docx(ruta):
    """Texto de un .docx: parrafos Y tablas, en el orden real del documento.

    python-docx expone .paragraphs y .tables por separado; recorrer solo .paragraphs
    pierde por completo el contenido de las tablas (planillas de prueba, datos de
    cuenta, listados de partes), que en el archivo del estudio es contenido real.
    """
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(ruta_larga(ruta))
    partes = []

    def texto_tabla(tabla):
        filas = []
        for fila in tabla.rows:
            celdas = [c.text.strip().replace("\n", " ") for c in fila.cells]
            if any(celdas):
                filas.append(" | ".join(celdas))
        return "\n".join(filas)

    for hijo in doc.element.body.iterchildren():
        if hijo.tag.endswith("}p"):
            t = Paragraph(hijo, doc).text
            if t.strip():
                partes.append(t)
        elif hijo.tag.endswith("}tbl"):
            t = texto_tabla(Table(hijo, doc))
            if t.strip():
                partes.append(t)

    # Encabezados y pies (suelen traer caratula, juzgado y numero de causa).
    for seccion in doc.sections:
        for cont in (seccion.header, seccion.footer):
            for par in cont.paragraphs:
                if par.text.strip():
                    partes.append(par.text)
            for tabla in cont.tables:
                t = texto_tabla(tabla)
                if t.strip():
                    partes.append(t)

    return "\n".join(partes)


def _pdf(ruta):
    from pypdf import PdfReader
    return "\n".join((pag.extract_text() or "") for pag in PdfReader(ruta_larga(ruta)).pages)


def _txt(ruta):
    return Path(ruta_larga(ruta)).read_text(encoding="utf-8", errors="ignore")


def extraer_texto(ruta):
    """Devuelve el texto de un documento segun su extension."""
    ext = Path(ruta).suffix.lower()
    if ext == ".docx":
        return _docx(ruta)
    if ext == ".pdf":
        return _pdf(ruta)
    if ext == ".txt":
        return _txt(ruta)
    return ""


def extraer_carpeta(carpeta):
    """Recorre la carpeta (y subcarpetas) y devuelve [{ruta, nombre, texto}, ...]."""
    documentos = []
    for ruta in Path(carpeta).rglob("*"):
        if ruta.is_file() and ruta.suffix.lower() in EXTENSIONES:
            try:
                texto = extraer_texto(ruta)
            except Exception as e:
                print(f"  /!\\ No se pudo leer un archivo {ruta.suffix}: {type(e).__name__}")
                continue
            if texto and texto.strip():
                documentos.append({"ruta": str(ruta), "nombre": ruta.name, "texto": texto})
    return documentos
