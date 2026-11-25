"""Dibujos suavizados para la interfaz: esquinas redondeadas, iconos, interruptores y casillas.

Tkinter no suaviza los bordes (en Windows las líneas y los círculos del lienzo se ven pixelados) ni dibuja esquinas
redondeadas. Por eso todo lo que no es texto se dibuja con Pillow a 4 veces su tamaño y se reduce con suavizado:
queda nítido a cualquier distancia. Las imágenes se guardan en caché por tamaño y color.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageTk

from ..recursos import carpeta_recursos

SS = 4                                     # sobremuestreo


def rgb(color: str) -> tuple:
    c = color.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def mezclar(a: str, b: str, t: float) -> str:
    x, y = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x[i] + (y[i] - x[i]) * t):02X}" for i in range(3))


@lru_cache(maxsize=None)
def ruta_fuente(negrita: bool = True) -> str | None:
    nombre = "BrownStd-Bold.otf" if negrita else "BrownStd-Regular.otf"
    candidatas = [carpeta_recursos() / "marca" / "fuentes" / nombre]
    if sys.platform == "win32":
        candidatas.append(Path("C:/Windows/Fonts") / ("segoeuib.ttf" if negrita else "segoeui.ttf"))
    candidatas += [Path("/usr/share/fonts/truetype/dejavu") / ("DejaVuSans-Bold.ttf" if negrita else "DejaVuSans.ttf")]
    return next((str(p) for p in candidatas if p.is_file()), None)


@lru_cache(maxsize=None)
def fuente(px: int, negrita: bool = True):
    ruta = ruta_fuente(negrita)
    try:
        return ImageFont.truetype(ruta, px * SS) if ruta else ImageFont.load_default(px * SS)
    except Exception:   # noqa: BLE001
        return ImageFont.load_default()


def texto_centrado(d: ImageDraw.ImageDraw, cx: float, cy: float, texto: str, px: int, color, negrita=True):
    """Centra por la caja real del glifo (no por la línea base): el «?» queda en el centro del círculo."""
    f = fuente(px, negrita)
    x0, y0, x1, y1 = d.textbbox((0, 0), texto, font=f)
    d.text((cx - (x0 + x1) / 2, cy - (y0 + y1) / 2), texto, font=f, fill=color)


# ---------------------------------------------------------------- caché de imágenes por intérprete de Tk
def _cache(widget) -> dict:
    raiz = widget._root()
    if not hasattr(raiz, "_graficos"):
        raiz._graficos = {}
    return raiz._graficos


def imagen(widget, clave: tuple, ancho: int, alto: int, dibujar, fondo: str | None = None) -> ImageTk.PhotoImage:
    """Dibuja con `dibujar(draw, w, h)` en coordenadas ×SS y devuelve la imagen reducida (en caché).

    El fondo queda transparente (Tk 8.6 mezcla los bordes suavizados con el color del control): así un icono sirve
    sobre cualquier fondo, también cuando la fila cambia de color. `fondo` se acepta por compatibilidad y se ignora.
    """
    fondo = None
    cache = _cache(widget)
    clave = (clave, ancho, alto)
    if clave not in cache:
        w, h = max(1, ancho) * SS, max(1, alto) * SS
        img = Image.new("RGBA", (w, h), rgb(fondo) if fondo else (0, 0, 0, 0))
        dibujar(ImageDraw.Draw(img), w, h)
        img = img.resize((max(1, ancho), max(1, alto)), Image.LANCZOS)
        cache[clave] = ImageTk.PhotoImage(img, master=widget._root())
    return cache[clave]


def pil(ancho: int, alto: int, dibujar, fondo: str | None = None) -> Image.Image:
    """Lo mismo que `imagen` pero devuelve la imagen de Pillow (para los estilos de ttk y el icono)."""
    w, h = max(1, ancho) * SS, max(1, alto) * SS
    img = Image.new("RGBA", (w, h), rgb(fondo) if fondo else (0, 0, 0, 0))
    dibujar(ImageDraw.Draw(img), w, h)
    return img.resize((max(1, ancho), max(1, alto)), Image.LANCZOS)


# ---------------------------------------------------------------- formas
def rectangulo(ancho, alto, radio, relleno, borde=None, grosor=0, exterior=None, esquinas=(True, True, True, True)):
    """Rectángulo redondeado. `exterior` pinta lo de fuera de las esquinas (el color de la ventana de atrás)."""
    def dibujar(d, w, h):
        g = grosor * SS
        r = radio * SS
        if borde and grosor:
            d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=rgb(borde), corners=esquinas)
            d.rounded_rectangle((g, g, w - 1 - g, h - 1 - g), max(0, r - g), fill=rgb(relleno), corners=esquinas)
        else:
            d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=rgb(relleno), corners=esquinas)
    return dibujar


def _con_exterior(dibujar, exterior):
    if not exterior:
        return dibujar

    def todo(d, w, h):
        d.rectangle((0, 0, w, h), fill=rgb(exterior))
        dibujar(d, w, h)
    return todo


def caja_pil(ancho, alto, radio, relleno, borde=None, grosor=0, exterior=None, esquinas=(True, True, True, True),
             banda=None):
    """`banda` = (color, ancho): franja de color en el borde izquierdo, dentro de la forma (tarjetas de cifras y
    avisos)."""
    base = rectangulo(ancho, alto, radio, relleno, borde, grosor, esquinas=esquinas)
    if banda:
        def dibujar(d, w, h):
            base(d, w, h)
            mascara = Image.new("L", (w, h), 0)
            ImageDraw.Draw(mascara).rounded_rectangle((0, 0, w - 1, h - 1), radio * SS, fill=255, corners=esquinas)
            capa = Image.new("RGBA", (w, h), rgb(banda[0]))
            recorte = Image.new("L", (w, h), 0)
            ImageDraw.Draw(recorte).rectangle((0, 0, banda[1] * SS, h), fill=255)
            from PIL import ImageChops
            d._image.paste(capa, (0, 0), ImageChops.multiply(mascara, recorte))
        base_final = dibujar
    else:
        base_final = base
    return pil(ancho, alto, _con_exterior(base_final, exterior))


def caja(widget, ancho, alto, radio, relleno, borde=None, grosor=0, exterior=None):
    return imagen(widget, ("caja", radio, relleno, borde, grosor, exterior), ancho, alto,
                  _con_exterior(rectangulo(ancho, alto, radio, relleno, borde, grosor), exterior))


# ---------------------------------------------------------------- iconos
COLOR = {"ok": "#67882C", "info": "#67882C", "aviso": "#F59C2F", "error": "#E6007E", "mal": "#E6007E",
         "gris": "#9A9A9A", "pendiente": "#9A9A9A", "curso": "#67882C"}


def simbolo(widget, tipo: str, d: int, fondo: str | None = None, relleno=True):
    """✓ · ✗ · ! · i · ○ · ◔, dibujados (no son letras: se ven igual con cualquier tipografía)."""
    color = rgb(COLOR[tipo])

    def dibujar(dr, w, h):
        lw = max(2, round(w / 9))
        if tipo == "mal" or (tipo == "ok" and not relleno):
            if tipo == "mal":
                m = w * 0.22
                dr.line((m, m, w - m, h - m), fill=color, width=lw + SS // 2)
                dr.line((m, h - m, w - m, m), fill=color, width=lw + SS // 2)
                for x, y in ((m, m), (w - m, h - m), (m, h - m), (w - m, m)):
                    r = (lw + SS // 2) / 2
                    dr.ellipse((x - r, y - r, x + r, y + r), fill=color)
            else:
                pts = [(w * .16, h * .53), (w * .40, h * .77), (w * .86, h * .25)]
                dr.line(pts, fill=color, width=lw + SS // 2, joint="curve")
                for x, y in (pts[0], pts[-1]):
                    r = (lw + SS // 2) / 2
                    dr.ellipse((x - r, y - r, x + r, y + r), fill=color)
            return
        if tipo == "pendiente":
            dr.ellipse((lw, lw, w - lw, h - lw), outline=color, width=lw)
            return
        if tipo == "curso":
            dr.ellipse((lw, lw, w - lw, h - lw), outline=rgb("#DADADA"), width=lw)
            dr.arc((lw, lw, w - lw, h - lw), start=-90, end=160, fill=color, width=lw)
            return
        dr.ellipse((0, 0, w - 1, h - 1), fill=color)
        blanco = (255, 255, 255, 255)
        if tipo == "ok":
            dr.line([(w * .27, h * .52), (w * .44, h * .69), (w * .74, h * .34)], fill=blanco, width=lw, joint="curve")
        elif tipo in ("aviso", "error"):
            dr.rounded_rectangle((w * .44, h * .2, w * .56, h * .6), w * .06, fill=blanco)
            dr.ellipse((w * .43, h * .67, w * .57, h * .81), fill=blanco)
        else:
            dr.ellipse((w * .43, h * .19, w * .57, h * .33), fill=blanco)
            dr.rounded_rectangle((w * .44, h * .4, w * .56, h * .8), w * .06, fill=blanco)
    return imagen(widget, ("simbolo", tipo, relleno), d, d, dibujar, fondo)


def ayuda(widget, d: int, lleno: bool, fondo: str):
    verde = rgb("#67882C")

    def dibujar(dr, w, h):
        lw = round(w * 0.075)
        if lleno:
            dr.ellipse((0, 0, w - 1, h - 1), fill=verde)
        else:
            dr.ellipse((lw / 2, lw / 2, w - 1 - lw / 2, h - 1 - lw / 2), outline=verde, width=lw)
        texto_centrado(dr, w / 2, h / 2, "?", round(d * 0.58), (255, 255, 255, 255) if lleno else verde)
    return imagen(widget, ("ayuda", lleno), d, d, dibujar, fondo)


def numero(widget, n, d: int, color: str, fondo: str):
    def dibujar(dr, w, h):
        dr.ellipse((0, 0, w - 1, h - 1), fill=rgb(color))
        texto_centrado(dr, w / 2, h / 2, str(n), round(d * 0.5), (255, 255, 255, 255))
    return imagen(widget, ("numero", str(n), color), d, d, dibujar, fondo)


def punto(widget, color: str, d: int, fondo: str):
    return imagen(widget, ("punto", color), d, d, lambda dr, w, h: dr.ellipse((0, 0, w - 1, h - 1), fill=rgb(color)),
                  fondo)


def lapiz(widget, d: int, color: str, fondo: str):
    """Lápiz inclinado con la punta abajo a la izquierda (mockup 14): mina, punta de madera, cuerpo, abrazadera y
    borrador, separados por cortes finos."""
    def dibujar(dr, w, h):
        s = w / 24
        L = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g = ImageDraw.Draw(L)
        c = rgb(color)
        nada = (0, 0, 0, 0)
        cy, t = h / 2, 2.9 * s                       # media altura del cuerpo
        x0, x1 = 1.2 * s, 22.8 * s                   # de la punta al borrador
        g.polygon([(x0, cy), (x0 + 6 * s, cy - t), (x0 + 6 * s, cy + t)], fill=c)            # punta (madera + mina)
        g.rectangle((x0 + 6 * s, cy - t, x1 - 5.2 * s, cy + t), fill=c)                       # cuerpo
        g.rectangle((x1 - 4.6 * s, cy - t, x1 - 2.6 * s, cy + t), fill=c)                     # abrazadera
        g.rounded_rectangle((x1 - 2.2 * s, cy - t, x1, cy + t), 1.3 * s, fill=c)              # borrador
        g.line((x0 + 2.3 * s, cy - 1.6 * s, x0 + 2.3 * s, cy + 1.6 * s), fill=nada, width=round(.7 * s))  # mina
        g.line((x0 + 6 * s, cy - t, x0 + 6 * s, cy + t), fill=nada, width=round(.6 * s))      # fin de la madera
        L = L.rotate(45, resample=Image.BICUBIC, center=(w / 2, h / 2))
        dr._image.alpha_composite(L)
    return imagen(widget, ("lapiz2", color), d, d, dibujar, fondo)


def papelera(widget, d: int, color: str, fondo: str):
    def dibujar(dr, w, h):
        s, c = w / 24, rgb(color)
        lw = round(1.7 * s)
        dr.rounded_rectangle((9.5 * s, 3.5 * s, 14.5 * s, 6.5 * s), 1 * s, outline=c, width=lw)        # asa
        dr.rounded_rectangle((4.5 * s, 5.8 * s, 19.5 * s, 7.8 * s), 1 * s, fill=c)                      # tapa
        dr.rounded_rectangle((6.3 * s, 8.8 * s, 17.7 * s, 20.5 * s), 2 * s, outline=c, width=lw)       # cuerpo
        for x in (9.8, 12, 14.2):
            dr.rounded_rectangle(((x - .45) * s, 11.3 * s, (x + .45) * s, 17.8 * s), .45 * s, fill=c)
    return imagen(widget, ("papelera", color), d, d, dibujar, fondo)


def candado(widget, d: int, color: str, fondo: str):
    def dibujar(dr, w, h):
        s, c = w / 24, rgb(color)
        dr.arc((7.3 * s, 3 * s, 16.7 * s, 13.5 * s), start=180, end=360, fill=c, width=round(2 * s))
        dr.line((7.3 * s + s, 8.2 * s, 7.3 * s + s, 11 * s), fill=c, width=round(2 * s))
        dr.line((16.7 * s - s, 8.2 * s, 16.7 * s - s, 11 * s), fill=c, width=round(2 * s))
        dr.rounded_rectangle((5 * s, 10.5 * s, 19 * s, 21 * s), 2.2 * s, fill=c)
        dr.ellipse((10.6 * s, 13.6 * s, 13.4 * s, 16.4 * s), fill=(0, 0, 0, 0))                  # cerradura
        dr.rounded_rectangle((11.4 * s, 15.6 * s, 12.6 * s, 18.4 * s), .6 * s, fill=(0, 0, 0, 0))
    return imagen(widget, ("candado", color), d, d, dibujar, fondo)


def flecha(widget, ancho: int, alto: int, color: str, fondo: str):
    def dibujar(dr, w, h):
        c, lw = rgb(color), round(h * 0.13)
        dr.line((lw, h / 2, w - lw * 2.2, h / 2), fill=c, width=lw)
        dr.polygon([(w - lw * 3.2, h * .18), (w - 1, h / 2), (w - lw * 3.2, h * .82)], fill=c)
    return imagen(widget, ("flecha", color), ancho, alto, dibujar, fondo)


def triangulo(ancho: int, alto: int, color: str, fondo: str | None = None) -> Image.Image:
    def dibujar(dr, w, h):
        dr.polygon([(w * .2, h * .32), (w * .8, h * .32), (w * .5, h * .72)], fill=rgb(color))
    return pil(ancho, alto, dibujar, fondo)


def asa(widget, fondo: str):
    def dibujar(dr, w, h):
        r = w * 0.11
        for x in (w * .32, w * .68):
            for y in (h * .25, h * .5, h * .75):
                dr.ellipse((x - r, y - r, x + r, y + r), fill=rgb("#A8A8A8"))
    return imagen(widget, ("asa",), 18, 26, dibujar, fondo)


def interruptor(widget, encendido: bool, activo: bool, fondo: str, ancho=52, alto=28):
    def dibujar(dr, w, h):
        color = ("#67882C" if encendido else "#BDBDBD") if activo else "#D9D9D9"
        dr.rounded_rectangle((0, 0, w - 1, h - 1), h / 2, fill=rgb(color))
        m = h * 0.12
        x = w - h + m if encendido else m
        dr.ellipse((x + SS * .5, m + SS * .8, x + h - 2 * m + SS * .5, h - m + SS * .8), fill=(0, 0, 0, 40))  # sombra
        dr.ellipse((x, m, x + h - 2 * m, h - m), fill=(255, 255, 255, 255))
    return imagen(widget, ("interruptor", encendido, activo), ancho, alto, dibujar, fondo)


def casilla(widget, marcada: bool, fondo: str, d=22):
    def dibujar(dr, w, h):
        if marcada:
            dr.rounded_rectangle((0, 0, w - 1, h - 1), w * .2, fill=rgb("#67882C"))
            dr.line([(w * .25, h * .53), (w * .43, h * .71), (w * .76, h * .31)], fill=(255, 255, 255, 255),
                    width=round(w * .12), joint="curve")
        else:
            dr.rounded_rectangle((0, 0, w - 1, h - 1), w * .2, fill=rgb("#606060"))
            g = w * .09
            dr.rounded_rectangle((g, g, w - 1 - g, h - 1 - g), w * .14, fill=(255, 255, 255, 255))
    return imagen(widget, ("casilla", marcada), d, d, dibujar, fondo)


def radio(widget, elegido: bool, fondo: str, d=22):
    def dibujar(dr, w, h):
        color = rgb("#67882C" if elegido else "#606060")
        g = w * .09
        dr.ellipse((0, 0, w - 1, h - 1), fill=color)
        dr.ellipse((g, g, w - 1 - g, h - 1 - g), fill=(255, 255, 255, 255))
        if elegido:
            m = w * .26
            dr.ellipse((m, m, w - 1 - m, h - 1 - m), fill=color)
    return imagen(widget, ("radio", elegido), d, d, dibujar, fondo)


def icono_programa() -> Image.Image | None:
    """La «A» del logotipo en un cuadrado blanco redondeado (icono de la ventana)."""
    logo = carpeta_recursos() / "marca" / "logotipo_verde.png"
    if not logo.is_file():
        return None
    img = Image.open(logo).convert("RGBA")
    w, h = img.size
    a = img.crop((round(w * 0.105), round(h * 0.335), round(w * 0.198), round(h * 0.548)))
    lado = round(max(a.size) * 1.3)
    fondo = Image.new("RGBA", (lado, lado), (255, 255, 255, 255))
    fondo.alpha_composite(a, ((lado - a.width) // 2, (lado - a.height) // 2))
    return fondo

