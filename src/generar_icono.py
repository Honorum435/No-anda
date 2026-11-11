"""Genera el icono de la app (balanza sobre marino) en todos los tamanos que hacen falta:
.ico para Windows (escritorio, menu Inicio, barra de tareas) y PNG para el celular.

Uso:  python src/generar_icono.py      (deja los archivos en src/static/)
"""
from pathlib import Path

from PIL import Image, ImageDraw

DESTINO = Path(__file__).resolve().parent / "static"
MARINO, MARINO_OSCURO, CREMA, DORADO = "#1E3A8A", "#172F72", "#FAF8F3", "#D08A2E"


def _linea(d, puntos, ancho, color):
    d.line(puntos, fill=color, width=ancho, joint="curve")
    r = ancho // 2
    for x, y in (puntos[0], puntos[-1]):  # puntas redondeadas
        d.ellipse((x - r, y - r, x + r, y + r), fill=color)


def _platillo(d, x, y0, y1, ancho_medio, grosor):
    _linea(d, [(x - ancho_medio, y1), (x, y0), (x + ancho_medio, y1)], grosor, CREMA)
    alto = int(ancho_medio * 0.55)
    d.chord((x - ancho_medio - grosor // 2, y1 - alto, x + ancho_medio + grosor // 2, y1 + alto),
            0, 180, fill=CREMA)


def dibujar(lado=1024):
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Fondo: cuadrado redondeado con un leve degrade vertical.
    fondo = Image.new("RGBA", (lado, lado), MARINO)
    fd = ImageDraw.Draw(fondo)
    for y in range(lado):
        t = y / lado
        c = tuple(int(int(MARINO[i:i + 2], 16) * (1 - t * .35) + int(MARINO_OSCURO[i:i + 2], 16) * t * .35)
                  for i in (1, 3, 5))
        fd.line([(0, y), (lado, y)], fill=c)
    mascara = Image.new("L", (lado, lado), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, lado - 1, lado - 1), radius=int(lado * .22), fill=255)
    img.paste(fondo, (0, 0), mascara)

    s = lado / 1024
    g = int(52 * s)
    _linea(d, [(512 * s, 262 * s), (512 * s, 772 * s)], g, CREMA)                  # poste
    _linea(d, [(372 * s, 772 * s), (652 * s, 772 * s)], g, CREMA)                  # base
    _linea(d, [(236 * s, 352 * s), (512 * s, 300 * s), (788 * s, 352 * s)], g, CREMA)  # cruz
    _platillo(d, 300 * s, 360 * s, 590 * s, 118 * s, int(40 * s))
    _platillo(d, 724 * s, 360 * s, 590 * s, 118 * s, int(40 * s))
    r = 44 * s
    d.ellipse((512 * s - r, 262 * s - r - 30 * s, 512 * s + r, 262 * s + r - 30 * s), fill=DORADO)
    return img


if __name__ == "__main__":
    DESTINO.mkdir(exist_ok=True)
    grande = dibujar(1024)
    for tam in (512, 192, 180):
        grande.resize((tam, tam), Image.LANCZOS).save(DESTINO / f"icono-{tam}.png")
    grande.resize((256, 256), Image.LANCZOS).save(
        DESTINO / "icono.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
                                     (128, 128), (256, 256)])
    print("Iconos generados en", DESTINO)
