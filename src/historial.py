"""Historial local de consultas, fichas y borradores.

Todo se guarda en datos/historial/ dentro del proyecto: nunca sale de la PC, igual que
el indice y la busqueda. Se guarda el texto tal como lo ve el usuario (con los datos
reales restaurados), asi que la carpeta es tan sensible como el archivo del estudio.

Estructura:
    datos/historial/conversaciones/<id>.json   una charla completa del chat
    datos/historial/fichas/<id>.json           una ficha-resumen de causa
    datos/historial/borradores/<id>.json       un escrito redactado
"""
import json
import time
from datetime import datetime
from pathlib import Path

from comun import BASE

RAIZ = BASE / "datos" / "historial"
CONVERSACIONES = RAIZ / "conversaciones"
FICHAS = RAIZ / "fichas"
BORRADORES = RAIZ / "borradores"

# Cuantas fuentes se guardan por respuesta (evita que el historial pese como el indice).
MAX_FUENTES = 8
RECORTE_FUENTE = 600


def _carpeta(c):
    c.mkdir(parents=True, exist_ok=True)
    return c


def nuevo_id():
    """Id ordenable por fecha, legible al mirar la carpeta."""
    return datetime.now().strftime("%Y-%m-%d_%H%M%S_") + str(int(time.time() * 1000))[-4:]


def _escribir(ruta, datos):
    """Escritura atomica: primero a un .tmp y despues rename, para que un corte
    de luz no deje un JSON a medias que despues no se pueda leer."""
    tmp = ruta.with_suffix(".tmp")
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(ruta)


def _leer(ruta):
    try:
        return json.loads(Path(ruta).read_text(encoding="utf-8"))
    except Exception:
        return None


def _fuentes_livianas(fuentes):
    """Guarda lo justo de cada fuente: de que documento salio y un extracto."""
    salida = []
    for f in (fuentes or [])[:MAX_FUENTES]:
        salida.append({
            "nombre": f.get("nombre"),
            "ruta": f.get("ruta"),
            "score": f.get("score"),
            "texto": (f.get("texto") or "")[:RECORTE_FUENTE],
        })
    return salida


def _titulo(mensajes):
    """La primera consulta del usuario sirve de titulo de la charla."""
    for m in mensajes:
        if m.get("rol") == "user" and m.get("texto"):
            t = " ".join(m["texto"].split())
            return t[:70] + ("…" if len(t) > 70 else "")
    return "(sin consultas)"


# ------------------------------- conversaciones -------------------------------

def guardar_conversacion(id_conv, mensajes):
    """Guarda (o pisa) una conversacion completa. Devuelve el id usado."""
    if not mensajes:
        return id_conv
    id_conv = id_conv or nuevo_id()
    limpios = [{
        "rol": m.get("rol"),
        "texto": m.get("texto"),
        "nota": m.get("nota", ""),
        "fuentes": _fuentes_livianas(m.get("fuentes")),
    } for m in mensajes]
    _escribir(_carpeta(CONVERSACIONES) / f"{id_conv}.json", {
        "id": id_conv,
        "titulo": _titulo(mensajes),
        "actualizada": datetime.now().isoformat(timespec="seconds"),
        "mensajes": limpios,
    })
    return id_conv


def listar_conversaciones(limite=100):
    """[(id, titulo, actualizada, n_consultas)] de la mas reciente a la mas vieja."""
    if not CONVERSACIONES.exists():
        return []
    salida = []
    for p in sorted(CONVERSACIONES.glob("*.json"), reverse=True)[:limite]:
        d = _leer(p)
        if d:
            consultas = sum(1 for m in d.get("mensajes", []) if m.get("rol") == "user")
            salida.append((d["id"], d.get("titulo", ""), d.get("actualizada", ""), consultas))
    return salida


def cargar_conversacion(id_conv):
    d = _leer(CONVERSACIONES / f"{id_conv}.json")
    return (d or {}).get("mensajes", [])


def ultima_conversacion():
    """Id de la charla mas reciente, para poder retomarla al abrir la app."""
    convs = listar_conversaciones(limite=1)
    return convs[0][0] if convs else None


