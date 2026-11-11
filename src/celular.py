"""Acceso desde el celular: un segundo servidor que escucha en la red local y pide PIN.

La app de escritorio escucha solo en esta PC (127.0.0.1). Para usarla desde el celular
se levanta otra copia en el puerto PUERTO_CELULAR, abierta al Wi-Fi de la casa u oficina,
que SIEMPRE pide el PIN (ver seguridad.py) y no permite tocar el archivo ni la
configuracion delicada. Si datos/.celular_activo existe, abrir.ps1 la levanta sola al
abrir el asistente.
"""
import io
import os
import socket
import subprocess
import sys
import time

from comun import BASE, PUERTO_CELULAR

MARCA = BASE / "datos" / ".celular_activo"
ARCHIVO_PID = BASE / "datos" / ".celular.pid"
_SIN_VENTANA = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def ip_local():
    """IP de esta PC en la red local (la que tiene que escribir el celular)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))  # no envia nada: solo elige la interfaz
            return s.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())


def url():
    return f"http://{ip_local()}:{PUERTO_CELULAR}"


def activo():
    try:
        with socket.create_connection(("127.0.0.1", PUERTO_CELULAR), timeout=0.5):
            return True
    except OSError:
        return False


def iniciar(espera=25):
    """Levanta el servidor del celular (sin ventana). Devuelve True si quedo andando."""
    MARCA.parent.mkdir(parents=True, exist_ok=True)
    MARCA.touch()
    if activo():
        return True
    p = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(BASE / "src" / "app.py"),
         "--server.port", str(PUERTO_CELULAR), "--server.address", "0.0.0.0",
         "--server.headless", "true", "--browser.gatherUsageStats", "false",
         "--", "--celular"],
        cwd=str(BASE), creationflags=_SIN_VENTANA,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    ARCHIVO_PID.write_text(str(p.pid), encoding="utf-8")
    fin = time.time() + espera
    while time.time() < fin:
        if activo():
            return True
        time.sleep(0.5)
    return activo()


def detener():
    """Apaga el servidor del celular y deja de levantarlo al abrir el asistente."""
    for f in (MARCA,):
        try:
            f.unlink()
        except FileNotFoundError:
            pass
    try:
        pid = int(ARCHIVO_PID.read_text(encoding="utf-8"))
    except Exception:
        pid = None
    if os.name == "nt":
        if pid:
            # /T: tambien el proceso hijo (el python.exe del entorno lanza otro python).
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                           creationflags=_SIN_VENTANA)
        if activo():
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine "
                            "-like '*streamlit*--celular*' } | ForEach-Object { "
                            "Stop-Process -Id $_.ProcessId -Force }"],
                           capture_output=True, creationflags=_SIN_VENTANA)
    try:
        ARCHIVO_PID.unlink()
    except FileNotFoundError:
        pass
    return not activo()


def qr_png(texto, escala=8):
    """Codigo QR (PNG) para abrir la direccion con la camara del celular."""
    import segno
    buf = io.BytesIO()
    segno.make(texto, error="m").save(buf, kind="png", scale=escala, border=2,
                                      dark="#0F172A", light="#FFFFFF")
    return buf.getvalue()
