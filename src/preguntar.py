"""Consulta completa: busca en el indice, anonimiza, le pide a Gemini una respuesta
citando las fuentes, y restaura los datos reales en la respuesta (local).

Uso por terminal:
    $env:GEMINI_API_KEY = "tu_clave"
    python src/preguntar.py "donde plantee nulidad de allanamiento y como lo redacte?"
"""
import os
import sys

from comun import MODELO_GEMINI, MODELO_NER, TOP_K
from buscar import buscar

PROMPT = """Sos un asistente para un abogado penalista argentino.
Responde la consulta usando UNICAMENTE la informacion de los fragmentos de casos de abajo.
- Cita siempre la fuente como [Fuente N] de donde sacaste cada cosa.
- Algunos datos personales pueden venir reemplazados por etiquetas como [PERSONA_1], [DNI_1]
  o [DOMICILIO_1]. Usalas TAL CUAL en tu respuesta, no las cambies ni inventes.
- Si la informacion no esta en los fragmentos, decilo con claridad. NO inventes datos ni jurisprudencia.

CONSULTA:
{consulta}

FRAGMENTOS DE CASOS:
{contexto}

RESPUESTA (clara y para un abogado, citando las fuentes como [Fuente N]):"""


def construir_prompt(consulta, textos):
    contexto = "\n\n".join(f"[Fuente {i + 1}]\n{t}" for i, t in enumerate(textos))
    return PROMPT.format(consulta=consulta, contexto=contexto)


def generar_respuesta(consulta, k=TOP_K, api_key=None, rerank=False, log=None):
    """Devuelve (texto, fragmentos, meta).
    - texto: respuesta redactada (None si no hay clave de Gemini).
    - fragmentos: las fuentes reales (para mostrar localmente).
    - meta: {'anonimizado': bool, 'ocultos': int, ...}.

    La anonimizacion es obligatoria y no se puede desactivar: los datos personales
    (y los apellidos de las carpetas de causas) se reemplazan por etiquetas antes de
    salir de la PC, y se vuelven a poner en la respuesta, que se ve completa.
    """
    aviso = log or (lambda m: None)
    aviso("Buscando en el archivo del estudio…")
    frags = buscar(consulta, k=k, rerank=rerank)
    aviso(f"Encontré {len(frags)} fragmento(s) relevante(s).")
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, frags, {"anonimizado": False, "ocultos": 0}

    aviso("Ocultando datos personales antes de salir a la nube…")
    from anonimizar import anonimizar_varios, restaurar
    from causas import nombres_de_clientes
    piezas, mapa = anonimizar_varios([consulta] + [f["texto"] for f in frags], MODELO_NER,
                                     nombres_de_clientes())
    consulta_env, textos_env = piezas[0], piezas[1:]

    aviso("Redactando la respuesta…")
    from nube import generar
    prompt = construir_prompt(consulta_env, textos_env)
    texto, modelo = generar(prompt, api_key, log=log)
    texto = restaurar(texto, mapa)
    return texto, frags, {"anonimizado": True, "ocultos": len(mapa), "modelo": modelo}


def responder(consulta, k=TOP_K):
    """Version para terminal."""
    texto, frags, meta = generar_respuesta(consulta, k=k)
    if texto is None:
        print("/!\\ No encontre la variable GEMINI_API_KEY.")
        print("    Fragmentos mas relevantes (busqueda local):\n")
        for i, r in enumerate(frags):
            print(f"[Fuente {i + 1}: {r['nombre']}] (similitud {r['score']:.2f})")
            print(f"    {r['texto'][:250].strip()}...\n")
        return
    if meta["anonimizado"]:
        print(f"[anonimizado: se ocultaron {meta['ocultos']} dato(s) personal(es) antes de la nube]\n")
    print(texto)
    print("\n-- Fuentes consultadas:")
    for i, r in enumerate(frags):
        print(f"  Fuente {i + 1}: {r['nombre']} (similitud {r['score']:.2f})")


if __name__ == "__main__":
    consulta = " ".join(sys.argv[1:]) or input("Tu consulta: ")
    responder(consulta)
