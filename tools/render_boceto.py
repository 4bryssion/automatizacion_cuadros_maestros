# -*- coding: utf-8 -*-
"""Dibuja el boceto de la ventana (Tkinter) con la identidad de Areandina.
Uso: python3 -I render_boceto.py <carpeta_marca> <salida.png>
Dibuja a 3x y reduce a 2x para suavizar los bordes."""
import sys
from PIL import Image, ImageDraw, ImageFont

MARCA, SALIDA = sys.argv[1], sys.argv[2]
S = 3                      # factor de dibujo
W, H = 760, 680            # tamaño lógico de la ventana

# --- paleta del manual de marca ---
VERDE, VERDE_CTA = "#7fb536", "#67882c"
MAGENTA, NARANJA = "#e6007e", "#F59C2F"
NEGRO, GRIS, GRIS_OSC = "#000000", "#606060", "#282828"
BLANCO, LINEA, FONDO = "#FFFFFF", "#D9D9D9", "#F5F5F5"


def fuente(nombre, px):
    return ImageFont.truetype(f"{MARCA}/fuentes/BrownStd-{nombre}.otf", int(px * S))


F_B = lambda p: fuente("Bold", p)
F_R = lambda p: fuente("Regular", p)
F_L = lambda p: fuente("Light", p)

img = Image.new("RGB", (W * S, H * S), BLANCO)
d = ImageDraw.Draw(img)


def P(v):
    return int(round(v * S))


def rect(x0, y0, x1, y1, fill=None, outline=None, w=1, r=0):
    box = [P(x0), P(y0), P(x1), P(y1)]
    if r:
        d.rounded_rectangle(box, radius=P(r), fill=fill, outline=outline, width=P(w) if outline else 0)
    else:
        d.rectangle(box, fill=fill, outline=outline, width=P(w) if outline else 0)


def txt(x, y, s, f, color=NEGRO, anchor="la"):
    d.text((P(x), P(y)), s, font=f, fill=color, anchor=anchor)


def tw(s, f):
    return d.textlength(s, font=f) / S


def check(cx, cy, color=VERDE_CTA, s=7):
    d.line([P(cx - s), P(cy), P(cx - s / 3), P(cy + s * .8), P(cx + s), P(cy - s * .8)],
           fill=color, width=P(2.4), joint="curve")


def cross(cx, cy, color=MAGENTA, s=6):
    d.line([P(cx - s), P(cy - s), P(cx + s), P(cy + s)], fill=color, width=P(2.4))
    d.line([P(cx - s), P(cy + s), P(cx + s), P(cy - s)], fill=color, width=P(2.4))


def logo(nombre, alto):
    im = Image.open(f"{MARCA}/logos/1. Logotipo Institucional /{nombre}").convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    r = P(alto) / im.height
    return im.resize((int(im.width * r), P(alto)), Image.LANCZOS)


# ---------- barra de título de la ventana ----------
rect(0, 0, W, 32, fill="#EDEDED")
txt(12, 16, "Cuadro maestro internacional", F_R(11), GRIS_OSC, "lm")
for i, kind in enumerate(("min", "max", "x")):
    cx = W - 100 + i * 34 + 17
    if kind == "min":
        d.line([P(cx - 5), P(16), P(cx + 5), P(16)], fill=GRIS_OSC, width=P(1))
    elif kind == "max":
        rect(cx - 5, 11, cx + 5, 21, outline=GRIS_OSC, w=1)
    else:
        cross(cx, 16, GRIS_OSC, 5)

# ---------- encabezado con logotipo ----------
lg = logo("_LOGOS-05.png", 34)       # logotipo verde (mínimo digital del manual: 30 px)
img.paste(lg, (P(28), P(32 + 18)), lg)
txt(W - 28, 32 + 20, "Cuadro maestro internacional", F_B(20), GRIS_OSC, "ra")
txt(W - 28, 32 + 46, "Genera el cuadro de un programa según su vigencia", F_L(12), GRIS, "ra")
rect(0, 32 + 78, W, 32 + 81, fill=VERDE)          # línea de marca
Y0 = 32 + 81

# ---------- sección 1: carpeta ----------
y = Y0 + 22
txt(28, y, "1. Carpeta con los Excel", F_B(13), GRIS_OSC)
rect(28, y + 26, 590, y + 58, fill=BLANCO, outline=GRIS, w=1)
txt(40, y + 42, "C:\\Fuentes\\Movilidad_IeC", F_R(12), NEGRO, "lm")
rect(604, y + 26, W - 28, y + 58, fill=BLANCO, outline=VERDE_CTA, w=1.5)
txt((604 + W - 28) / 2, y + 42, "Buscar…", F_B(12), VERDE_CTA, "mm")

