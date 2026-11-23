# -*- coding: utf-8 -*-
"""Boceto v8 (identidad Areandina): Campos, Fuentes, Equivalencias y Tipos de persona.
Uso: python3 -I boceto_v8.py <carpeta_marca> <carpeta_salida>"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MARCA, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
S = 3

# ---------- paleta (manual de marca) y estados derivados ----------
VERDE, VERDE_CTA = "#7fb536", "#67882c"
MAGENTA, NARANJA = "#e6007e", "#F59C2F"
NEGRO, GRIS, GRIS_OSC = "#000000", "#606060", "#282828"
BLANCO, LINEA, FONDO = "#FFFFFF", "#D9D9D9", "#F5F5F5"
HOVER_CTA, PRESS_CTA = "#587425", "#4A6320"     # CTA al 85 % y 72 % de luminosidad
TINTE_VERDE, AVISO_BG, OK_BG = "#EAF2DD", "#FFF3E3", "#EEF5E3"
OFICINA = "Oficina de Relaciones Internacionales"


def fuente(nombre, px):
    return ImageFont.truetype(f"{MARCA}/fuentes/BrownStd-{nombre}.otf", max(1, int(round(px * S))))


def logo(nombre, alto):
    im = Image.open(f"{MARCA}/logos/1. Logotipo Institucional /{nombre}").convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    r = int(alto * S) / im.height
    return im.resize((int(im.width * r), int(alto * S)), Image.LANCZOS)


# ---------- textos de ayuda (se usan en el boceto, en la imagen y en el .md) ----------
def R(t): return (t, False)
def B(t): return (t, True)


AYUDAS = {
    "carpeta": {
        "titulo": "Carpeta con los Excel",
        "bloques": [
            ("p", [R("Reúne en "), B("una sola carpeta"), R(" todos los Excel que usará el programa: el de convenios y, "
                    "por cada año de la vigencia, el de movilidad y los dos de internacionalización en casa.")]),
            ("p", [B("Por qué: "), R("el programa lee la carpeta completa y elige solo los archivos del rango que pidas. "
                    "Si están repartidos en varias carpetas no los encuentra y tendrías que buscarlos uno por uno.")]),
            ("p", [B("Cómo nombrarlos "), R("(propuesta; se ajusta en Configuración):")]),
            ("chips", ["Convenios.xlsx", "Movilidad_2021.xlsx", "IntCasa_2021-1.xlsx", "IntCasa_2021-2.xlsx"]),
            ("p", [R("El "), B("año debe ir en el nombre"), R(": de ahí lo lee el programa.")]),
            ("h", "Para evitar errores"),
            ("b", [R("Cierra los Excel antes de generar.")]),
            ("b", [R("Un solo archivo por año y tipo: sin “copia”, “(1)” ni “final2”.")]),
            ("b", [R("Formato .xlsx y sin contraseña.")]),
            ("b", [R("Si la carpeta está en OneDrive o Drive, que los archivos estén descargados en el equipo.")]),
            ("b", [R("Evita símbolos como # % & en los nombres y rutas muy largas.")]),
        ],
    },
    "vigencia": {
        "titulo": "Vigencia (años completos)",
        "bloques": [
            ("p", [R("La vigencia se pide en "), B("años completos"), R(": del año inicial al año final, "),
                   B("ambos incluidos"), R(". De 2019 a 2023 son 5 años.")]),
            ("p", [R("Cada año aporta 3 archivos: la movilidad anual y los dos semestres de internacionalización en casa. "
                     "Por eso "), B("no se aceptan rangos a mitad de año"), R(", ni fechas con día o mes, ni un solo semestre.")]),
            ("p", [R("Si el programa te entrega fechas con mes o día, confirma con la oficina qué años corresponden "
                     "antes de generar.")]),
            ("p", [R("“Desde” no puede ser mayor que “Hasta”. No hay límite de años: de 2019 a 2026 son 8 años y 24 archivos.")]),
        ],
    },
    "config": {
        "titulo": "Configuración",
        "bloques": [
            ("p", [R("Define "), B("cómo lee el programa cada Excel"), R(": columnas, filtros y reglas de cruce. "
                     "Cámbiala solo si los Excel cambiaron de formato.")]),
            ("p", [R("Dentro encontrarás el detalle de cada opción y una guía para editarla.")]),
        ],
    },
    "revision": {
        "titulo": "Ver revisión",
        "bloques": [
            ("p", [R("Informe de lo que el programa "), B("no pudo cruzar o dejó dudoso"), R(" al generar el cuadro. "
                     "Se activa después de generar.")]),
            ("p", [R("Dentro encontrarás el detalle de cada aviso y cómo resolverlo.")]),
        ],
    },
    "archivos": {
        "titulo": "Archivos que se usarán",
        "bloques": [
            ("p", [R("Es la lista de comprobación antes de generar. Cada "), B("fila"), R(" es un año de la vigencia y cada "),
                   B("columna"), R(" es un archivo que el programa necesita:")]),
            ("b", [B("Movilidad (anual): "), R("movilidad entrante y saliente de personas de todo el año.")]),
            ("b", [B("Int. en casa · 1.º y 2.º semestre: "), R("internacionalización en casa, un archivo por semestre.")]),
            ("p", [B("Para qué sirve: "), R("con estos archivos el programa cuenta cuántas personas, y de qué tipo, "
                     "pertenecen a cada convenio del programa durante su vigencia.")]),
            ("h", "Qué significa cada marca"),
            ("ok", [B("Encontrado: "), R("el archivo está en la carpeta y se puede leer.")]),
            ("mal", [B("Falta este archivo: "), R("no se encontró o no se pudo abrir. Ese año quedará incompleto en el conteo.")]),
            ("p", [B("“14 de 15 encontrados”: "), R("archivos hallados sobre los esperados. Naranja = faltan; verde = completo.")]),
            ("p", [R("Puedes generar igual con archivos faltantes; lo que falte quedará anotado en la revisión.")]),
        ],
    },
}


# ---------- lienzo ----------
class Lienzo:
    def __init__(self, W, H, fondo=BLANCO):
        self.W, self.H = W, H
        self.img = Image.new("RGB", (int(W * S), int(H * S)), fondo)
        self.d = ImageDraw.Draw(self.img)

    @staticmethod
    def P(v):
        return int(round(v * S))

    def rect(self, x0, y0, x1, y1, fill=None, line=None, w=1, r=0, corners=None):
        P = self.P
        box = [P(x0), P(y0), P(x1), P(y1)]
        if r:
            self.d.rounded_rectangle(box, radius=P(r), fill=fill, outline=line,
                                     width=P(w) if line else 0, corners=corners)
        else:
            self.d.rectangle(box, fill=fill, outline=line, width=P(w) if line else 0)

    def txt(self, x, y, s, f, color=NEGRO, anchor="la"):
        self.d.text((self.P(x), self.P(y)), s, font=f, fill=color, anchor=anchor)

    def tw(self, s, f):
        return self.d.textlength(s, font=f) / S

    def check(self, cx, cy, color=VERDE_CTA, s=7):
        P = self.P
        self.d.line([P(cx - s), P(cy), P(cx - s / 3), P(cy + s * .8), P(cx + s), P(cy - s * .8)],
                    fill=color, width=P(2.4), joint="curve")

    def cross(self, cx, cy, color=MAGENTA, s=6, w=2.4):
        P = self.P
        self.d.line([P(cx - s), P(cy - s), P(cx + s), P(cy + s)], fill=color, width=P(w))
        self.d.line([P(cx - s), P(cy + s), P(cx + s), P(cy - s)], fill=color, width=P(w))

    def flecha(self, cx, cy, color=GRIS_OSC):
        P = self.P
        self.d.polygon([(P(cx - 6), P(cy - 3)), (P(cx + 6), P(cy - 3)), (P(cx), P(cy + 4))], fill=color)

    def pegar(self, im, x, y):
        self.img.paste(im, (self.P(x), self.P(y)), im if im.mode == "RGBA" else None)


# ---------- componentes ----------
def boton_primario(L, x0, y0, x1, y1, texto, estado="normal"):
    col = {"normal": VERDE_CTA, "hover": HOVER_CTA, "press": PRESS_CTA}[estado]
    L.rect(x0, y0, x1, y1, fill=col, r=8)
    L.txt((x0 + x1) / 2, (y0 + y1) / 2, texto, fuente("Bold", 14), BLANCO, "mm")


def boton_secundario(L, x0, y0, x1, y1, texto, estado="normal", size=13):
    fill = TINTE_VERDE if estado == "hover" else BLANCO
    L.rect(x0, y0, x1, y1, fill=fill, line=VERDE_CTA, w=1.5, r=8)
    L.txt((x0 + x1) / 2, (y0 + y1) / 2, texto, fuente("Bold", size), VERDE_CTA, "mm")


def campo(L, x0, y0, x1, y1, texto, flecha=False, foco=False):
    L.rect(x0, y0, x1, y1, fill=BLANCO, line=(VERDE_CTA if foco else GRIS), w=(2 if foco else 1), r=6)
    L.txt(x0 + 12, (y0 + y1) / 2, texto, fuente("Regular", 12), NEGRO, "lm")
    if flecha:
        L.flecha(x1 - 18, (y0 + y1) / 2)


def icono_ayuda(L, x, y, hover=False):
    """Círculo con '?' centrado verticalmente en y; x = borde izquierdo."""
    cx, cy, r = x + 10, y, 10
    P = L.P
    if hover:
        L.d.ellipse([P(cx - r), P(cy - r), P(cx + r), P(cy + r)], fill=VERDE_CTA)
        L.txt(cx, cy, "?", fuente("Bold", 12), BLANCO, "mm")
    else:
        L.d.ellipse([P(cx - r), P(cy - r), P(cx + r), P(cy + r)], fill=BLANCO, outline=VERDE_CTA, width=P(1.6))
        L.txt(cx, cy, "?", fuente("Bold", 12), VERDE_CTA, "mm")
    return x + 2 * r


def etiqueta_con_ayuda(L, x, y, texto, hover=False):
    f = fuente("Bold", 13)
    L.txt(x, y, texto, f, GRIS_OSC, "lm")
    return icono_ayuda(L, x + L.tw(texto, f) + 8, y, hover)


# ---------- tarjeta de ayuda (popover) ----------
def partir(L, segs, f_r, f_b, ancho):
    """Reparte segmentos (texto, negrita) en líneas de palabras con su fuente."""
    import re
    tokens, pend = [], False          # (palabra, negrita, hay_espacio_antes)
    for t, neg in segs:
        for m in re.finditer(r"\s+|\S+", t):
            s = m.group(0)
            if s.isspace():
                pend = True
            else:
                tokens.append((s, neg, pend and bool(tokens)))
                pend = False
    lineas, actual, wlin = [], [], 0
    esp = L.tw(" ", f_r)
    for s, neg, sp in tokens:
        f = f_b if neg else f_r
        ancho_w = L.tw(s, f)
        extra = esp if (sp and actual) else 0
        if actual and wlin + extra + ancho_w > ancho:
            lineas.append(actual)
            actual, wlin, extra, sp = [], 0, 0, False
        wlin += extra + ancho_w
        actual.append((s, neg, bool(sp and actual)))
    if actual:
        lineas.append(actual)
    return lineas


def tarjeta(ayuda, ancho=430):
    """Devuelve una imagen RGBA (con sombra) de la tarjeta de ayuda."""
    tmp = Lienzo(10, 10)
    f_r, f_b, f_h, f_t, f_c = fuente("Regular", 11.5), fuente("Bold", 11.5), fuente("Bold", 12), fuente("Bold", 14), fuente("Regular", 10.5)
    pad, lh, inner = 18, 17.5, ancho - 36
    cmds, y = [], pad
    cmds.append(("titulo", ayuda["titulo"], y)); y += 28
    for tipo, dato in ayuda["bloques"]:
        if tipo == "h":
            y += 4; cmds.append(("h", dato, y)); y += 22
        elif tipo == "chips":
            x, fila = 0, y
            chips = []
            for c in dato:
                w = tmp.tw(c, f_c) + 18
                if x + w > inner:
                    x, fila = 0, fila + 26
                chips.append((c, x, fila, w)); x += w + 8
            cmds.append(("chips", chips, y)); y = fila + 28
        else:
            sangria = 16 if tipo in ("b", "ok", "mal") else 0
            lineas = partir(tmp, dato, f_r, f_b, inner - sangria)
            cmds.append((tipo, lineas, y)); y += len(lineas) * lh + 7
    alto = y + pad - 2
    marg = 14
    base = Lienzo(ancho + 2 * marg, alto + 2 * marg, fondo=BLANCO)
    sombra = Image.new("L", base.img.size, 0)
    sd = ImageDraw.Draw(sombra)
    sd.rounded_rectangle([marg * S, (marg + 4) * S, (marg + ancho) * S, (marg + alto + 4) * S], radius=12 * S, fill=70)
    sombra = sombra.filter(ImageFilter.GaussianBlur(7 * S))
    L = base
    L.rect(marg, marg, marg + ancho, marg + alto, fill=BLANCO, line=VERDE, w=1.5, r=12)
    for cmd in cmds:
        tipo, dato, y0 = cmd
        X, Y = marg + pad, marg + y0
        if tipo == "titulo":
            L.txt(X, Y + 8, dato, f_t, GRIS_OSC, "lm")
            L.rect(X, Y + 22, X + 46, Y + 24.5, fill=VERDE)
        elif tipo == "h":
            L.txt(X, Y + 8, dato, f_h, VERDE_CTA, "lm")
        elif tipo == "chips":
            for c, cx, cy, w in dato:
                L.rect(X + cx, marg + cy, X + cx + w, marg + cy + 22, fill=FONDO, line=LINEA, w=1, r=6)
                L.txt(X + cx + w / 2, marg + cy + 11, c, f_c, GRIS_OSC, "mm")
        else:
            sang = 16 if tipo in ("b", "ok", "mal") else 0
            if tipo == "b":
                L.d.ellipse([L.P(X + 3), L.P(Y + 6), L.P(X + 8), L.P(Y + 11)], fill=VERDE_CTA)
            elif tipo == "ok":
                L.check(X + 5, Y + 8, VERDE_CTA, 5)
            elif tipo == "mal":
                L.cross(X + 5, Y + 8, MAGENTA, 4.2, 2)
            for i, linea in enumerate(dato):
                cx = X + sang
                for w, neg, sp in linea:
                    f = f_b if neg else f_r
                    if sp:
                        cx += L.tw(" ", f_r)
                    L.txt(cx, Y + 8 + i * lh, w, f, NEGRO, "lm")
                    cx += L.tw(w, f)
    mascara = Image.new("L", L.img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle([marg * S, marg * S, (marg + ancho) * S, (marg + alto) * S],
                                              radius=12 * S, fill=255)
    return {"rgb": L.img, "mascara": mascara, "sombra": sombra}


def poner(dest, t, x, y):
    """Pega la tarjeta (sombra suave + tarjeta con esquinas redondeadas) en dest, en px lógicos."""
    pos = (int(x * S), int(y * S))
    dest.paste(Image.new("RGB", t["rgb"].size, "#000000"), pos, t["sombra"])
    dest.paste(t["rgb"], pos, t["mascara"])


# ---------- ventana completa ----------
def ventana(W, H=None, popover=None, hover=None, estrecha=False):
    """H=None: la altura se ajusta al contenido (ventana mínima necesaria)."""
    L = Lienzo(W, H or 1300)
    M = 20 if estrecha else 28
    # barra de título (la dibuja Windows)
    L.rect(0, 0, W, 32, fill="#EDEDED")
    L.txt(12, 16, "Cuadro maestro internacional", fuente("Regular", 11), GRIS_OSC, "lm")
    for i, k in enumerate(("min", "max", "x")):
        cx = W - 100 + i * 34 + 17
        if k == "min":
            L.d.line([L.P(cx - 5), L.P(16), L.P(cx + 5), L.P(16)], fill=GRIS_OSC, width=L.P(1))
        elif k == "max":
            L.rect(cx - 5, 11, cx + 5, 21, line=GRIS_OSC, w=1)
        else:
            L.cross(cx, 16, GRIS_OSC, 5, 1.2)
    # encabezado
    lg = logo("_LOGOS-05.png", 34)
    L.pegar(lg, M, 32 + 18)
    L.txt(W - M, 32 + 22, "Cuadro maestro internacional", fuente("Bold", 20), GRIS_OSC, "ra")
    L.txt(W - M, 32 + 48, OFICINA, fuente("Light", 12), GRIS, "ra")
    L.rect(0, 32 + 78, W, 32 + 81, fill=VERDE)
    y = 32 + 81 + 22

    # 1. carpeta
    etiqueta_con_ayuda(L, M, y + 8, "1. Carpeta con los Excel", hover=(popover == "carpeta"))
    bw = 110
    campo(L, M, y + 26, W - M - bw - 14, y + 58, "C:\\Fuentes\\Movilidad_IeC", foco=False)
    est = "hover" if hover == "buscar" else "normal"
    boton_secundario(L, W - M - bw, y + 26, W - M, y + 58, "Buscar…", est, 12)
    y += 80

    # 2 y 3. programa y vigencia
    if not estrecha:
        pw = int((W - 2 * M) * 0.46)
        L.txt(M, y + 8, "2. Programa", fuente("Bold", 13), GRIS_OSC, "lm")
        campo(L, M, y + 26, M + pw, y + 58, "Fisioterapia", flecha=True)
        vx = M + pw + 32
        etiqueta_con_ayuda(L, vx, y + 8, "3. Vigencia (años completos)", hover=(popover == "vigencia"))
        mitad = (W - M - vx - 20) / 2
        for k, (etq, val) in enumerate((("Desde", "2019"), ("Hasta", "2023"))):
            x0 = vx + k * (mitad + 20)
            L.txt(x0, y + 42, etq, fuente("Regular", 12), GRIS_OSC, "lm")
            campo(L, x0 + 50, y + 26, x0 + mitad, y + 58, val, flecha=True)
        y += 82
    else:
        L.txt(M, y + 8, "2. Programa", fuente("Bold", 13), GRIS_OSC, "lm")
        campo(L, M, y + 26, W - M, y + 58, "Fisioterapia", flecha=True)
        y += 74
        etiqueta_con_ayuda(L, M, y + 8, "3. Vigencia (años completos)", hover=(popover == "vigencia"))
        mitad = (W - 2 * M - 16) / 2
        for k, (etq, val) in enumerate((("Desde", "2019"), ("Hasta", "2023"))):
            x0 = M + k * (mitad + 16)
            L.txt(x0, y + 42, etq, fuente("Regular", 12), GRIS_OSC, "lm")
            campo(L, x0 + 50, y + 26, x0 + mitad, y + 58, val, flecha=True)
        y += 82

    # panel de archivos
    etiqueta_con_ayuda(L, M, y + 4, "Archivos que se usarán", hover=(popover == "archivos"))
    badge = "14 de 15 encontrados"
    fb = fuente("Bold", 11)
    bwid = L.tw(badge, fb) + 24
    L.rect(W - M - bwid, y - 7, W - M, y + 15, fill=NARANJA, r=11)
    L.txt(W - M - bwid / 2, y + 4, badge, fb, NEGRO, "mm")
    gy = y + 26
    total = W - 2 * M
    cw = [total * 0.14] + [total * 0.286] * 3
    xs = [M]
    for w in cw[:-1]:
        xs.append(xs[-1] + w)
    cabeceras = ("Año", "Movilidad (anual)", "Int. en casa · 1.º sem.", "Int. en casa · 2.º sem.") if estrecha else \
                ("Año", "Movilidad (anual)", "Int. en casa · 1.º semestre", "Int. en casa · 2.º semestre")
    L.rect(M, gy, W - M, gy + 30, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    for x, t in zip(xs, cabeceras):
        L.txt(x + 12, gy + 15, t, fuente("Bold", 10.5 if estrecha else 11), BLANCO, "lm")
    filas = [("2019", 1, 1, 1), ("2020", 1, 1, 1), ("2021", 0, 1, 1), ("2022", 1, 1, 1), ("2023", 1, 1, 1)]
    for i, (anio, *oks) in enumerate(filas):
        ry = gy + 30 + i * 30
        ultima = i == len(filas) - 1
        L.rect(M, ry, W - M, ry + 30, fill=(BLANCO if i % 2 == 0 else FONDO), r=8 if ultima else 0,
               corners=(False, False, True, True) if ultima else None)
        L.txt(xs[0] + 12, ry + 15, anio, fuente("Regular", 12), NEGRO, "lm")
        for k, ok in enumerate(oks, start=1):
            if ok:
                L.check(xs[k] + 22, ry + 15)
                if cw[k] >= 150:
                    L.txt(xs[k] + 38, ry + 15, "Encontrado", fuente("Light", 11), GRIS, "lm")
            else:
                L.cross(xs[k] + 22, ry + 15)
                L.txt(xs[k] + 38, ry + 15, "Falta" if estrecha else "Falta este archivo", fuente("Bold", 11), MAGENTA, "lm")
    L.rect(M, gy, W - M, gy + 30 + 5 * 30, line=LINEA, w=1, r=8)
    y = gy + 30 + 5 * 30 + 14

    # aviso
    msg = "Falta Movilidad 2021. Puedes generar igual: quedará anotado en la revisión."
    f_av = fuente("Regular", 12)
    lineas = partir(L, [R(msg)], f_av, f_av, W - 2 * M - 62)
    ah = 20 + 17 * len(lineas) + 3
    L.rect(M, y, W - M, y + ah, fill=AVISO_BG, line=NARANJA, w=1, r=8)
    L.d.ellipse([L.P(M + 12), L.P(y + ah / 2 - 8), L.P(M + 28), L.P(y + ah / 2 + 8)], fill=NARANJA)
    L.txt(M + 20, y + ah / 2, "!", fuente("Bold", 11), NEGRO, "mm")
    for i, ln in enumerate(lineas):
        L.txt(M + 40, y + 12 + 8.5 + i * 17, " ".join(t[0] for t in ln), f_av, NEGRO, "lm")
    y += ah + 18

    # botones
    est_g = {"generar": "hover", "generar_press": "press"}.get(hover, "normal")
    est_c = "hover" if hover == "config" else "normal"
    if not estrecha:
        boton_primario(L, M, y, M + 290, y + 46, "Generar cuadro maestro", est_g)
        boton_secundario(L, M + 304, y, M + 304 + 146, y + 46, "Configuración", est_c)
        icono_ayuda(L, M + 304 + 146 + 10, y + 23, hover=(popover == "config"))
        L.txt(W - M - 28, y + 23, "Ver revisión", fuente("Regular", 12), "#9A9A9A", "rm")
        icono_ayuda(L, W - M - 20, y + 23, hover=(popover == "revision"))
        fin = y + 46
    else:
        boton_primario(L, M, y, W - M, y + 46, "Generar cuadro maestro", est_g)
        y += 58
        boton_secundario(L, M, y, M + 160, y + 40, "Configuración", est_c, 12)
        icono_ayuda(L, M + 170, y + 20, hover=(popover == "config"))
        L.txt(W - M - 28, y + 20, "Ver revisión", fuente("Regular", 12), "#9A9A9A", "rm")
        icono_ayuda(L, W - M - 20, y + 20, hover=(popover == "revision"))
        fin = y + 40

    if H is None:                      # ajustar altura al contenido
        H = int(fin + 30 + 34)
        L.img = L.img.crop((0, 0, int(W * S), int(H * S)))
        L.d = ImageDraw.Draw(L.img)
        L.H = H

    # pie
    L.rect(0, H - 34, W, H, fill=FONDO)
    L.d.line([0, L.P(H - 34), L.P(W), L.P(H - 34)], fill=LINEA, width=L.P(1))
    L.txt(M, H - 17, "Fundación Universitaria del Área Andina", fuente("Light", 10), GRIS, "lm")
    L.txt(W - M, H - 17, "Boceto v0.4.1 · datos ficticios", fuente("Light", 10), GRIS, "rm")
    L.rect(0, 0, W - 1, H - 1, line="#9A9A9A", w=1)
    return L


def reducir(img, f=2):
    return img.resize((img.width * f // S, img.height * f // S), Image.LANCZOS)


# =====================================================================
#  v0.5 — componentes nuevos
# =====================================================================
VERSION = "Boceto v0.5 · datos ficticios"
ROSA_SUAVE = "#FDE6F2"


def lapiz(L, cx, cy, color=GRIS, s=1.0):
    P = L.P
    L.d.line([P(cx - 3 * s), P(cy + 3 * s), P(cx + 5 * s), P(cy - 5 * s)], fill=color, width=P(3.6 * s))
    L.d.polygon([(P(cx - 7 * s), P(cy + 7 * s)), (P(cx - 6 * s), P(cy + 2 * s)), (P(cx - 2 * s), P(cy + 6 * s))], fill=color)


def papelera(L, cx, cy, color=GRIS, s=1.0):
    P = L.P
    w = P(1.7 * s)
    L.d.line([P(cx - 7 * s), P(cy - 4 * s), P(cx + 7 * s), P(cy - 4 * s)], fill=color, width=w)
    L.d.line([P(cx - 2.5 * s), P(cy - 6.5 * s), P(cx + 2.5 * s), P(cy - 6.5 * s)], fill=color, width=w)
    L.d.rounded_rectangle([P(cx - 5 * s), P(cy - 3 * s), P(cx + 5 * s), P(cy + 7 * s)], radius=P(1.5), outline=color, width=w)
    L.d.line([P(cx - 1.8 * s), P(cy), P(cx - 1.8 * s), P(cy + 4.5 * s)], fill=color, width=P(1.3 * s))
    L.d.line([P(cx + 1.8 * s), P(cy), P(cx + 1.8 * s), P(cy + 4.5 * s)], fill=color, width=P(1.3 * s))


def lupa(L, cx, cy, color=GRIS):
    P = L.P
    L.d.ellipse([P(cx - 6), P(cy - 6), P(cx + 4), P(cy + 4)], outline=color, width=P(1.8))
    L.d.line([P(cx + 3), P(cy + 3), P(cx + 8), P(cy + 8)], fill=color, width=P(2))


def mas(L, cx, cy, color=BLANCO, s=6):
    P = L.P
    L.d.line([P(cx - s), P(cy), P(cx + s), P(cy)], fill=color, width=P(2.4))
    L.d.line([P(cx), P(cy - s), P(cx), P(cy + s)], fill=color, width=P(2.4))


def portapapeles(L, cx, cy, color=VERDE_CTA, s=1.0):
    P = L.P
    L.d.rounded_rectangle([P(cx - 6 * s), P(cy - 6 * s), P(cx + 6 * s), P(cy + 8 * s)], radius=P(2), outline=color, width=P(1.7))
    L.d.rounded_rectangle([P(cx - 3 * s), P(cy - 8 * s), P(cx + 3 * s), P(cy - 4 * s)], radius=P(1.5), fill=color)
    L.d.line([P(cx - 3 * s), P(cy + 1 * s), P(cx + 3 * s), P(cy + 1 * s)], fill=color, width=P(1.4))
    L.d.line([P(cx - 3 * s), P(cy + 4 * s), P(cx + 1 * s), P(cy + 4 * s)], fill=color, width=P(1.4))


def flecha_der(L, x0, y, x1, color=GRIS, w=2):
    P = L.P
    L.d.line([P(x0), P(y), P(x1), P(y)], fill=color, width=P(w))
    L.d.polygon([(P(x1 + 5), P(y)), (P(x1 - 3), P(y - 5)), (P(x1 - 3), P(y + 5))], fill=color)


def flecha_abajo(L, x, y0, y1, color=GRIS, w=2):
    P = L.P
    L.d.line([P(x), P(y0), P(x), P(y1)], fill=color, width=P(w))
    L.d.polygon([(P(x), P(y1 + 5)), (P(x - 5), P(y1 - 3)), (P(x + 5), P(y1 - 3))], fill=color)


def chip(L, x, y, texto, bg=TINTE_VERDE, fg=VERDE_CTA, size=11, alineado="l", h=22):
    f = fuente("Bold", size)
    w = L.tw(texto, f) + 20
    x0 = x - w if alineado == "r" else x
    L.rect(x0, y, x0 + w, y + h, fill=bg, r=h / 2)
    L.txt(x0 + w / 2, y + h / 2, texto, f, fg, "mm")
    return x0, w


def casilla(L, x, y, marcada=True, s=16):
    if marcada:
        L.rect(x, y, x + s, y + s, fill=VERDE_CTA, r=4)
        L.check(x + s / 2, y + s / 2 + 0.5, BLANCO, 4.2)
    else:
        L.rect(x, y, x + s, y + s, fill=BLANCO, line=GRIS, w=1.5, r=4)


def parrafo(L, x, y, texto, ancho, fam="Light", px=12, color=GRIS_OSC, lh=None, negrita_en=None):
    """Texto con ajuste de línea. Devuelve la y final."""
    f = fuente(fam, px)
    lh = lh or px * 1.5
    for ln in partir(L, [(texto, False)], f, f, ancho):
        L.txt(x, y, " ".join(t[0] for t in ln), f, color, "la")
        y += lh
    return y


def barra_ventana(L, W, titulo):
    L.rect(0, 0, W, 32, fill="#EDEDED")
    L.txt(12, 16, titulo, fuente("Regular", 11), GRIS_OSC, "lm")
    for i, k in enumerate(("min", "max", "x")):
        cx = W - 100 + i * 34 + 17
        if k == "min":
            L.d.line([L.P(cx - 5), L.P(16), L.P(cx + 5), L.P(16)], fill=GRIS_OSC, width=L.P(1))
        elif k == "max":
            L.rect(cx - 5, 11, cx + 5, 21, line=GRIS_OSC, w=1)
        else:
            L.cross(cx, 16, GRIS_OSC, 5, 1.2)


def recortar(L, H):
    L.img = L.img.crop((0, 0, int(L.W * S), int(H * S)))
    L.d = ImageDraw.Draw(L.img)
    L.H = H


# ---------- ventana: Configuración ----------
TARJETAS = [
    ("Programas", "25 programas", "Los programas que se pueden elegir al generar un cuadro: se listan, se modifican, se crean o se eliminan.", "Administrar", None),
    ("Campos del cuadro maestro", "8 campos", "Las columnas del cuadro. Crea, edita o elimina campos y elige de dónde sale cada uno.", "Administrar", None),
    ("Fuentes de datos", "3 fuentes", "Cómo lee el programa cada Excel: fila de encabezados, columnas y filtros.", "Administrar", "semaforo"),
    ("Equivalencias de instituciones", "12 guardadas", "Nombres distintos que son la misma universidad (por ejemplo, con un error de escritura).", "Administrar", None),
    ("Equivalencias de programas", "9 guardadas", "Por ejemplo: Ingeniería Industrial Distancia = Ingeniería Industrial.", "Administrar", None),
    ("Tipos de persona", "8 tipos", "Cómo se nombra cada tipo en el cuadro: Docente saliente, Experto internacional…", "Administrar", None),
    ("Reglas de cruce", "5 reglas", "Cómo se asigna cada registro a un convenio y cómo se cuenta.", "Administrar", None),
    ("Asistente con Gemini", "Opcional", "Ayuda a emparejar columnas y nombres. Solo usa títulos de columnas y nombres de instituciones.", "Abrir asistente", "gris"),
]


def ventana_config(W=760, hover=None):
    L = Lienzo(W, 1000)
    M = 28
    barra_ventana(L, W, "Cuadro maestro internacional · Configuración")
    L.pegar(logo("_LOGOS-05.png", 34), M, 32 + 18)
    L.txt(W - M, 32 + 22, "Configuración", fuente("Bold", 20), GRIS_OSC, "ra")
    L.txt(W - M, 32 + 48, OFICINA, fuente("Light", 12), GRIS, "ra")
    L.rect(0, 32 + 78, W, 32 + 81, fill=VERDE)
    y = 32 + 81 + 18
    # volver + intro
    L.txt(M, y + 10, "‹  Volver al cuadro maestro", fuente("Bold", 12.5), VERDE_CTA, "lm")
    y += 32
    y = parrafo(L, M, y, "Aquí adaptas el programa a cambios en los Excel. Todo se puede listar, modificar, crear y eliminar, "
               "y se guarda al instante.", W - 2 * M, "Light", 12.5) + 10
    cw, gap = (W - 2 * M - 16) / 2, 16
    f_t, f_d = fuente("Bold", 14), fuente("Light", 11.5)
    alto_card = 128
    for i, (tit, cuenta, desc, boton, extra) in enumerate(TARJETAS):
        cx = M + (i % 2) * (cw + gap)
        cy = y + (i // 2) * (alto_card + 14)
        L.rect(cx, cy, cx + cw, cy + alto_card, fill=BLANCO, line=LINEA, w=1.2, r=12)
        L.txt(cx + 16, cy + 22, tit, f_t, GRIS_OSC, "lm")
        icono_ayuda(L, cx + 16 + L.tw(tit, f_t) + 8, cy + 22, hover=(hover == ("ayuda", i)))
        ty = cy + 42
        for ln in partir(L, [(desc, False)], f_d, f_d, cw - 32)[:3]:
            L.txt(cx + 16, ty, " ".join(t[0] for t in ln), f_d, GRIS, "la")
            ty += 16.5
        by = cy + alto_card - 14 - 30
        bw = 118 if boton == "Administrar" else 136
        est = "hover" if hover == ("btn", i) else "normal"
        boton_secundario(L, cx + cw - 14 - bw, by, cx + cw - 14, by + 30, boton, est, 12)
        if extra == "gris":
            chip(L, cx + 16, by + 4, cuenta, "#EDEDED", GRIS, 10.5, "l", 22)
        else:
            x0_, w_ = chip(L, cx + 16, by + 4, cuenta, TINTE_VERDE, VERDE_CTA, 10.5, "l", 22)
            if extra == "semaforo":      # estado de las fuentes
                sx = cx + 16 + w_ + 12
                for col, n in ((VERDE, "20"), (NARANJA, "1"), (MAGENTA, "1")):
                    L.d.ellipse([L.P(sx), L.P(by + 11), L.P(sx + 8), L.P(by + 19)], fill=col)
                    L.txt(sx + 13, by + 15, n, fuente("Bold", 11), GRIS_OSC, "lm")
                    sx += 38
    filas = (len(TARJETAS) + 1) // 2
    y += filas * (alto_card + 14) + 2
    # barra de acciones
    L.txt(M, y + 20, "Última modificación: 12-nov-2026", fuente("Light", 11.5), GRIS, "lm")
    boton_secundario(L, W - M - 290 - 190 - 12, y + 4, W - M - 290 - 12, y + 40, "Exportar configuración", "normal", 12)
    boton_primario(L, W - M - 290, y + 4, W - M, y + 40, "Probar con mis archivos")
    H = int(y + 40 + 28 + 34)
    recortar(L, H)
    L.rect(0, H - 34, W, H, fill=FONDO)
    L.d.line([0, L.P(H - 34), L.P(W), L.P(H - 34)], fill=LINEA, width=L.P(1))
    L.txt(M, H - 17, "Fundación Universitaria del Área Andina", fuente("Light", 10), GRIS, "lm")
    L.txt(W - M, H - 17, VERSION, fuente("Light", 10), GRIS, "rm")
    L.rect(0, 0, W - 1, H - 1, line="#9A9A9A", w=1)
    return L


# ---------- modales ----------
RADIO = 16


def modal_base(W, H, titulo):
    L = Lienzo(W, H)
    L.rect(0, 0, W, 32, fill="#EDEDED")
    L.txt(14, 16, titulo, fuente("Regular", 11), GRIS_OSC, "lm")
    L.cross(W - 24, 16, GRIS_OSC, 5, 1.2)
    return L


def cerrar_modal(L):
    L.rect(0.5, 0.5, L.W - 0.5, L.H - 0.5, line="#9A9A9A", w=1, r=RADIO)
    return L.img


def sobre(base_rgb, dl, dy_extra=0):
    """Atenúa la ventana de fondo y pone el modal redondeado con sombra, centrado."""
    base = Image.blend(base_rgb, Image.new("RGB", base_rgb.size, "#000000"), 0.45)
    dx = int((base.width - dl.width) / 2)
    dy = max(int(8 * S), int((base.height - dl.height) / 2)) + dy_extra
    if dy + dl.height > base.height:                 # el modal es más alto que la ventana: ampliar el fondo
        nuevo = Image.new("RGB", (base.width, dy + dl.height + int(16 * S)), "#4A4A4A")
        nuevo.paste(base, (0, 0))
        base = nuevo
    mk = Image.new("L", dl.size, 0)
    ImageDraw.Draw(mk).rounded_rectangle([0, 0, dl.width - 1, dl.height - 1], radius=RADIO * S, fill=255)
    m3 = 40 * S // 3
    sm = Image.new("L", (dl.width + 2 * m3, dl.height + 2 * m3), 0)
    ImageDraw.Draw(sm).rounded_rectangle([m3, m3 + 12, sm.width - m3, sm.height - m3 + 12], radius=RADIO * S, fill=120)
    sm = sm.filter(ImageFilter.GaussianBlur(14))
    base.paste(Image.new("RGB", sm.size, "#000000"), (dx - m3, dy - m3), sm)
    base.paste(dl, (dx, dy), mk)
    return base


# ---------- modal CRUD de programas ----------
PROGRAMAS = ["Administración de empresas", "Administración de negocios internacionales", "Arquitectura",
             "Comunicación Audiovisual y Digital", "Contaduría Pública", "Derecho", "Enfermería",
             "Entrenamiento Deportivo", "Especialización en Auditoria en Salud"]


def fila_programa(L, x0, y, x1, texto, estado):
    """Una fila = un input con sus acciones dentro. Devuelve (alto, posición del lápiz)."""
    f = fuente("Regular", 12.5)
    h = 38
    if estado == "editando":
        L.rect(x0, y, x1, y + h, fill=BLANCO, line=VERDE_CTA, w=2, r=7)
        L.txt(x0 + 14, y + h / 2, texto, f, NEGRO, "lm")
        cx = x0 + 14 + L.tw(texto, f) + 1
        L.d.line([L.P(cx), L.P(y + 9), L.P(cx), L.P(y + h - 9)], fill=NEGRO, width=L.P(1.4))
        L.rect(x1 - 70, y + 6, x1 - 40, y + h - 6, fill=TINTE_VERDE, r=6)
        L.check(x1 - 55, y + h / 2 + 0.5, VERDE_CTA, 5.5)
        L.cross(x1 - 21, y + h / 2, GRIS, 5, 1.8)
        L.txt(x0 + 4, y + h + 11, "Enter guarda · Esc cancela", fuente("Light", 11), GRIS, "lm")
        return h + 22, None
    if estado == "eliminar":
        L.rect(x0, y, x1, y + h + 4, fill=AVISO_BG, line=NARANJA, w=1.4, r=7)
        L.d.ellipse([L.P(x0 + 12), L.P(y + 11), L.P(x0 + 30), L.P(y + 29)], fill=NARANJA)
        L.txt(x0 + 21, y + 20, "!", fuente("Bold", 12), NEGRO, "mm")
        L.txt(x0 + 40, y + 20, "¿Eliminar este programa?", fuente("Bold", 12.5), GRIS_OSC, "lm")
        boton_secundario(L, x1 - 178, y + 6, x1 - 98, y + h - 2 + 2, "Cancelar", "normal", 11.5)
        L.rect(x1 - 90, y + 6, x1 - 10, y + h - 2 + 2, fill=MAGENTA, r=8)
        L.txt(x1 - 50, y + 21, "Eliminar", fuente("Bold", 11.5), BLANCO, "mm")
        L.txt(x0 + 4, y + h + 15, "Solo se quita de la lista; tus Excel no se tocan.", fuente("Light", 11), GRIS, "lm")
        return h + 26, None
    hov = estado == "hover"
    L.rect(x0, y, x1, y + h, fill=BLANCO, line=(VERDE_CTA if hov else GRIS), w=(1.6 if hov else 1), r=7)
    L.txt(x0 + 14, y + h / 2, texto, f, NEGRO, "lm")
    px, ppx = x1 - 62, x1 - 28
    if hov:
        L.d.ellipse([L.P(px - 14), L.P(y + h / 2 - 14), L.P(px + 14), L.P(y + h / 2 + 14)], fill=TINTE_VERDE)
    lapiz(L, px, y + h / 2, VERDE_CTA if hov else GRIS)
    papelera(L, ppx, y + h / 2, GRIS)
    return h, (px, y)


def modal_programas(W=640):
    L = modal_base(W, 900, "Programas")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Programas", fuente("Bold", 20), GRIS_OSC, "lm")
    icono_ayuda(L, pad + L.tw("Programas", fuente("Bold", 20)) + 10, y + 12)
    chip(L, W - pad, y + 1, "25 programas · sede Pereira", TINTE_VERDE, VERDE_CTA, 11, "r", 24)
    y += 36
    y = parrafo(L, pad, y, "Son los programas que podrás elegir al generar un cuadro. Cambia un nombre con el lápiz, "
                "quita uno con la papelera o crea uno nuevo.", W - 2 * pad, "Light", 12.5) + 8
    # buscar + crear
    L.rect(pad, y, pad + 372, y + 38, fill=BLANCO, line=GRIS, w=1, r=7)
    lupa(L, pad + 20, y + 18, GRIS)
    L.txt(pad + 40, y + 19, "Buscar programa…", fuente("Regular", 12.5), "#9A9A9A", "lm")
    L.rect(W - pad - 190, y, W - pad, y + 38, fill=VERDE_CTA, r=8)
    mas(L, W - pad - 190 + 26, y + 19, BLANCO, 6)
    L.txt(W - pad - 190 + 42, y + 19, "Crear programa", fuente("Bold", 13.5), BLANCO, "lm")
    y += 54
    # lista con desplazamiento
    ly0 = y
    ix0, ix1 = pad + 12, W - pad - 28
    y += 12
    estados = ["normal", "hover", "editando", "eliminar", "normal", "normal", "normal", "normal", "normal"]
    textos = list(PROGRAMAS)
    textos[2] = "Arquitectura y Urbanismo"
    lapiz_pos = None
    for t, e in zip(textos, estados):
        h, pos = fila_programa(L, ix0, y, ix1, t, e)
        if pos and e == "hover":
            lapiz_pos = pos
        y += h + 8
    ly1 = y + 4
    L.rect(pad, ly0, W - pad, ly1, line=LINEA, w=1.2, r=10)
    # barra de desplazamiento (se dibuja sobre el borde derecho de la lista)
    L.rect(W - pad - 16, ly0 + 12, W - pad - 8, ly1 - 12, fill="#ECECEC", r=4)
    L.rect(W - pad - 16, ly0 + 12, W - pad - 8, ly0 + 12 + int((ly1 - ly0 - 24) * 0.36), fill="#A8A8A8", r=4)
    # tooltip sobre el lápiz en hover
    if lapiz_pos:
        tx, ty = lapiz_pos[0] - 24, lapiz_pos[1] + 19
        L.rect(tx - 52, ty - 12, tx, ty + 12, fill=GRIS_OSC, r=6)
        L.d.polygon([(L.P(tx - 1), L.P(ty - 5)), (L.P(tx - 1), L.P(ty + 5)), (L.P(tx + 5), L.P(ty))], fill=GRIS_OSC)
        L.txt(tx - 26, ty, "Editar", fuente("Regular", 11), BLANCO, "mm")
    y = ly1 + 14
    L.txt(pad, y + 18, "Mostrando 9 de 25 · desplázate para ver más", fuente("Light", 11.5), GRIS, "lm")
    L.txt(pad, y + 38, "Los cambios se guardan al instante.", fuente("Light", 11.5), GRIS, "lm")
    boton_primario(L, W - pad - 130, y + 6, W - pad, y + 46, "Listo")
    H = int(y + 46 + 26)
    recortar(L, H)
    cerrar_modal(L)
    return L


# ---------- modal: asistente con Gemini (4 pasos) ----------
def ilustracion(L, n, ox, oy, w=330, h=108):
    L.rect(ox, oy, ox + w, oy + h, fill=FONDO, r=10)
    f9, f10b = fuente("Light", 9.5), fuente("Bold", 10.5)
    if n == 1:                                           # mensaje preparado + botón copiar
        L.rect(ox + 22, oy + 14, ox + 176, oy + 94, fill=BLANCO, line=LINEA, w=1.2, r=7)
        L.txt(ox + 32, oy + 28, "Mensaje para Gemini", f10b, GRIS_OSC, "lm")
        for i, ancho in enumerate((124, 108, 118, 80)):
            L.rect(ox + 32, oy + 42 + i * 12, ox + 32 + ancho, oy + 47 + i * 12, fill="#D9D9D9", r=3)
        flecha_der(L, ox + 184, oy + 54, ox + 202, GRIS, 1.6)
        L.rect(ox + 212, oy + 30, ox + 316, oy + 66, fill=BLANCO, line=VERDE_CTA, w=1.6, r=8)
        portapapeles(L, ox + 230, oy + 48, VERDE_CTA, 0.9)
        L.txt(ox + 244, oy + 48, "Copiar", fuente("Bold", 11.5), VERDE_CTA, "lm")
        chip(L, ox + w - 14, oy + 74, "Sin datos de personas", "#EDEDED", GRIS_OSC, 9.5, "r", 20)
    elif n == 2:                                         # navegador con Gemini
        L.rect(ox + 36, oy + 12, ox + w - 36, oy + 96, fill=BLANCO, line=GRIS, w=1.2, r=9)
        L.rect(ox + 36, oy + 12, ox + w - 36, oy + 32, fill="#EDEDED", r=9, corners=(True, True, False, False))
        for i in range(3):
            L.d.ellipse([L.P(ox + 48 + i * 11), L.P(oy + 18), L.P(ox + 54 + i * 11), L.P(oy + 24)], fill="#B8B8B8")
        L.rect(ox + 96, oy + 16, ox + w - 56, oy + 28, fill=BLANCO, r=6)
        L.txt(ox + 106, oy + 22, "gemini.google.com", f9, GRIS, "lm")
        L.txt(ox + w / 2, oy + 52, "Gemini", fuente("Bold", 15), GRIS_OSC, "mm")
        L.rect(ox + 70, oy + 68, ox + w - 70, oy + 88, fill="#F5F5F5", line=LINEA, w=1, r=10)
        L.txt(ox + 82, oy + 78, "Escribe aquí tu mensaje…", f9, "#9A9A9A", "lm")
    elif n == 3:                                         # pegar y enviar
        for i, t in enumerate(("Ctrl", "V")):
            kx = ox + w / 2 - 38 + i * 48
            L.rect(kx, oy + 10, kx + (44 if i == 0 else 32), oy + 32, fill=BLANCO, line=GRIS, w=1.3, r=5)
            L.txt(kx + (22 if i == 0 else 16), oy + 21, t, fuente("Bold", 11), GRIS_OSC, "mm")
        L.txt(ox + w / 2 - 41, oy + 21, "", f9, GRIS, "mm")
        flecha_abajo(L, ox + w / 2, oy + 36, oy + 56, VERDE_CTA, 2)
        L.rect(ox + 36, oy + 62, ox + w - 36, oy + 98, fill=BLANCO, line=GRIS, w=1.3, r=18)
        L.txt(ox + 52, oy + 80, "Ayúdame a emparejar estos nombres de…", f9, GRIS_OSC, "lm")
        L.d.ellipse([L.P(ox + w - 68), L.P(oy + 68), L.P(ox + w - 42), L.P(oy + 92)], fill=VERDE_CTA)
        L.d.line([L.P(ox + w - 55), L.P(oy + 86), L.P(ox + w - 55), L.P(oy + 74)], fill=BLANCO, width=L.P(2))
        L.d.polygon([(L.P(ox + w - 55), L.P(oy + 72)), (L.P(ox + w - 60), L.P(oy + 78)), (L.P(ox + w - 50), L.P(oy + 78))], fill=BLANCO)
    else:                                                # copiar respuesta y pegar en el programa
        L.rect(ox + 18, oy + 12, ox + 150, oy + 96, fill=BLANCO, line=LINEA, w=1.2, r=10)
        L.txt(ox + 28, oy + 26, "Respuesta", f10b, GRIS_OSC, "lm")
        for i, ancho in enumerate((106, 90, 100, 70)):
            L.rect(ox + 28, oy + 40 + i * 12, ox + 28 + ancho, oy + 45 + i * 12, fill="#D9D9D9", r=3)
        portapapeles(L, ox + 136, oy + 24, VERDE_CTA, 0.75)
        flecha_der(L, ox + 156, oy + 54, ox + 176, GRIS, 1.6)
        L.rect(ox + 186, oy + 12, ox + w - 14, oy + 96, fill=BLANCO, line=VERDE_CTA, w=1.6, r=8)
        L.txt(ox + 196, oy + 25, "Pegar respuesta", f10b, GRIS_OSC, "lm")
        L.rect(ox + 196, oy + 36, ox + w - 24, oy + 62, fill="#F5F5F5", line=LINEA, w=1, r=5)
        L.rect(ox + 196, oy + 70, ox + w - 24, oy + 88, fill=VERDE_CTA, r=6)
        L.txt(ox + 186 + (w - 14 - 186) / 2, oy + 79, "Revisar sugerencias", fuente("Bold", 9.5), BLANCO, "mm")


PASOS = [
    ("Copia el mensaje", "El programa lo prepara por ti con títulos de columnas y nombres de instituciones. Pulsa Copiar."),
    ("Abre Gemini", "Se abre en tu navegador. Inicia sesión con tu cuenta y abre un chat nuevo."),
    ("Pega y envía", "Pega el mensaje con Ctrl + V y envíalo. Gemini responde con una lista de coincidencias."),
    ("Vuelve y pega la respuesta", "Copia la respuesta de Gemini, vuelve aquí, pégala y pulsa Revisar sugerencias."),
]


def modal_gemini_pasos(W=756):
    L = modal_base(W, 1000, "Asistente con Gemini")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Asistente con Gemini", fuente("Bold", 20), GRIS_OSC, "lm")
    chip(L, pad + L.tw("Asistente con Gemini", fuente("Bold", 20)) + 12, y + 1, "Opcional", "#EDEDED", GRIS, 11, "l", 24)
    y += 38
    y = parrafo(L, pad, y, "Gemini te ayuda a emparejar columnas y nombres de instituciones que el programa no reconoció. "
                "Son 4 pasos y no necesitas instalar nada.", W - 2 * pad, "Light", 12.5) + 10
    cw, gap = (W - 2 * pad - 16) / 2, 16
    f_t, f_d = fuente("Bold", 14), fuente("Light", 11.5)
    lin_max = max(len(partir(L, [(d_, False)], f_d, f_d, cw - 28)) for _, d_ in PASOS)
    alto_card = 6 + 108 + 14 + 36 + lin_max * 16.5 + 16
    for i, (tit, desc) in enumerate(PASOS):
        cx = pad + (i % 2) * (cw + gap)
        cy = y + (i // 2) * (alto_card + 14)
        L.rect(cx, cy, cx + cw, cy + alto_card, fill=BLANCO, line=LINEA, w=1.2, r=12)
        ilustracion(L, i + 1, cx + 6, cy + 6, cw - 12, 108)
        ty = cy + 6 + 108 + 14
        L.d.ellipse([L.P(cx + 14), L.P(ty), L.P(cx + 14 + 26), L.P(ty + 26)], fill=VERDE_CTA)
        L.txt(cx + 27, ty + 13, str(i + 1), fuente("Bold", 13), BLANCO, "mm")
        L.txt(cx + 50, ty + 13, tit, f_t, GRIS_OSC, "lm")
        ty += 36
        for ln in partir(L, [(desc, False)], f_d, f_d, cw - 28)[:3]:
            L.txt(cx + 14, ty, " ".join(t[0] for t in ln), f_d, GRIS, "la")
            ty += 16.5
    y += 2 * (alto_card + 14)
    # avisos
    L.rect(pad, y, W - pad, y + 66, fill=AVISO_BG, line=NARANJA, w=1, r=8)
    L.d.ellipse([L.P(pad + 12), L.P(y + 12), L.P(pad + 30), L.P(y + 30)], fill=NARANJA)
    L.txt(pad + 21, y + 21, "!", fuente("Bold", 12), NEGRO, "mm")
    L.txt(pad + 42, y + 21, "Gemini solo sugiere: nada se aplica sin tu confirmación.", fuente("Bold", 12), GRIS_OSC, "lm")
    L.txt(pad + 42, y + 44, "No pegues nombres, documentos ni correos de personas. El mensaje que prepara el programa ya no los incluye.",
          fuente("Regular", 11.5), NEGRO, "lm")
    y += 66 + 18
    boton_secundario(L, pad, y, pad + 120, y + 42, "Cerrar", "normal", 13)
    L.txt(pad + 140, y + 21, "Ya tengo la respuesta", fuente("Bold", 12.5), VERDE_CTA, "lm")
    boton_primario(L, W - pad - 310, y, W - pad, y + 42, "Copiar mensaje y abrir Gemini")
    H = int(y + 42 + 26)
    recortar(L, H)
    cerrar_modal(L)
    return L


# ---------- modal: pegar respuesta y confirmar sugerencias ----------
SUGERENCIAS = [
    ("Universidad Autónoma deSinaloa", "UNIVERSIDAD AUTÓNOMA DE SINALOA (UAS)", True),
    ("Benemérita Universidad Autónoma de Puebla", "BENEMERITA UNIVERSIDAD AUTONOMA DE PUEBLA - BUAP", True),
    ("Universidad Autónoma del Estado de México", "UNIVERSIDAD AUTÓNOMA DEL ESTADO DE MÉXICO - UAEMEX", True),
    ("Universidad Nacional Autónoma de México", "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO - UNAM", True),
    ("Universidad de Montreal", None, False),
]


def modal_gemini_respuesta(W=700):
    L = modal_base(W, 1000, "Asistente con Gemini · Paso 4 de 4")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Pega la respuesta de Gemini", fuente("Bold", 20), GRIS_OSC, "lm")
    chip(L, W - pad, y + 1, "Paso 4 de 4", TINTE_VERDE, VERDE_CTA, 11, "r", 24)
    y += 40
    L.rect(pad, y, W - pad, y + 96, fill=BLANCO, line=VERDE_CTA, w=2, r=8)
    f = fuente("Regular", 11)
    for i, t in enumerate(("1. Universidad Autónoma deSinaloa → UNIVERSIDAD AUTÓNOMA DE SINALOA (UAS)",
                           "2. Benemérita Universidad Autónoma de Puebla → BENEMERITA UNIVERSIDAD AUTONOMA DE PUEBLA - BUAP",
                           "3. Universidad Autónoma del Estado de México → UNIVERSIDAD AUTÓNOMA DEL ESTADO DE MÉXICO…",
                           "4. Universidad Nacional Autónoma de México → UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO…",
                           "5. Universidad de Montreal → sin coincidencia")):
        L.txt(pad + 14, y + 14 + i * 16.5, t, f, GRIS_OSC, "lm")
    y += 96 + 12
    boton_primario(L, W - pad - 190, y, W - pad, y + 38, "Revisar sugerencias")
    L.txt(pad, y + 19, "Pegado: 5 líneas", fuente("Light", 11.5), GRIS, "lm")
    y += 38 + 22
    L.txt(pad, y + 10, "Sugerencias (5)", fuente("Bold", 14), GRIS_OSC, "lm")
    L.txt(W - pad, y + 10, "Marca las que quieres guardar", fuente("Light", 11.5), GRIS, "rm")
    y += 28
    # tabla
    cols = [pad, pad + 44, pad + 300, W - pad - 130]
    L.rect(pad, y, W - pad, y + 34, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    for x, t in ((cols[1], "El Excel dice"), (cols[2], "Gemini propone"), (cols[3], "Estado")):
        L.txt(x, y + 17, t, fuente("Bold", 11.5), BLANCO, "lm")
    casilla(L, pad + 14, y + 9, True, 16)
    y += 34
    f_c = fuente("Regular", 11.5)
    for i, (orig, prop, ok) in enumerate(SUGERENCIAS):
        fh = 44
        L.rect(pad, y, W - pad, y + fh, fill=(FONDO if i % 2 else BLANCO))
        casilla(L, pad + 14, y + 14, ok, 16)
        L.txt(cols[1], y + fh / 2, orig, f_c, NEGRO, "lm")
        if prop:
            ln = partir(L, [(prop, False)], f_c, f_c, cols[3] - cols[2] - 16)
            ty = y + fh / 2 - (len(ln) - 1) * 7.5
            for j, l_ in enumerate(ln[:2]):
                L.txt(cols[2], ty + j * 15, " ".join(t[0] for t in l_), f_c, NEGRO, "lm")
            chip(L, cols[3], y + 11, "Por confirmar", AVISO_BG, "#9A5B00", 10.5, "l", 22)
        else:
            L.txt(cols[2], y + fh / 2, "—", f_c, GRIS, "lm")
            chip(L, cols[3], y + 11, "No coincide", ROSA_SUAVE, MAGENTA, 10.5, "l", 22)
        y += fh
    L.rect(pad, y - 44 * len(SUGERENCIAS) - 34, W - pad, y, line=LINEA, w=1.2, r=8)
    y += 12
    y = parrafo(L, pad, y, "Las equivalencias que guardes aparecen en Configuración → Equivalencias de instituciones y el programa "
                "no vuelve a preguntarlas. Lo que no coincide queda en Ver revisión.", W - 2 * pad, "Light", 11.5) + 8
    L.txt(pad, y + 21, "4 de 5 seleccionadas", fuente("Bold", 12), GRIS_OSC, "lm")
    boton_secundario(L, W - pad - 190 - 12 - 120, y, W - pad - 190 - 12, y + 42, "Cancelar", "normal", 13)
    boton_primario(L, W - pad - 190, y, W - pad, y + 42, "Guardar 4 equivalencias")
    H = int(y + 42 + 26)
    recortar(L, H)
    cerrar_modal(L)
    return L





# =====================================================================
#  v0.7 — Campos del cuadro maestro y Fuentes de datos
# =====================================================================
VERSION = "Boceto v0.7 · datos ficticios"
OK_TXT = "#4A6320"
AVISO_TXT = "#9A5B00"


def agarre(L, cx, cy, color="#A8A8A8"):
    """Seis puntos para arrastrar."""
    P = L.P
    for dx in (-3, 3):
        for dy in (-5, 0, 5):
            L.d.ellipse([P(cx + dx - 1.3), P(cy + dy - 1.3), P(cx + dx + 1.3), P(cy + dy + 1.3)], fill=color)


def candado(L, cx, cy, color=GRIS):
    P = L.P
    L.d.rounded_rectangle([P(cx - 5), P(cy - 1), P(cx + 5), P(cy + 6)], radius=P(1.5), fill=color)
    L.d.arc([P(cx - 3.5), P(cy - 7), P(cx + 3.5), P(cy + 1)], start=180, end=360, fill=color, width=P(1.7))


def tooltip(L, x_der, y, texto, size=11):
    """Globo oscuro a la izquierda del punto (x_der, y) con flecha hacia la derecha."""
    f = fuente("Regular", size)
    w = L.tw(texto, f) + 20
    L.rect(x_der - w - 6, y - 12, x_der - 6, y + 12, fill=GRIS_OSC, r=6)
    L.d.polygon([(L.P(x_der - 7), L.P(y - 5)), (L.P(x_der - 7), L.P(y + 5)), (L.P(x_der - 1), L.P(y))], fill=GRIS_OSC)
    L.txt(x_der - 6 - w / 2, y, texto, f, BLANCO, "mm")


def tooltip_arriba(L, x_der, y_base, texto, size=11):
    """Globo oscuro sobre el punto: su borde derecho en x_der y la flecha hacia abajo."""
    f = fuente("Regular", size)
    w = L.tw(texto, f) + 20
    L.rect(x_der - w, y_base - 24, x_der, y_base, fill=GRIS_OSC, r=6)
    L.d.polygon([(L.P(x_der - 20), L.P(y_base)), (L.P(x_der - 10), L.P(y_base)), (L.P(x_der - 15), L.P(y_base + 6))], fill=GRIS_OSC)
    L.txt(x_der - w / 2, y_base - 12, texto, f, BLANCO, "mm")


def desplegable(L, x0, y0, x1, y1, texto, foco=False, color=NEGRO):
    L.rect(x0, y0, x1, y1, fill=BLANCO, line=(VERDE_CTA if foco else GRIS), w=(2 if foco else 1), r=6)
    L.txt(x0 + 12, (y0 + y1) / 2, texto, fuente("Regular", 12), color, "lm")
    L.flecha(x1 - 18, (y0 + y1) / 2)


FUENTE_CHIP = {
    "Matriz": (TINTE_VERDE, OK_TXT),
    "Reportes": (AVISO_BG, AVISO_TXT),
    "Calculado": ("#EDEDED", GRIS_OSC),
    "Vacío": (BLANCO, GRIS),
}

# nombre, fuente, detalle, tipo, base
CAMPOS = [
    ("No.", "Calculado", "Número consecutivo", "Número", False),
    ("Institución", "Matriz", "Nombre de la institución", "Texto", True),
    ("Breve objeto", "Matriz", "Objeto del convenio", "Texto", False),
    ("Resultados concretos", "Calculado", "Movilidad + int. en casa, por año y tipo", "Texto calculado", True),
    ("Vigencia (años)", "Matriz", "Fechas de inicio y fin / vigencia", "Número", True),
    ("Activo", "Matriz", "Estado del convenio hoy", "Opciones", True),
    ("Nº de usuarios", "Vacío", "No se llena", "Número", False),
    ("No aplica", "Vacío", "No se llena", "Texto", False),
]


def modal_campos(W=900):
    L = modal_base(W, 1200, "Campos del cuadro maestro")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Campos del cuadro maestro", fuente("Bold", 20), GRIS_OSC, "lm")
    icono_ayuda(L, pad + L.tw("Campos del cuadro maestro", fuente("Bold", 20)) + 10, y + 12)
    chip(L, W - pad, y + 1, "8 campos", TINTE_VERDE, VERDE_CTA, 11, "r", 24)
    y += 36
    y = parrafo(L, pad, y, "Son las columnas del cuadro que se genera, en el orden en que aparecen. Cada campo dice de dónde "
                "sale su dato. Arrástralos para ordenarlos, edítalos con el lápiz o crea uno nuevo.", W - 2 * pad, "Light", 12.5) + 8
    # barra de herramientas
    f_h = fuente("Light", 11.5)
    L.txt(pad, y + 19, "Arrastra", f_h, GRIS, "lm")
    gx = pad + L.tw("Arrastra", f_h) + 16
    agarre(L, gx, y + 19, "#A8A8A8")
    L.txt(gx + 14, y + 19, "para cambiar el orden en el cuadro", f_h, GRIS, "lm")
    L.rect(W - pad - 170, y, W - pad, y + 38, fill=VERDE_CTA, r=8)
    mas(L, W - pad - 170 + 26, y + 19, BLANCO, 6)
    L.txt(W - pad - 170 + 42, y + 19, "Crear campo", fuente("Bold", 13.5), BLANCO, "lm")
    y += 54
    # tabla
    x0, x1 = pad, W - pad
    cx = [x0 + 14, x0 + 50, x0 + 82, x0 + 292, x0 + 640]       # agarre, #, nombre, origen, tipo
    L.rect(x0, y, x1, y + 34, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    for xx, t in ((cx[1], "#"), (cx[2], "Nombre en el cuadro"), (cx[3], "De dónde sale el dato"), (cx[4], "Tipo")):
        L.txt(xx, y + 17, t, fuente("Bold", 11.5), BLANCO, "lm")
    top = y
    y += 34
    f_n, f_d = fuente("Bold", 12.5), fuente("Regular", 11.5)
    tooltip_pos = None
    for i, (nom, fu, det, tipo, base) in enumerate(CAMPOS):
        editando = (i == 1)
        hover = (i == 3)
        fh = 48
        fondo = BLANCO if i % 2 == 0 else FONDO
        if hover:
            fondo = "#F1F7E7"
        L.rect(x0, y, x1, y + fh, fill=fondo)
        agarre(L, cx[0] + 4, y + fh / 2, VERDE_CTA if hover else "#A8A8A8")
        L.txt(cx[1], y + fh / 2, str(i + 1), f_d, GRIS, "lm")
        L.txt(cx[2], y + fh / 2, nom, f_n, GRIS_OSC, "lm")
        bg, fg = FUENTE_CHIP[fu]
        if fu == "Vacío":
            L.rect(cx[3], y + 13, cx[3] + L.tw(fu, fuente("Bold", 10.5)) + 20, y + 35, fill=BLANCO, line=LINEA, w=1.2, r=11)
            L.txt(cx[3] + (L.tw(fu, fuente("Bold", 10.5)) + 20) / 2, y + 24, fu, fuente("Bold", 10.5), GRIS, "mm")
            wchip = L.tw(fu, fuente("Bold", 10.5)) + 20
        else:
            _, wchip = chip(L, cx[3], y + 13, fu, bg, fg, 10.5, "l", 22)
        L.txt(cx[3] + wchip + 10, y + fh / 2, det, f_d, NEGRO, "lm")
        L.txt(cx[4], y + fh / 2, tipo, f_d, GRIS_OSC, "lm")
        px, ppx = x1 - 64, x1 - 30
        if hover:
            L.d.ellipse([L.P(px - 14), L.P(y + fh / 2 - 14), L.P(px + 14), L.P(y + fh / 2 + 14)], fill=TINTE_VERDE)
        lapiz(L, px, y + fh / 2, VERDE_CTA if hover else GRIS)
        if base:
            candado(L, ppx, y + fh / 2, GRIS)
            if hover:
                tooltip_pos = (ppx + 17, y + 10)
        else:
            papelera(L, ppx, y + fh / 2, GRIS)
        if editando:
            # fila en edición: panel que se abre debajo
            L.rect(x0, y, x1, y + fh, fill=TINTE_VERDE)
            agarre(L, cx[0] + 4, y + fh / 2, "#A8A8A8")
            L.txt(cx[1], y + fh / 2, str(i + 1), f_d, GRIS, "lm")
            L.txt(cx[2], y + fh / 2, "Editando: " + nom, f_n, OK_TXT, "lm")
            y += fh
            ph = 252
            L.rect(x0, y, x1, y + ph, fill=TINTE_VERDE)
            L.rect(x0 + 16, y + 6, x1 - 16, y + ph - 14, fill=BLANCO, line=VERDE_CTA, w=1.6, r=10)
            ix = x0 + 36
            colw = (x1 - x0 - 72 - 20) / 2
            L.txt(ix, y + 28, "Nombre en el cuadro", fuente("Bold", 12), GRIS_OSC, "lm")
            campo(L, ix, y + 40, ix + colw, y + 72, nom, foco=True)
            L.txt(ix + colw + 20, y + 28, "Tipo de dato", fuente("Bold", 12), GRIS_OSC, "lm")
            desplegable(L, ix + colw + 20, y + 40, ix + 2 * colw + 20, y + 72, tipo)
            L.txt(ix, y + 92, "Fuente del dato", fuente("Bold", 12), GRIS_OSC, "lm")
            desplegable(L, ix, y + 104, ix + colw, y + 136, "Matriz de convenios")
            L.txt(ix + colw + 20, y + 92, "Columna del Excel", fuente("Bold", 12), GRIS_OSC, "lm")
            desplegable(L, ix + colw + 20, y + 104, ix + 2 * colw + 20, y + 136, "Nombre de la institución")
            chip(L, ix + colw + 20, y + 146, "Exacta", TINTE_VERDE, OK_TXT, 10, "l", 20)
            L.txt(ix + colw + 20 + 66, y + 156, "Encontrada con este nombre en la matriz", fuente("Light", 11), GRIS, "lm")
            L.txt(ix, y + 158, "Campo base: se puede renombrar, no eliminar.", fuente("Light", 11), GRIS, "lm")
            boton_secundario(L, x1 - 36 - 120 - 12 - 120, y + ph - 14 - 50, x1 - 36 - 120 - 12, y + ph - 14 - 12, "Cancelar", "normal", 12)
            boton_primario(L, x1 - 36 - 120, y + ph - 14 - 50, x1 - 36, y + ph - 14 - 12, "Guardar")
            y += ph
        else:
            y += fh
    bottom = y
    L.rect(x0, top, x1, bottom, line=LINEA, w=1.2, r=8)
    if tooltip_pos:
        tooltip_arriba(L, tooltip_pos[0], tooltip_pos[1], "Campo base: no se puede eliminar")
    y += 16
    y = parrafo(L, pad, y, "Los campos base son los que el programa necesita para calcular. Los demás se pueden quitar o agregar. "
                "Los cambios se guardan al instante.", W - 2 * pad - 150, "Light", 11.5, GRIS) + 2
    boton_primario(L, W - pad - 130, y - 36, W - pad, y + 4, "Listo")
    H = int(y + 4 + 26)
    recortar(L, H)
    cerrar_modal(L)
    return L


# ---------- Fuentes de datos ----------
FUENTES = [
    ("Matriz de convenios", "Un archivo · hoja CONV_INTERNACIONALES", [(VERDE, "8 exactas")]),
    ("Movilidad", "Un archivo por año", [(VERDE, "6 exactas"), (NARANJA, "1 por confirmar")]),
    ("Internacionalización en casa", "Dos archivos por año (1.º y 2.º semestre)", [(VERDE, "6 exactas"), (MAGENTA, "1 sin identificar")]),
]

COLS_IC = [
    ("Año", "AÑO", "exacta"),
    ("Semestre", "SEMESTRE", "exacta"),
    ("Programa", "PROGRAMA ACADÉMICO", "exacta"),
    ("Institución", "INSTITUCIÓN ALIADA", "exacta"),
    ("Tipo de actividad", "TIPO DE ACTIVIDAD", "exacta"),
    ("Participantes", "NO. PARTICIPANTES", "exacta"),
    ("Tipo de persona", None, "sin"),
]


def modal_fuentes(W=980):
    L = modal_base(W, 1300, "Fuentes de datos")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Fuentes de datos", fuente("Bold", 20), GRIS_OSC, "lm")
    icono_ayuda(L, pad + L.tw("Fuentes de datos", fuente("Bold", 20)) + 10, y + 12)
    cx_ = W - pad
    for txt, bg, fg in (("1 sin identificar", ROSA_SUAVE, MAGENTA), ("1 por confirmar", AVISO_BG, AVISO_TXT), ("20 exactas", TINTE_VERDE, OK_TXT)):
        x_, w_ = chip(L, cx_, y + 1, txt, bg, fg, 11, "r", 24)
        cx_ = x_ - 8
    y += 36
    y = parrafo(L, pad, y, "Aquí dices cómo reconoce el programa cada tipo de Excel: qué archivos son, dónde están los encabezados y "
                "qué columna trae cada dato. Lo exacto se aplica solo; lo dudoso te lo pide confirmar.", W - 2 * pad, "Light", 12.5) + 10
    ytop = y
    lw = 290
    # lista izquierda
    f_t, f_s = fuente("Bold", 13.5), fuente("Light", 11)
    cy = y
    for i, (tit, sub, estados) in enumerate(FUENTES):
        sel = i == 2
        ch = 112
        L.rect(pad, cy, pad + lw, cy + ch, fill=(TINTE_VERDE if sel else BLANCO), line=(VERDE_CTA if sel else LINEA),
               w=(2 if sel else 1.2), r=12)
        L.txt(pad + 16, cy + 24, tit, f_t, GRIS_OSC, "lm")
        sl = partir(L, [(sub, False)], f_s, f_s, lw - 32)
        for j, ln in enumerate(sl):
            L.txt(pad + 16, cy + 46 + j * 15, " ".join(t[0] for t in ln), f_s, GRIS, "la")
        ey = cy + 46 + len(sl) * 15 + 8
        ex = pad + 16
        for col, txt in estados:
            L.d.ellipse([L.P(ex), L.P(ey + 6), L.P(ex + 9), L.P(ey + 15)], fill=col)
            L.txt(ex + 14, ey + 10.5, txt, fuente("Bold", 10.5), GRIS_OSC, "lm")
            ex += 14 + L.tw(txt, fuente("Bold", 10.5)) + 14
        cy += ch + 12
    L.rect(pad, cy, pad + lw, cy + 40, fill=BLANCO, line=VERDE_CTA, w=1.5, r=8)
    mas(L, pad + 60, cy + 20, VERDE_CTA, 6)
    L.txt(pad + 78, cy + 20, "Agregar fuente", fuente("Bold", 13), VERDE_CTA, "lm")
    cy += 52
    # panel derecho
    rx0, rx1 = pad + lw + 20, W - pad
    ry = y
    L.txt(rx0, ry + 14, "Internacionalización en casa", fuente("Bold", 16), GRIS_OSC, "lm")
    L.rect(rx1 - 100, ry, rx1, ry + 28, fill=BLANCO, line=VERDE_CTA, w=1.4, r=8)
    L.txt(rx1 - 50, ry + 14, "Cambiar nombre", fuente("Bold", 10.5), VERDE_CTA, "mm")
    ry += 36
    # cómo se encuentra el archivo
    L.txt(rx0, ry + 10, "1  Cómo se encuentra el archivo", fuente("Bold", 13), VERDE_CTA, "lm")
    ry += 28
    mid = (rx1 - rx0 - 16) / 2
    L.txt(rx0, ry + 8, "El nombre del archivo contiene", fuente("Bold", 11.5), GRIS_OSC, "lm")
    campo(L, rx0, ry + 20, rx0 + mid, ry + 50, "IntCasa")
    L.txt(rx0 + mid + 16, ry + 8, "Año y semestre", fuente("Bold", 11.5), GRIS_OSC, "lm")
    desplegable(L, rx0 + mid + 16, ry + 20, rx1, ry + 50, "Se leen del nombre (2022-1)")
    ry += 66
    # fila de encabezados
    L.txt(rx0, ry + 10, "2  Fila de encabezados", fuente("Bold", 13), VERDE_CTA, "lm")
    ry += 28
    L.rect(rx0, ry, rx0 + 40, ry + 22, fill=VERDE_CTA, r=11)
    L.d.ellipse([L.P(rx0 + 21), L.P(ry + 3), L.P(rx0 + 37), L.P(ry + 19)], fill=BLANCO)
    L.txt(rx0 + 52, ry + 11, "Detectarla automáticamente", fuente("Bold", 12), GRIS_OSC, "lm")
    chip(L, rx1, ry - 1, "Detectada: fila 1 en 2022-1 · fila 2 en 2022-2", "#EDEDED", GRIS_OSC, 10.5, "r", 24)
    ry += 40
    # columnas
    L.txt(rx0, ry + 10, "3  Qué columna trae cada dato", fuente("Bold", 13), VERDE_CTA, "lm")
    ry += 28
    c0, c1, c2 = rx0 + 14, rx0 + 180, rx0 + 340
    L.rect(rx0, ry, rx1, ry + 32, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    for xx, t in ((c0, "Dato que necesita"), (c1, "Columna en el Excel"), (c2, "Estado")):
        L.txt(xx, ry + 16, t, fuente("Bold", 11.5), BLANCO, "lm")
    t0 = ry
    ry += 32
    fr = fuente("Regular", 12)
    for i, (dato, col, est) in enumerate(COLS_IC):
        rh = 40
        L.rect(rx0, ry, rx1, ry + rh, fill=(ROSA_SUAVE if est == "sin" else (BLANCO if i % 2 == 0 else FONDO)))
        L.txt(c0, ry + rh / 2, dato, fuente("Bold", 12), GRIS_OSC, "lm")
        if est == "exacta":
            L.txt(c1, ry + rh / 2, col, fr, NEGRO, "lm")
            L.check(c2 + 6, ry + rh / 2, VERDE_CTA, 5)
            L.txt(c2 + 20, ry + rh / 2, "Exacta", fuente("Bold", 11.5), OK_TXT, "lm")
        else:
            L.txt(c1, ry + rh / 2, "—", fr, GRIS, "lm")
            L.cross(c2 + 6, ry + rh / 2, MAGENTA, 4.5, 2)
            L.txt(c2 + 20, ry + rh / 2, "Sin identificar", fuente("Bold", 11.5), MAGENTA, "lm")
            bw = L.tw("Elegir columna…", fuente("Bold", 11.5)) + 28
            boton_secundario(L, rx1 - 14 - bw, ry + 6, rx1 - 14, ry + rh - 6, "Elegir columna…", "normal", 11.5)
        ry += rh
    L.rect(rx0, t0, rx1, ry, line=LINEA, w=1.2, r=8)
    ry += 12
    ry = parrafo(L, rx0, ry, "El programa buscó esa columna por nombre y no encontró una que se parezca lo bastante. "
                 "Elige cuál trae el tipo de persona (por ejemplo, el vínculo SNIES); se guarda para los próximos archivos.",
                 rx1 - rx0, "Light", 11.5, GRIS, 16) + 6
    # filtros
    L.txt(rx0, ry + 10, "4  Qué filas se usan", fuente("Bold", 13), VERDE_CTA, "lm")
    ry += 28
    for txt, marcada in (("Solo las filas del programa elegido al generar", True),
                         ("Omitir las actividades sin institución (se cuentan aparte, no se listan)", True)):
        casilla(L, rx0, ry + 2, marcada, 16)
        L.txt(rx0 + 26, ry + 10, txt, fuente("Regular", 12), NEGRO, "lm")
        ry += 28
    yend = max(ry, cy)
    y = yend + 14
    L.d.line([L.P(pad), L.P(y), L.P(W - pad), L.P(y)], fill=LINEA, width=L.P(1))
    y += 14
    boton_secundario(L, pad, y, pad + 200, y + 42, "Probar con un archivo…", "normal", 13)
    L.txt(pad + 216, y + 21, "Los cambios se guardan al instante.", fuente("Light", 11.5), GRIS, "lm")
    boton_primario(L, W - pad - 130, y, W - pad, y + 42, "Listo")
    H = int(y + 42 + 26)
    recortar(L, H)
    cerrar_modal(L)
    return L



# =====================================================================
#  v0.8 — Equivalencias de instituciones, de programas y Tipos de persona
# =====================================================================
VERSION = "Boceto v0.8 · datos ficticios"


def recortar_texto(L, s, f, ancho):
    if L.tw(s, f) <= ancho:
        return s
    while s and L.tw(s + "…", f) > ancho:
        s = s[:-1]
    return s.rstrip() + "…"


ORIGEN_CHIP = {
    "Tú": (TINTE_VERDE, OK_TXT),
    "Gemini": ("#EDEDED", GRIS_OSC),
    "Revisión": (AVISO_BG, AVISO_TXT),
}


def cabecera_pares(L, x0, x1, y, t_izq, t_der, t_ori="Origen"):
    L.rect(x0, y, x1, y + 34, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    L.txt(x0 + 14, y + 17, t_izq, fuente("Bold", 11.5), BLANCO, "lm")
    L.txt(x0 + 340, y + 17, t_der, fuente("Bold", 11.5), BLANCO, "lm")
    L.txt(x1 - 215, y + 17, t_ori, fuente("Bold", 11.5), BLANCO, "lm")
    return 34


def fila_par(L, x0, x1, y, izq, der, origen, estado="normal", idx=0, et_izq="", et_der=""):
    """Una fila 'nombre en el Excel → nombre correcto'. Devuelve el alto usado."""
    f = fuente("Regular", 12)
    h = 46
    fondo = BLANCO if idx % 2 == 0 else FONDO
    if estado == "hover":
        fondo = "#F1F7E7"
    if estado == "editando":
        L.rect(x0, y, x1, y + h, fill=TINTE_VERDE)
        L.txt(x0 + 14, y + h / 2, "Editando equivalencia", fuente("Bold", 12.5), OK_TXT, "lm")
        ph = 250
        L.rect(x0, y + h, x1, y + h + ph, fill=TINTE_VERDE)
        L.rect(x0 + 16, y + h + 2, x1 - 16, y + h + ph - 14, fill=BLANCO, line=VERDE_CTA, w=1.6, r=10)
        ix = x0 + 36
        colw = (x1 - x0 - 72 - 24) / 2
        yy = y + h + 22
        L.txt(ix, yy, et_izq, fuente("Bold", 12), GRIS_OSC, "lm")
        campo(L, ix, yy + 12, ix + colw, yy + 44, izq, foco=True)
        L.txt(ix, yy + 58, "Escríbelo tal cual aparece en el Excel, con sus errores.", fuente("Light", 11), GRIS, "lm")
        flecha_der(L, ix + colw + 5, yy + 28, ix + colw + 17, GRIS, 1.8)
        rx = ix + colw + 24
        L.txt(rx, yy, et_der, fuente("Bold", 12), GRIS_OSC, "lm")
        desplegable(L, rx, yy + 12, rx + colw, yy + 44, der, foco=True)
        # resultados de la búsqueda
        opts = ["UNIVERSIDAD AUTÓNOMA DE SINALOA (UAS)", "UNIVERSIDAD AUTÓNOMA DE NUEVO LEÓN (UANL)",
                "UNIVERSIDAD AUTÓNOMA DEL CARMEN (UNACAR)"] if "Sinaloa" in izq else []
        oy = yy + 48
        if opts:
            L.rect(rx, oy, rx + colw, oy + 3 * 30 + 6, fill=BLANCO, line=LINEA, w=1.2, r=8)
            for k, o in enumerate(opts):
                if k == 0:
                    L.rect(rx + 4, oy + 4, rx + colw - 4, oy + 4 + 30, fill=TINTE_VERDE, r=6)
                L.txt(rx + 14, oy + 19 + k * 30, recortar_texto(L, o, fuente("Regular", 11.5), colw - 28),
                      fuente("Bold" if k == 0 else "Regular", 11.5), NEGRO, "lm")
        by = y + h + ph - 14 - 12 - 40
        boton_secundario(L, x1 - 36 - 130 - 12 - 120, by, x1 - 36 - 130 - 12, by + 40, "Cancelar", "normal", 12.5)
        boton_primario(L, x1 - 36 - 130, by, x1 - 36, by + 40, "Guardar")
        return h + ph
    if estado == "eliminar":
        L.rect(x0, y, x1, y + 70, fill=AVISO_BG, line=NARANJA, w=1.4)
        L.d.ellipse([L.P(x0 + 14), L.P(y + 13), L.P(x0 + 32), L.P(y + 31)], fill=NARANJA)
        L.txt(x0 + 23, y + 22, "!", fuente("Bold", 12), NEGRO, "mm")
        L.txt(x0 + 44, y + 22, "¿Eliminar esta equivalencia?", fuente("Bold", 12.5), GRIS_OSC, "lm")
        L.txt(x0 + 44, y + 46, "El programa volverá a preguntar la próxima vez que encuentre este nombre. Tus Excel no se tocan.",
              fuente("Light", 11.5), GRIS_OSC, "lm")
        boton_secundario(L, x1 - 196, y + 14, x1 - 106, y + 44, "Cancelar", "normal", 11.5)
        L.rect(x1 - 98, y + 14, x1 - 14, y + 44, fill=MAGENTA, r=8)
        L.txt(x1 - 56, y + 29, "Eliminar", fuente("Bold", 11.5), BLANCO, "mm")
        return 70
    L.rect(x0, y, x1, y + h, fill=fondo)
    L.txt(x0 + 14, y + h / 2, recortar_texto(L, izq, f, 285), f, NEGRO, "lm")
    flecha_der(L, x0 + 304, y + h / 2, x0 + 318, GRIS, 1.8)
    L.txt(x0 + 340, y + h / 2, recortar_texto(L, der, fuente("Bold", 12), x1 - x0 - 340 - 225), fuente("Bold", 12), GRIS_OSC, "lm")
    bg, fg = ORIGEN_CHIP[origen]
    chip(L, x1 - 215, y + 12, origen, bg, fg, 10.5, "l", 22)
    px, ppx = x1 - 62, x1 - 28
    if estado == "hover":
        L.d.ellipse([L.P(px - 14), L.P(y + h / 2 - 14), L.P(px + 14), L.P(y + h / 2 + 14)], fill=TINTE_VERDE)
    lapiz(L, px, y + h / 2, VERDE_CTA if estado == "hover" else GRIS)
    papelera(L, ppx, y + h / 2, GRIS)
    return h


def modal_pares(W, titulo, chip_txt, intro, ejemplos, t_izq, t_der, et_izq, et_der, buscar, crear, nota, estados, pie_mostrando):
    L = modal_base(W, 1500, titulo)
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, titulo, fuente("Bold", 20), GRIS_OSC, "lm")
    icono_ayuda(L, pad + L.tw(titulo, fuente("Bold", 20)) + 10, y + 12)
    chip(L, W - pad, y + 1, chip_txt, TINTE_VERDE, VERDE_CTA, 11, "r", 24)
    y += 36
    y = parrafo(L, pad, y, intro, W - 2 * pad, "Light", 12.5) + 8
    # buscar + crear
    L.rect(pad, y, pad + 372, y + 38, fill=BLANCO, line=GRIS, w=1, r=7)
    lupa(L, pad + 20, y + 18, GRIS)
    L.txt(pad + 40, y + 19, buscar, fuente("Regular", 12.5), "#9A9A9A", "lm")
    cw = L.tw(crear, fuente("Bold", 13.5)) + 70
    L.rect(W - pad - cw, y, W - pad, y + 38, fill=VERDE_CTA, r=8)
    mas(L, W - pad - cw + 26, y + 19, BLANCO, 6)
    L.txt(W - pad - cw + 42, y + 19, crear, fuente("Bold", 13.5), BLANCO, "lm")
    y += 54
    x0, x1 = pad, W - pad
    top = y
    y += cabecera_pares(L, x0, x1, y, t_izq, t_der)
    hover_pos = None
    for i, (izq, der, ori) in enumerate(ejemplos):
        est = estados.get(i, "normal")
        h = fila_par(L, x0, x1, y, izq, der, ori, est, i, et_izq, et_der)
        if est == "hover":
            hover_pos = (x1 - 62, y)
        y += h
    L.rect(x0, top, x1, y, line=LINEA, w=1.2, r=8)
    if hover_pos:
        tx, ty = hover_pos[0] - 24, hover_pos[1] + 23
        L.rect(tx - 52, ty - 12, tx, ty + 12, fill=GRIS_OSC, r=6)
        L.d.polygon([(L.P(tx - 1), L.P(ty - 5)), (L.P(tx - 1), L.P(ty + 5)), (L.P(tx + 5), L.P(ty))], fill=GRIS_OSC)
        L.txt(tx - 26, ty, "Editar", fuente("Regular", 11), BLANCO, "mm")
    y += 16
    L.txt(pad, y + 8, pie_mostrando, fuente("Light", 11.5), GRIS, "lm")
    y = parrafo(L, pad, y + 28, nota, W - 2 * pad - 160, "Light", 11.5, GRIS) + 2
    boton_primario(L, W - pad - 130, y - 42, W - pad, y - 2, "Listo")
    H = int(y + 6 + 24)
    recortar(L, H)
    cerrar_modal(L)
    return L


INST = [
    ("Universidad Autónoma deSinaloa", "UNIVERSIDAD AUTÓNOMA DE SINALOA (UAS)", "Gemini"),
    ("Univ. del Istmo", "UNIVERSIDAD DEL ISTMO", "Tú"),
    ("BUAP", "BENEMÉRITA UNIVERSIDAD AUTÓNOMA DE PUEBLA - BUAP", "Tú"),
    ("Universidad Autónoma del Edo. de México", "UNIVERSIDAD AUTÓNOMA DEL ESTADO DE MÉXICO - UAEMEX", "Gemini"),
    ("UNAM", "UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO - UNAM", "Revisión"),
    ("Universidad de Carabobo ", "UNIVERSIDAD DE CARABOBO", "Tú"),
    ("Universidad Metodista", "UNIVERSIDAD METODISTA DE SAO PAULO", "Revisión"),
]


def modal_equivalencias_instituciones(W=980):
    return modal_pares(
        W, "Equivalencias de instituciones", "12 guardadas",
        "Nombres que en un Excel se escriben distinto pero son la misma institución. El programa los trata como una sola y no "
        "vuelve a preguntar.",
        INST, "Como aparece en el Excel", "Es la institución", "Como aparece en el Excel", "Institución de la matriz de convenios",
        "Buscar equivalencia…", "Crear equivalencia",
        "Las equivalencias se aplican a todos los archivos, de este año y de otros. Los cambios se guardan al instante.",
        {1: "normal", 2: "hover", 0: "editando", 4: "eliminar"}, "Mostrando 7 de 12 · desplázate para ver más")


PROG = [
    ("Ingeniería Industrial Distancia", "Ingeniería Industrial", "Tú"),
    ("Administración de Empresas (Distancia)", "Administración de empresas", "Tú"),
    ("Contaduría Pública Distancia", "Contaduría Pública", "Gemini"),
    ("Fisioterapia ", "Fisioterapia", "Revisión"),
    ("Enfermería Pereira", "Enfermería", "Tú"),
    ("Comunicación Audiovisual", "Comunicación Audiovisual y Digital", "Revisión"),
    ("Negocios Internacionales", "Administración de negocios internacionales", "Tú"),
]


def modal_equivalencias_programas(W=980):
    return modal_pares(
        W, "Equivalencias de programas", "9 guardadas",
        "Nombres de programa que cambian entre la matriz de convenios y los reportes, por ejemplo una modalidad o un espacio de más. "
        "Así el programa sabe que son el mismo.",
        PROG, "Como aparece en los reportes", "Es el programa", "Como aparece en los reportes", "Programa de la matriz de convenios",
        "Buscar equivalencia…", "Crear equivalencia",
        "Los programas de la matriz se administran en Configuración → Programas. Los cambios se guardan al instante.",
        {2: "hover"}, "Mostrando 7 de 9 · desplázate para ver más")


# ---------- Tipos de persona ----------
TIPOS = [
    ("Estudiante saliente", ["Estudiantes en el exterior", "Estudiante saliente", "Estudiante de intercambio"], False),
    ("Estudiante entrante", ["Estudiantes extranjeros", "Estudiante entrante"], False),
    ("Experto internacional", ["Experto Internacional", "Experto invitado"], False),
    ("Docente saliente", ["Docente saliente", "Profesor en el exterior"], False),
    ("Docente entrante", ["Docente entrante", "Profesor visitante"], False),
    ("Administrativo saliente", ["Administrativo saliente"], False),
    ("Administrativo entrante", ["Administrativo entrante"], False),
    ("Internacionalización en casa", None, True),
]


def chip_valor(L, x, y, texto, con_x=False, h=26):
    f = fuente("Regular", 11.5)
    w = L.tw(texto, f) + 20 + (18 if con_x else 0)
    L.rect(x, y, x + w, y + h, fill=FONDO, line=LINEA, w=1.2, r=h / 2)
    L.txt(x + 10, y + h / 2, texto, f, GRIS_OSC, "lm")
    if con_x:
        L.cross(x + w - 14, y + h / 2, GRIS, 3.6, 1.6)
    return w


def chip_agregar(L, x, y, h=26):
    f = fuente("Bold", 11)
    w = L.tw("Agregar valor", f) + 36
    L.rect(x, y, x + w, y + h, fill=BLANCO, line=VERDE_CTA, w=1.4, r=h / 2)
    mas(L, x + 14, y + h / 2, VERDE_CTA, 4.2)
    L.txt(x + 26, y + h / 2, "Agregar valor", f, VERDE_CTA, "lm")
    return w


def modal_tipos_persona(W=980):
    L = modal_base(W, 1500, "Tipos de persona")
    pad = 28
    y = 32 + 24
    L.txt(pad, y + 12, "Tipos de persona", fuente("Bold", 20), GRIS_OSC, "lm")
    icono_ayuda(L, pad + L.tw("Tipos de persona", fuente("Bold", 20)) + 10, y + 12)
    chip(L, W - pad, y + 1, "8 tipos", TINTE_VERDE, VERDE_CTA, 11, "r", 24)
    y += 36
    y = parrafo(L, pad, y, "El cuadro agrupa a las personas en estos tipos. Cada tipo reconoce los valores que aparecen en la columna de vínculo "
                "de los Excel. Si aparece un valor nuevo, agrégalo al tipo que le corresponde.", W - 2 * pad, "Light", 12.5) + 8
    L.rect(pad, y, pad + 372, y + 38, fill=BLANCO, line=GRIS, w=1, r=7)
    lupa(L, pad + 20, y + 18, GRIS)
    L.txt(pad + 40, y + 19, "Buscar tipo o valor…", fuente("Regular", 12.5), "#9A9A9A", "lm")
    cw = L.tw("Crear tipo", fuente("Bold", 13.5)) + 70
    L.rect(W - pad - cw, y, W - pad, y + 38, fill=VERDE_CTA, r=8)
    mas(L, W - pad - cw + 26, y + 19, BLANCO, 6)
    L.txt(W - pad - cw + 42, y + 19, "Crear tipo", fuente("Bold", 13.5), BLANCO, "lm")
    y += 54
    x0, x1 = pad, W - pad
    top = y
    L.rect(x0, y, x1, y + 34, fill=GRIS_OSC, r=8, corners=(True, True, False, False))
    L.txt(x0 + 16, y + 17, "Tipo en el cuadro", fuente("Bold", 11.5), BLANCO, "lm")
    L.txt(x0 + 280, y + 17, "Valores que reconoce en el Excel", fuente("Bold", 11.5), BLANCO, "lm")
    y += 34
    area0, area1 = x0 + 280, x1 - 96
    hover_pos = None
    for i, (nom, vals, base) in enumerate(TIPOS):
        editando = i == 0
        # alto según las líneas de chips
        if vals is None:
            h = 52
        else:
            xx, lineas = area0, 1
            for v in vals:
                w = L.tw(v, fuente("Regular", 11.5)) + 20 + (18 if editando else 0)
                if xx + w > area1:
                    xx, lineas = area0, lineas + 1
                xx += w + 8
            if xx + 140 > area1:
                lineas += 1
            h = max(52, 14 + lineas * 34)
        if editando:
            h += 112
        fondo = TINTE_VERDE if editando else (BLANCO if i % 2 == 0 else FONDO)
        L.rect(x0, y, x1, y + h, fill=fondo)
        L.txt(x0 + 16, y + 26, nom, fuente("Bold", 12.5), (OK_TXT if editando else GRIS_OSC), "lm")
        if vals is None:
            L.txt(area0, y + 26, "Todo lo que viene del reporte de internacionalización en casa", fuente("Regular", 11.5), GRIS, "lm")
        else:
            xx, yy = area0, y + 13
            for v in vals:
                w = L.tw(v, fuente("Regular", 11.5)) + 20 + (18 if editando else 0)
                if xx + w > area1:
                    xx, yy = area0, yy + 34
                chip_valor(L, xx, yy, v, con_x=editando)
                xx += w + 8
            if not editando:
                pass
            else:
                if xx + 140 > area1:
                    xx, yy = area0, yy + 34
                chip_agregar(L, xx, yy)
        px, ppx = x1 - 64, x1 - 30
        if i == 2:
            L.d.ellipse([L.P(px - 14), L.P(y + 26 - 14), L.P(px + 14), L.P(y + 26 + 14)], fill=TINTE_VERDE)
            hover_pos = (px, y + 26)
        lapiz(L, px, y + 26, VERDE_CTA if i == 2 else GRIS)
        if base:
            candado(L, ppx, y + 26, GRIS)
        else:
            papelera(L, ppx, y + 26, GRIS)
        if editando:
            by = y + h - 112
            L.rect(area0 - 14, by + 4, x1 - 16, y + h - 12, fill=BLANCO, line=VERDE_CTA, w=1.6, r=10)
            L.txt(area0, by + 24, "Valores que el programa vio y no reconoció", fuente("Bold", 11.5), GRIS_OSC, "lm")
            xx = area0
            for v in ("Estudiante Posgrado Exterior", "Intercambio"):
                w = L.tw("+  " + v, fuente("Regular", 11.5)) + 20
                L.rect(xx, by + 36, xx + w, by + 62, fill=AVISO_BG, line=NARANJA, w=1.2, r=13)
                L.txt(xx + 10, by + 49, "+  " + v, fuente("Regular", 11.5), AVISO_TXT, "lm")
                xx += w + 8
            L.txt(area0, by + 82, "Toca un valor para agregarlo a este tipo.", fuente("Light", 11), GRIS, "lm")
            boton_primario(L, x1 - 30 - 110, by + 62, x1 - 30, by + 62 + 34, "Guardar")
            boton_secundario(L, x1 - 30 - 110 - 10 - 110, by + 62, x1 - 30 - 110 - 10, by + 62 + 34, "Cancelar", "normal", 12.5)
        y += h
    L.rect(x0, top, x1, y, line=LINEA, w=1.2, r=8)
    if hover_pos:
        tx, ty = hover_pos[0] - 24, hover_pos[1]
        L.rect(tx - 52, ty - 12, tx, ty + 12, fill=GRIS_OSC, r=6)
        L.d.polygon([(L.P(tx - 1), L.P(ty - 5)), (L.P(tx - 1), L.P(ty + 5)), (L.P(tx + 5), L.P(ty))], fill=GRIS_OSC)
        L.txt(tx - 26, ty, "Editar", fuente("Regular", 11), BLANCO, "mm")
    y += 16
    y = parrafo(L, pad, y, "El tipo Internacionalización en casa es base: se asigna a todo el reporte de internacionalización en casa y no se elimina. "
                "Los cambios se guardan al instante.", W - 2 * pad - 160, "Light", 11.5, GRIS) + 2
    boton_primario(L, W - pad - 130, y - 42, W - pad, y - 2, "Listo")
    H = int(y + 6 + 24)
    recortar(L, H)
    cerrar_modal(L)
    return L


# =====================================================================
#  generación
# =====================================================================
reducir(sobre(ventana_config(1060, hover=("btn", 3)).img, modal_equivalencias_instituciones(980).img)).save(f"{OUT}/modal_equivalencias_instituciones.png")
reducir(sobre(ventana_config(1060, hover=("btn", 4)).img, modal_equivalencias_programas(980).img)).save(f"{OUT}/modal_equivalencias_programas.png")
reducir(sobre(ventana_config(1060, hover=("btn", 5)).img, modal_tipos_persona(980).img)).save(f"{OUT}/modal_tipos_persona.png")
print("listo")
