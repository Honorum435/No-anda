"""PIN para entrar al asistente desde el celular (o desde cualquier otro equipo de la red).

El archivo de causas es penal: nadie que este en el mismo Wi-Fi puede entrar sin el PIN.
Se guarda solo un hash con sal (PBKDF2), nunca el PIN, en datos/.pin_celular (gitignored).
"""
import hashlib
import hmac
import json
import secrets

from comun import BASE

ARCHIVO_PIN = BASE / "datos" / ".pin_celular"
ITERACIONES = 200_000
MAX_FALLOS = 5            # despues de 5 intentos fallidos...
BLOQUEO_SEGUNDOS = 300    # ...se bloquea 5 minutos


def pin_valido(pin):
    return bool(pin) and pin.isdigit() and 6 <= len(pin) <= 8


def hay_pin():
    return ARCHIVO_PIN.exists()


def guardar_pin(pin):
    if not pin_valido(pin):
        raise ValueError("El PIN tiene que tener entre 6 y 8 numeros.")
    sal = secrets.token_bytes(16)
    h = hashlib.pbkdf2_hmac("sha256", pin.encode(), sal, ITERACIONES)
    ARCHIVO_PIN.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_PIN.write_text(json.dumps({"sal": sal.hex(), "hash": h.hex(), "iter": ITERACIONES}),
                           encoding="utf-8")


def verificar_pin(pin):
    try:
        d = json.loads(ARCHIVO_PIN.read_text(encoding="utf-8"))
        h = hashlib.pbkdf2_hmac("sha256", (pin or "").encode(), bytes.fromhex(d["sal"]),
                                int(d["iter"]))
    except Exception:
        return False
    return hmac.compare_digest(h.hex(), d["hash"])


def borrar_pin():
    try:
        ARCHIVO_PIN.unlink()
    except FileNotFoundError:
        pass
