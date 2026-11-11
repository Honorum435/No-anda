"""Lista los modelos de Gemini disponibles para tu clave (para elegir el correcto en comun.py)."""
import os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("Falta GEMINI_API_KEY. Configurala antes de correr esto.")

from google import genai

cliente = genai.Client(api_key=api_key)
print("Modelos disponibles para tu clave:\n")
for m in cliente.models.list():
    acciones = getattr(m, "supported_actions", None) or \
        getattr(m, "supported_generation_methods", None) or ""
    print(f"  {m.name}    {acciones}")
