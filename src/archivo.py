"""Gestion del archivo indexado desde la interfaz: elegir carpeta, estimar e indexar.

Pensado para que el abogado pueda enchufar su disco externo y actualizar el archivo
sin tocar la terminal. Todo corre local; si la PC no tiene GPU va igual, pero lento
(por eso el indexado es incremental: solo procesa lo que todavia no esta).
"""
import json
import os
import string
from pathlib import Path

from comun import BASE, CARPETA_INDICE, clave_ruta
from extraer_texto import EXTENSIONES

PROC_PATH = CARPETA_INDICE / "procesados.json"
OCR_PATH = CARPETA_INDICE / "ocr_hechos.json"


# --------------------------------- discos ---------------------------------

def discos():
    """Unidades montadas: [(letra, etiqueta, libre_GB, total_GB)]. Sirve para que el
    usuario elija el disco externo sin escribir la ruta a mano."""
    salida = []
    for letra in string.ascii_uppercase:
        raiz = f"{letra}:\\"
        if not os.path.exists(raiz):
            continue
        try:
            import shutil
            total, _, libre = shutil.disk_usage(raiz)
        except OSError:
            continue
        etiqueta = ""
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(raiz), buf, ctypes.sizeof(buf),
                None, None, None, None, 0)
            etiqueta = buf.value
        except Exception:
            pass
        salida.append((letra, etiqueta, libre / 2**30, total / 2**30))
    return salida


# ------------------------------ estado del indice ------------------------------

def _fragmentos():
    p = CARPETA_INDICE / "fragmentos.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def resumen_indice():
    """(n_documentos, n_fragmentos, carpetas_raiz) de lo que hay indexado hoy."""
    frags = _fragmentos()
    rutas = {f.get("ruta") for f in frags if f.get("ruta")}
    raices = {}
    for r in rutas:
        partes = str(r).replace("\\", "/").split("/")
        raiz = "/".join(partes[:6]) if len(partes) > 6 else str(Path(r).parent)
        raices[raiz] = raices.get(raiz, 0) + 1
    return len(rutas), len(frags), sorted(raices.items(), key=lambda x: -x[1])[:6]


def _leer_lista(ruta):
    try:
        return set(json.loads(ruta.read_text(encoding="utf-8")))
    except Exception:
        return set()


def _vistos(frags):
    vistos = {str(f.get("ruta")) for f in frags if f.get("ruta")} | _leer_lista(PROC_PATH)
    return {clave_ruta(v) for v in vistos}


def estimar(carpeta):
    """Que habria para hacer en esa carpeta, sin tocar nada.
    Devuelve dict con totales, nuevos por extension y una estimacion de tiempo."""
    carpeta = Path(carpeta)
    if not carpeta.exists():
        return {"error": "La carpeta no existe o el disco no está conectado."}
    # El indice guarda rutas absolutas: sin resolver, nada coincidiria y se
    # reindexaria todo de nuevo.
    carpeta = carpeta.resolve()

    frags = _fragmentos()
    vistos = _vistos(frags)
    total, nuevos, docs_viejos, por_ext = 0, [], 0, {}
    for p in carpeta.rglob("*"):
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if ext in EXTENSIONES or ext in {".doc", ".odt", ".rtf"}:
            # Un .doc que ya tiene su .docx al lado no aporta nada: se convirtio antes
            # y el .docx es el que se indexa. Contarlo inflaria la estimacion.
            if ext in {".doc", ".odt", ".rtf"} and p.with_suffix(".docx").exists():
                continue
            total += 1
            if clave_ruta(p) in vistos:
                docs_viejos += 1
            else:
                nuevos.append(p)
                por_ext[ext] = por_ext.get(ext, 0) + 1

    # PDF escaneados de una vuelta anterior que todavia no pasaron por el OCR (por
    # ejemplo, si en ese momento faltaba Tesseract).
    con_texto = {clave_ruta(f.get("ruta")) for f in frags if f.get("ruta")}
    hechos = {clave_ruta(r) for r in _leer_lista(OCR_PATH)}
    nuevos_claves = {clave_ruta(p) for p in nuevos}
    sin_ocr = [p for p in carpeta.rglob("*.pdf")
               if clave_ruta(p) not in con_texto and clave_ruta(p) not in hechos
               and clave_ruta(p) not in nuevos_claves]

    # ~46 fragmentos por documento en este archivo; velocidad segun haya GPU o no.
    # El OCR va aparte: ~30 s por documento escaneado.
    frag_est = len(nuevos) * 46
    try:
        import torch
        con_gpu = torch.cuda.is_available()
    except Exception:
        con_gpu = False
    vel = 85 if con_gpu else 5.5
    return {
        "carpeta": str(carpeta), "total": total, "ya_indexados": docs_viejos,
        "nuevos": len(nuevos), "por_extension": por_ext, "pendientes_ocr": len(sin_ocr),
        "a_convertir": sum(v for k, v in por_ext.items() if k in {".doc", ".odt", ".rtf"}),
        "gpu": con_gpu, "minutos": frag_est / vel / 60 + len(sin_ocr) * 0.5,
    }