# ---------------------------- fichas y borradores ----------------------------

def guardar_ficha(caso, texto, docs=None, meta=None):
    id_f = nuevo_id()
    _escribir(_carpeta(FICHAS) / f"{id_f}.json", {
        "id": id_f, "caso": caso, "texto": texto,
        "documentos": list((docs or {}).keys()),
        "meta": meta or {},
        "fecha": datetime.now().isoformat(timespec="seconds"),
    })
    return id_f


def guardar_borrador(tipo, descripcion, texto, fuentes=None, meta=None):
    id_b = nuevo_id()
    _escribir(_carpeta(BORRADORES) / f"{id_b}.json", {
        "id": id_b, "tipo": tipo, "descripcion": descripcion, "texto": texto,
        "fuentes": _fuentes_livianas(fuentes),
        "meta": meta or {},
        "fecha": datetime.now().isoformat(timespec="seconds"),
    })
    return id_b


def _listar(carpeta, campos, limite):
    if not carpeta.exists():
        return []
    salida = []
    for p in sorted(carpeta.glob("*.json"), reverse=True)[:limite]:
        d = _leer(p)
        if d:
            salida.append(tuple(d.get(c, "") for c in campos))
    return salida


def listar_fichas(limite=100):
    """[(id, caso, fecha)]"""
    return _listar(FICHAS, ("id", "caso", "fecha"), limite)


def listar_borradores(limite=100):
    """[(id, tipo, descripcion, fecha)]"""
    return _listar(BORRADORES, ("id", "tipo", "descripcion", "fecha"), limite)


def cargar_ficha(id_f):
    return _leer(FICHAS / f"{id_f}.json") or {}


def cargar_borrador(id_b):
    return _leer(BORRADORES / f"{id_b}.json") or {}


PAPELERA = RAIZ / "papelera"

_CARPETAS = {"conversacion": CONVERSACIONES, "ficha": FICHAS, "borrador": BORRADORES}


def borrar(tipo, id_item):
    """Manda un item a la papelera. tipo: 'conversacion' | 'ficha' | 'borrador'.

    No se elimina de verdad: se mueve a datos/historial/papelera/. Una ficha cuesta
    ~50 segundos y una llamada a Gemini, asi que un clic equivocado no deberia ser
    definitivo (ISO 9241-110: tolerancia a errores).
    """
    origen = _CARPETAS[tipo] / f"{id_item}.json"
    if not origen.exists():
        return False
    destino = _carpeta(PAPELERA) / f"{tipo}__{id_item}.json"
    origen.replace(destino)
    return True


def restaurar(tipo, id_item):
    """Devuelve a su lugar un item que estaba en la papelera."""
    origen = PAPELERA / f"{tipo}__{id_item}.json"
    if not origen.exists():
        return False
    origen.replace(_carpeta(_CARPETAS[tipo]) / f"{id_item}.json")
    return True


def listar_papelera():
    """[(tipo, id, titulo)] de lo borrado, para poder recuperarlo."""
    if not PAPELERA.exists():
        return []
    salida = []
    for p in sorted(PAPELERA.glob("*.json"), reverse=True):
        tipo, _, id_item = p.stem.partition("__")
        d = _leer(p) or {}
        titulo = d.get("titulo") or d.get("caso") or d.get("tipo") or id_item
        salida.append((tipo, id_item, titulo))
    return salida


def vaciar_papelera():
    """Borra definitivamente. Solo se llama cuando el usuario lo pide explicitamente."""
    n = 0
    for p in PAPELERA.glob("*.json") if PAPELERA.exists() else []:
        p.unlink()
        n += 1
    return n


def estadisticas():
    """(n_conversaciones, n_fichas, n_borradores, megas_ocupados)"""
    n = [len(list(c.glob("*.json"))) if c.exists() else 0
         for c in (CONVERSACIONES, FICHAS, BORRADORES)]
    peso = sum(p.stat().st_size for p in RAIZ.rglob("*.json")) if RAIZ.exists() else 0
    return (*n, peso / (1024 * 1024))
