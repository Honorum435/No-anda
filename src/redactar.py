"""Redacta un escrito nuevo usando los escritos del estudio como modelo de estilo y estructura.

Reusa la busqueda (para traer modelos parecidos) y la anonimizacion (para no mandar datos
reales a la nube). Devuelve el borrador con los nombres restaurados localmente.
"""
import os

from comun import MODELO_GEMINI, MODELO_NER
from buscar import buscar

PROMPT = """Sos un asistente para un abogado penalista argentino.
Tu tarea es REDACTAR un escrito nuevo para el caso que se describe abajo, siguiendo el ESTILO,
la ESTRUCTURA y las FORMULAS de los escritos modelo del estudio que te paso.

Reglas:
- Imita la FORMA de los modelos (encabezado, formulas de cortesia, citas, orden de los argumentos,
  peticion final). NO copies los hechos de los modelos.
- Completa con los hechos del CASO NUEVO. Si falta un dato necesario, deja un marcador claro como
  [COMPLETAR: domicilio del imputado].
- Algunos datos personales pueden venir reemplazados por etiquetas como [PERSONA_1], [DNI_1] o
  [DOMICILIO_1]. Usalas TAL CUAL, no las cambies.
- No inventes jurisprudencia, articulos ni datos que no esten.

TIPO DE ESCRITO: {tipo}

CASO NUEVO (hechos y lo que se pide):
{descripcion}

FRAGMENTOS DE ESCRITOS MODELO DEL ESTUDIO (usalos como guia de forma):
{modelos}

Redacta el escrito completo, listo para revisar y editar:"""


def redactar(descripcion, tipo="", k=8, api_key=None, rerank=False, log=None):
    """Devuelve (borrador, fuentes, meta). borrador es None si no hay clave de Gemini.
    La anonimizacion es obligatoria (ver preguntar.generar_respuesta)."""
    aviso = log or (lambda m: None)
    consulta = (tipo + ". " + descripcion).strip()
    aviso("Buscando escritos parecidos en el archivo…")
    frags = buscar(consulta, k=k, rerank=rerank)
    aviso(f"Usando {len(frags)} escrito(s) como modelo.")

    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None, frags, {"anonimizado": False, "ocultos": 0}

    aviso("Ocultando datos personales antes de salir a la nube…")
    from anonimizar import anonimizar_varios, restaurar, neutralizar
    from causas import nombres_de_clientes
    # El tipo de escrito tambien se anonimiza: puede traer un nombre ("Excarcelacion de X").
    piezas, mapa = anonimizar_varios([descripcion, tipo or ""] + [f["texto"] for f in frags],
                                     MODELO_NER, nombres_de_clientes())
    desc_env, tipo_env, modelos_env = piezas[0], piezas[1], piezas[2:]

    modelos = "\n\n---\n\n".join(
        f"[Modelo {i + 1}]\n{t}" for i, t in enumerate(modelos_env)
    )
    prompt = PROMPT.format(
        tipo=(tipo_env or "(sin especificar)"), descripcion=desc_env, modelos=modelos
    )

    aviso("Redactando el borrador…")
    from nube import generar
    texto, modelo = generar(prompt, api_key, log=log)
    # Solo se restauran los datos que trajo QUIEN CONSULTA (descripcion y tipo). Los del
    # resto del mapa vienen de escritos de otras causas usados como modelo: restaurarlos
    # filtraria datos de otros clientes al borrador (secreto profesional).
    propios = {t: v for t, v in mapa.items() if t in desc_env or t in tipo_env}
    ajenos = len(mapa) - len(propios)
    texto = neutralizar(restaurar(texto, propios))
    return texto, frags, {"anonimizado": True, "ocultos": len(mapa),
                          "de_otras_causas": ajenos, "modelo": modelo}