# ---------- sección 2: programa y vigencia ----------
y += 80
txt(28, y, "2. Programa", F_B(13), GRIS_OSC)
rect(28, y + 26, 380, y + 58, fill=BLANCO, outline=GRIS, w=1)
txt(40, y + 42, "Fisioterapia", F_R(12), NEGRO, "lm")
d.polygon([(P(356), P(y + 38)), (P(368), P(y + 38)), (P(362), P(y + 46))], fill=GRIS_OSC)

txt(410, y, "3. Vigencia (años completos)", F_B(13), GRIS_OSC)
for x0, etq, val in ((410, "Desde", "2019"), (586, "Hasta", "2023")):
    txt(x0, y + 26 - 1, "", F_R(10), GRIS)
    rect(x0 + 52, y + 26, x0 + 142, y + 58, fill=BLANCO, outline=GRIS, w=1)
    txt(x0, y + 42, etq, F_R(12), GRIS_OSC, "lm")
    txt(x0 + 62, y + 42, val, F_R(12), NEGRO, "lm")
    d.polygon([(P(x0 + 118), P(y + 38)), (P(x0 + 130), P(y + 38)), (P(x0 + 124), P(y + 46))], fill=GRIS_OSC)

# ---------- panel de archivos ----------
y += 82
txt(28, y, "Archivos que se usarán", F_B(13), GRIS_OSC)
badge = "14 de 15 encontrados"
bw = tw(badge, F_B(11)) + 22
rect(W - 28 - bw, y - 2, W - 28, y + 20, fill=NARANJA)
txt(W - 28 - bw / 2, y + 9, badge, F_B(11), NEGRO, "mm")

gy = y + 30
cols = [28, 150, 360, 560]                      # x de cada columna
rect(28, gy, W - 28, gy + 30, fill=GRIS_OSC)
for x, t in zip(cols, ("Año", "Movilidad (anual)", "Int. en casa · 1.º semestre", "Int. en casa · 2.º semestre")):
    txt(x + 12, gy + 15, t, F_B(11), BLANCO, "lm")
rows = [("2019", 1, 1, 1), ("2020", 1, 1, 1), ("2021", 0, 1, 1), ("2022", 1, 1, 1), ("2023", 1, 1, 1)]
for i, (anio, a, b, c) in enumerate(rows):
    ry = gy + 30 + i * 30
    rect(28, ry, W - 28, ry + 30, fill=(BLANCO if i % 2 == 0 else FONDO))
    txt(cols[0] + 12, ry + 15, anio, F_R(12), NEGRO, "lm")
    for x, ok, nom in ((cols[1], a, "Movilidad"), (cols[2], b, "IeC"), (cols[3], c, "IeC")):
        if ok:
            check(x + 22, ry + 15)
            txt(x + 38, ry + 15, "Encontrado", F_L(11), GRIS, "lm")
        else:
            cross(x + 22, ry + 15)
            txt(x + 38, ry + 15, "Falta este archivo", F_B(11), MAGENTA, "lm")
rect(28, gy, W - 28, gy + 30 + 5 * 30, outline=LINEA, w=1)

# ---------- aviso ----------
ay = gy + 30 + 5 * 30 + 14
rect(28, ay, W - 28, ay + 40, fill="#FFF3E3", outline=NARANJA, w=1)
d.ellipse([P(40), P(ay + 13), P(54), P(ay + 27)], fill=NARANJA)
txt(47, ay + 20, "!", F_B(11), NEGRO, "mm")
txt(66, ay + 20, "Falta Movilidad 2021. Puedes generar igual: quedará anotado en la hoja Revisión.", F_R(12), NEGRO, "lm")

# ---------- botones ----------
by = ay + 58
rect(28, by, 318, by + 46, fill=VERDE_CTA)
txt(173, by + 23, "Generar cuadro maestro", F_B(14), BLANCO, "mm")
rect(332, by, 478, by + 46, fill=BLANCO, outline=VERDE_CTA, w=1.5)
txt(405, by + 23, "Configuración", F_B(13), VERDE_CTA, "mm")
txt(W - 28, by + 23, "Ver revisión", F_R(12), "#9A9A9A", "rm")

# ---------- pie ----------
rect(0, H - 34, W, H, fill=FONDO)
d.line([0, P(H - 34), P(W), P(H - 34)], fill=LINEA, width=P(1))
txt(28, H - 17, "Fundación Universitaria del Área Andina", F_L(10), GRIS, "lm")
txt(W - 28, H - 17, "Boceto v0.1 · datos ficticios", F_L(10), GRIS, "rm")

# borde de ventana
rect(0, 0, W - 1, H - 1, outline="#9A9A9A", w=1)
img = img.resize((W * 2, H * 2), Image.LANCZOS)
img.save(SALIDA)
print("ok", img.size)
