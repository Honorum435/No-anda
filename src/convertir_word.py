"""Convierte .doc, .odt y .rtf a .docx usando Microsoft Word (COM).
Se corre UNA vez antes de indexar, para que python-docx pueda leerlos.
Requiere Word instalado y pywin32.

Uso:
    python src/convertir_word.py "datos/casos_reales"
"""
import sys
from pathlib import Path

A_CONVERTIR = {".doc", ".odt", ".rtf"}
WD_FORMAT_DOCX = 16  # wdFormatDocumentDefault (.docx)


def convertir_carpeta(carpeta):
    import pythoncom
    import win32com.client as win32

    pythoncom.CoInitialize()
    # Rutas ABSOLUTAS: Word (COM) resuelve las relativas contra su propio directorio
    # de trabajo (system32) y no encuentra el archivo.
    archivos = [p.resolve() for p in Path(carpeta).rglob("*")
                if p.is_file() and p.suffix.lower() in A_CONVERTIR]
    if not archivos:
        print("No hay archivos .doc/.odt/.rtf para convertir.")
        return

    print(f"Convirtiendo {len(archivos)} archivo(s) con Word...")
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    ok, saltados, fallos = 0, 0, 0
    try:
        for p in archivos:
            destino = p.with_suffix(".docx")
            if destino.exists():
                saltados += 1
                continue
            try:
                doc = word.Documents.Open(
                    str(p), ReadOnly=True, AddToRecentFiles=False, ConfirmConversions=False
                )
                doc.SaveAs2(str(destino), FileFormat=WD_FORMAT_DOCX)
                doc.Close(False)
                ok += 1
            except Exception as e:
                fallos += 1
                print(f"  /!\\ No se pudo convertir un archivo {p.suffix}: {e}")
    finally:
        word.Quit()
    print(f"Listo. Convertidos: {ok} | Ya existian: {saltados} | Fallos: {fallos}")


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "datos/casos_reales"
    convertir_carpeta(carpeta)
