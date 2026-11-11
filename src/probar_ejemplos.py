"""Demo: corre varias consultas escritas DISTINTO a los documentos y muestra el mejor match.
Sirve para comprobar que la busqueda entiende el significado, no solo palabras exactas.
"""
from buscar import buscar

CONSULTAS = [
    "entraron a la casa sin permiso del juez",        # deberia traer el de nulidad de allanamiento
    "quiero que liberen a mi clienta que esta presa",  # deberia traer el de excarcelacion
    "paso demasiado tiempo desde el hecho",            # deberia traer el de prescripcion
]

for c in CONSULTAS:
    print(f"\n=== Consulta: \"{c}\" ===")
    for r in buscar(c, k=2):
        print(f"  [{r['score']:.3f}] {r['nombre']}")
        print(f"          {r['texto'][:130].strip()}...")