# --------------------------------- indexar ---------------------------------

def indexar_carpeta(carpeta, log=print, convertir=True, ocr=True, parar=None):
    """Actualiza el indice con lo nuevo de 'carpeta'. Devuelve (docs, fragmentos).

    Tres pasos, los mismos que hace actualizar.ps1 por terminal:
      1. .doc/.odt/.rtf -> .docx (necesita Word instalado)
      2. indexado incremental de lo nuevo
      3. OCR de los PDF escaneados que quedaron sin texto
    """
    carpeta = Path(carpeta)
    if not carpeta.exists():
        raise FileNotFoundError("La carpeta no existe o el disco no está conectado.")
    carpeta = carpeta.resolve()

    if convertir:
        log("[1/3] Convirtiendo documentos viejos (.doc) a .docx…")
        try:
            from convertir_word import convertir_carpeta
            convertir_carpeta(carpeta)
        except Exception as e:
            log(f"   (sin conversion: {type(e).__name__}. Necesita Word instalado.)")
    else:
        log("[1/3] Conversion de .doc omitida.")

    if parar is not None and parar():
        log("Cancelado antes de indexar.")
        return 0, 0

    log("[2/3] Indexando los documentos nuevos…")
    from actualizar import actualizar_incremental
    docs, frags = actualizar_incremental(carpeta, log=log, parar=parar)

    if ocr:
        log("[3/3] OCR de los PDF escaneados sin texto…")
        try:
            from ocr import indexar_ocr
            d2, f2 = indexar_ocr(carpeta, dpi=300, log=log, parar=parar)
            docs, frags = docs + d2, frags + f2
        except Exception as e:
            log(f"   (sin OCR: {type(e).__name__}. Necesita Tesseract instalado.)")
    else:
        log("[3/3] OCR omitido.")

    return docs, frags


# ------------------------- disco externo con otra letra -------------------------

def remapear(prefijo_viejo, prefijo_nuevo):
    """Reescribe las rutas del indice cuando el disco externo vuelve con otra letra.

    Windows le asigna la letra segun que haya conectado: el mismo disco puede ser E:
    hoy y G: manana. Sin esto, el indice apunta a rutas muertas (no se puede abrir el
    original) y los mismos documentos se reindexarian como si fueran nuevos.
    """
    frags = _fragmentos()
    if not frags:
        return 0
    vp, np_ = prefijo_viejo.rstrip("\\/"), prefijo_nuevo.rstrip("\\/")
    # Una letra de disco siempre en mayuscula ('g:' -> 'G:'), como la devuelve Windows.
    if len(np_) == 2 and np_[1] == ":":
        np_ = np_.upper()

    def cambiar(r):
        return np_ + r[len(vp):] if r and r.lower().startswith(vp.lower()) else r

    cambiados = 0
    for f in frags:
        r = f.get("ruta") or ""
        nueva = cambiar(r)
        if nueva != r:
            f["ruta"] = nueva
            cambiados += 1
    if cambiados:
        (CARPETA_INDICE / "fragmentos.json").write_text(
            json.dumps(frags, ensure_ascii=False), encoding="utf-8")
        for lista in (PROC_PATH, OCR_PATH):
            if lista.exists():
                try:
                    rutas = json.loads(lista.read_text(encoding="utf-8"))
                    lista.write_text(json.dumps([cambiar(r) for r in rutas], ensure_ascii=False),
                                     encoding="utf-8")
                except Exception:
                    pass
    return cambiados


def reubicar_si_se_movio():
    """Si la carpeta del asistente se copio a otra PC u otra ubicacion (por ejemplo, de
    C:\\Users\\Usuario\\Desktop\\Proyectos\\AsistenteLegal a C:\\Users\\Papa\\AsistenteLegal),
    el indice sigue apuntando a la ruta vieja y 'Abrir original' no encuentra nada.
    Detecta el prefijo viejo de lo que esta dentro de datos/ y lo corrige. Los documentos
    de discos externos no se tocan. Devuelve cuantas referencias corrigio."""
    from collections import Counter
    frags = _fragmentos()
    if not frags:
        return 0
    paso = max(1, len(frags) // 300)
    candidatos = Counter()
    for f in frags[::paso]:
        r = f.get("ruta") or ""
        i = r.replace("\\", "/").lower().find("/datos/")
        if i <= 0 or os.path.exists(r):
            continue
        if (BASE / r[i + 1:].replace("\\", "/")).exists():
            candidatos[r[:i]] += 1
    if not candidatos:
        return 0
    viejo, _ = candidatos.most_common(1)[0]
    if clave_ruta(viejo) == clave_ruta(BASE):
        return 0
    return remapear(viejo, str(BASE))
