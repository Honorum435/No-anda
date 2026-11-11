"""Agrupa los fragmentos del indice por CAUSA (carpeta), a partir de la ruta del archivo.

El archivo del estudio esta organizado carpeta-por-causa bajo 'MochiPato'
(p.ej. .../MochiPato/MACHUCA/escrito.docx). Los documentos sueltos se agrupan aparte.
"""
import json
import re
import unicodedata
from collections import Counter
from functools import lru_cache

from comun import CARPETA_INDICE

SUELTOS = "(documentos sueltos)"
_ANCLAS = ("MochiPato", "drive_casos", "casos_reales")

# Palabras de nombres de carpeta que no son nombres de personas (temas, cursos, fueros).
# Tratarlas como apellido taparia texto juridico ("Codigo Penal", "Juzgado Federal").
_GENERICAS = {
    "codigo", "penal", "ppenal", "federal", "nacional", "provincial", "juzgado", "tribunal",
    "camara", "causa", "causas", "expediente", "juicio", "jurados", "jurado", "litigacion",
    "cibercrimen", "criminologia", "jurisprudencia", "doctrina", "modelos", "modelo",
    "escritos", "escrito", "varios", "otros", "curso", "cursos", "charla", "charlas",
    "estudio", "clase", "clases", "material", "documentos", "doc", "docs", "nuevo", "nueva",
    "viejo", "copia", "por", "para", "con", "del", "los", "las", "sus", "recurso",
    "recursos", "casacion", "apelacion", "nulidad", "excarcelacion", "estafa", "robo",
    "hurto", "homicidio", "drogas", "plantillas", "plantilla",
}


def _sin_tildes(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def caso_de_ruta(ruta):
    """Nombre de la causa (carpeta) a la que pertenece un documento."""
    if not ruta:
        return SUELTOS
    partes = str(ruta).replace("\\", "/").split("/")
    for ancla in _ANCLAS:
        if ancla in partes:
            resto = partes[partes.index(ancla) + 1:]
            return resto[0] if len(resto) >= 2 else SUELTOS
    return partes[-2] if len(partes) >= 2 else SUELTOS


@lru_cache(maxsize=1)
def _fragmentos():
    p = CARPETA_INDICE / "fragmentos.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def nombres_de_clientes():
    """Apellidos y nombres que salen de los nombres de las carpetas de causas.

    Las carpetas suelen llevar el apellido del cliente: es la lista mas confiable de
    nombres que nunca tienen que llegar a la nube. Se pasan a la anonimizacion para
    taparlos aunque el detector automatico (NER) no los reconozca.

    Se descartan las palabras comunes: las de _GENERICAS y las que en los propios
    escritos aparecen sobre todo en minuscula (sustantivos, no apellidos).
    """
    candidatas = {_sin_tildes(w): w
                  for c, _, _ in listar_casos()
                  for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]{3,}", c)}
    candidatas = {b: w for b, w in candidatas.items() if b not in _GENERICAS}
    if not candidatas:
        return ()
    # Una pasada por una muestra de los escritos: cuantas veces va en minuscula.
    muestra = " ".join(f.get("texto", "") for f in _fragmentos()[::5])
    minus, total = Counter(), Counter()
    for palabra, n in Counter(re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]{3,}", muestra)).items():
        base = _sin_tildes(palabra)
        if base in candidatas:
            total[base] += n
            if palabra.islower():
                minus[base] += n
    return tuple(sorted(w for b, w in candidatas.items()
                        if not (total[b] >= 5 and minus[b] >= 0.5 * total[b])))


def nombres_de_la_causa(caso):
    """Las palabras del nombre de UNA carpeta de causa que no son genericas."""
    return [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]{3,}", caso or "")
            if _sin_tildes(w) not in _GENERICAS]


def refrescar():
    """Despues de agregar o mover documentos: vuelve a leer el indice."""
    _fragmentos.cache_clear()
    nombres_de_clientes.cache_clear()


def listar_casos(solo_carpetas=True):
    """Lista [(causa, n_docs, n_fragmentos)] ordenada alfabeticamente.
    Si solo_carpetas=True excluye los documentos sueltos."""
    docs, frags = {}, {}
    for f in _fragmentos():
        c = caso_de_ruta(f.get("ruta"))
        if solo_carpetas and c == SUELTOS:
            continue
        frags[c] = frags.get(c, 0) + 1
        docs.setdefault(c, set()).add(f.get("nombre"))
    return sorted(((c, len(docs[c]), frags[c]) for c in docs), key=lambda x: x[0].lower())


def fragmentos_de_caso(caso, max_por_doc=2, max_total=30):
    """Extractos representativos de una causa: hasta max_por_doc fragmentos por documento
    (los primeros suelen traer caratula, partes y datos clave), con un tope total."""
    por_doc, seleccion = {}, []
    for f in _fragmentos():
        if caso_de_ruta(f.get("ruta")) != caso:
            continue
        nombre = f.get("nombre")
        if por_doc.get(nombre, 0) < max_por_doc:
            seleccion.append(f)
            por_doc[nombre] = por_doc.get(nombre, 0) + 1
        if len(seleccion) >= max_total:
            break
    return seleccion


def documentos_de_caso(caso):
    """Dict {nombre: ruta} de los documentos unicos de una causa (preserva el orden)."""
    vistos = {}
    for f in _fragmentos():
        if caso_de_ruta(f.get("ruta")) != caso:
            continue
        nombre = f.get("nombre")
        if nombre not in vistos:
            vistos[nombre] = f.get("ruta")
    return vistos
