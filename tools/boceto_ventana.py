# -*- coding: utf-8 -*-
"""Boceto v3 de la ventana (identidad Areandina).
Uso: python3 -I boceto_v3.py <carpeta_marca> <carpeta_salida>
Genera: ventana_principal.png, ventana_responsiva.png, textos_ayuda.png y textos_ayuda.md"""
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
VERSION = "Boceto v0.11 · datos ficticios"


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
    "previsualizar": {
        "titulo": "Previsualizar cuadro",
        "bloques": [
            ("p", [R("Muestra "), B("cómo quedaría el cuadro"), R(" con tus archivos y la configuración actual, "
                     "sin crear ningún archivo.")]),
            ("p", [R("Sirve para detectar problemas antes de generar. Se activa al elegir la carpeta y el programa.")]),
            ("p", [R("Dentro encontrarás las cifras, los avisos y las primeras filas del cuadro.")]),
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
    est_p = "hover" if hover == "previsualizar" else "normal"
    if not estrecha:
        boton_primario(L, M, y, M + 290, y + 46, "Generar cuadro maestro", est_g)
        boton_secundario(L, M + 304, y, M + 304 + 190, y + 46, "Previsualizar cuadro", est_p, 13)
        icono_ayuda(L, M + 304 + 190 + 12, y + 23, hover=(popover == "previsualizar"))
        y += 60
    else:
        boton_primario(L, M, y, W - M, y + 46, "Generar cuadro maestro", est_g)
        y += 58
        boton_secundario(L, M, y, M + 200, y + 40, "Previsualizar cuadro", est_p, 12)
        icono_ayuda(L, M + 212, y + 20, hover=(popover == "previsualizar"))
        y += 52
    boton_secundario(L, M, y, M + 160, y + 40, "Configuración", est_c, 12)
    icono_ayuda(L, M + 172, y + 20, hover=(popover == "config"))
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
    L.txt(W - M, H - 17, VERSION, fuente("Light", 10), GRIS, "rm")
    L.rect(0, 0, W - 1, H - 1, line="#9A9A9A", w=1)
    return L


def reducir(img, f=2):
    return img.resize((img.width * f // S, img.height * f // S), Image.LANCZOS)


# ---------- alerta de confirmación ----------
ALERTA = {
    "titulo": "¿Generar el cuadro maestro?",
    "resumen": [("Programa", "Fisioterapia"), ("Vigencia", "2019 a 2023"),
                ("Archivos", "14 de 15 encontrados"), ("Configuración", "modificada hoy, 13:52")],
    "aviso": "Falta 1 de 15 archivos (Movilidad 2021). Ese año quedará incompleto en el conteo.",
    "bloques": [
        ("p", [R("Se usará la "), B("configuración de cruce de datos actual"),
               R(" de los Excel: las columnas, filtros y reglas guardadas en Configuración.")]),
        ("h", "Antes de continuar, ten en cuenta"),
        ("b", [R("El resultado depende de esa configuración. Si los Excel cambiaron de columnas, nombres o filtros "
                 "y la configuración no se actualizó, el cuadro puede quedar "), B("incompleto o con datos incorrectos"), R(".")]),
        ("b", [R("El programa "), B("no modifica tus Excel originales"), R(": solo los lee y crea un archivo nuevo.")]),
        ("b", [R("Después de generarlo, abre "), B("Ver revisión"),
               R(" y confirma lo que no se pudo cruzar antes de entregar el cuadro.")]),
    ],
    "pregunta": "¿Quieres continuar?",
    "botones": ("Cancelar", "Sí, generar cuadro maestro"),
}


RADIO_ALERTA = 16


def dialogo(W=580):
    """Diálogo modal de confirmación (ventana secundaria con barra de título del sistema)."""
    tmp = Lienzo(10, 10)
    f_r, f_b = fuente("Regular", 12), fuente("Bold", 12)
    pad = 28
    inner = W - 2 * pad
    y = 32 + 24
    y += 60                                            # icono + título
    y += len(ALERTA["resumen"]) * 24 + 24 + 16          # caja de resumen
    lav = partir(tmp, [R(ALERTA["aviso"])], f_r, f_r, inner - 52)
    ah = 22 + 17 * len(lav)
    y += ah + 16
    layout = []
    for tipo, dato in ALERTA["bloques"]:
        if tipo == "h":
            y += 4; layout.append((tipo, dato, y)); y += 24
        else:
            sang = 16 if tipo == "b" else 0
            lin = partir(tmp, dato, f_r, f_b, inner - sang)
            layout.append((tipo, lin, y)); y += len(lin) * 18 + 8
    y += 6
    pregunta_y = y; y += 42
    botones_y = y; y += 40 + 26
    H = y
    D = Lienzo(W, H)
    D.rect(0, 0, W, 32, fill="#EDEDED")
    D.txt(12, 16, "Confirmar generación", fuente("Regular", 11), GRIS_OSC, "lm")
    D.cross(W - 24, 16, GRIS_OSC, 5, 1.2)
    yy = 32 + 24
    D.d.ellipse([D.P(pad), D.P(yy), D.P(pad + 40), D.P(yy + 40)], fill=NARANJA)
    D.txt(pad + 20, yy + 21, "!", fuente("Bold", 22), NEGRO, "mm")
    D.txt(pad + 56, yy + 21, ALERTA["titulo"], fuente("Bold", 19), GRIS_OSC, "lm")
    yy += 60
    cajah = len(ALERTA["resumen"]) * 24 + 24
    D.rect(pad, yy, W - pad, yy + cajah, fill=FONDO, line=LINEA, w=1, r=8)
    for i, (k, v) in enumerate(ALERTA["resumen"]):
        ry = yy + 12 + i * 24 + 12
        D.txt(pad + 16, ry, k, fuente("Bold", 11.5), GRIS_OSC, "lm")
        if k == "Archivos":
            D.d.ellipse([D.P(pad + 140), D.P(ry - 4), D.P(pad + 148), D.P(ry + 4)], fill=NARANJA)
            D.txt(pad + 156, ry, v, f_r, NEGRO, "lm")
        else:
            D.txt(pad + 140, ry, v, f_r, NEGRO, "lm")
    yy += cajah + 16
    D.rect(pad, yy, W - pad, yy + ah, fill=AVISO_BG, line=NARANJA, w=1, r=8)
    D.d.ellipse([D.P(pad + 12), D.P(yy + ah / 2 - 8), D.P(pad + 28), D.P(yy + ah / 2 + 8)], fill=NARANJA)
    D.txt(pad + 20, yy + ah / 2, "!", fuente("Bold", 11), NEGRO, "mm")
    for i, ln in enumerate(lav):
        D.txt(pad + 40, yy + 11 + 8.5 + i * 17, " ".join(t[0] for t in ln), f_r, NEGRO, "lm")
    for tipo, dato, y0 in layout:
        if tipo == "h":
            D.txt(pad, y0 + 9, dato, fuente("Bold", 12.5), VERDE_CTA, "lm")
            continue
        sang = 16 if tipo == "b" else 0
        if tipo == "b":
            D.d.ellipse([D.P(pad + 3), D.P(y0 + 6), D.P(pad + 8), D.P(y0 + 11)], fill=VERDE_CTA)
        for i, linea in enumerate(dato):
            cx = pad + sang
            for w, neg, sp in linea:
                f = f_b if neg else f_r
                if sp:
                    cx += D.tw(" ", f_r)
                D.txt(cx, y0 + 8 + i * 18, w, f, NEGRO, "lm")
                cx += D.tw(w, f)
    D.txt(pad, pregunta_y + 14, ALERTA["pregunta"], fuente("Bold", 13.5), GRIS_OSC, "lm")
    bx1 = W - pad
    bw_p = 280
    boton_primario(D, bx1 - bw_p, botones_y, bx1, botones_y + 40, ALERTA["botones"][1])
    bw_c = 120
    cx1 = bx1 - bw_p - 12
    # "Cancelar" lleva el foco inicial (Enter = Cancelar): borde grueso
    D.rect(cx1 - bw_c, botones_y, cx1, botones_y + 40, fill=BLANCO, line=VERDE_CTA, w=2.5, r=8)
    D.txt(cx1 - bw_c / 2, botones_y + 20, ALERTA["botones"][0], fuente("Bold", 13), VERDE_CTA, "mm")
    D.rect(0.5, 0.5, W - 0.5, H - 0.5, line="#9A9A9A", w=1, r=RADIO_ALERTA)
    return D.img


# ---------- 1) ventana principal: ayuda de Vigencia abierta y botón principal en hover ----------
L = ventana(760, None, popover="vigencia", hover="generar")
t = tarjeta(AYUDAS["vigencia"], 430)
poner(L.img, t, 760 - 28 - 430 - 14 + 10, 32 + 81 + 22 + 80 + 14)
reducir(L.img).save(f"{OUT}/ventana_principal.png")

# ---------- 2) responsiva: amplia y mínima (altura ajustada al contenido) ----------
amplia = ventana(1000).img
minima = ventana(560, estrecha=True).img
f = 1.4
a = amplia.resize((int(amplia.width * f / S), int(amplia.height * f / S)), Image.LANCZOS)
m = minima.resize((int(minima.width * f / S), int(minima.height * f / S)), Image.LANCZOS)
M_ = 36
cab = 60
hoja = Image.new("RGB", (a.width + m.width + 3 * M_, max(a.height, m.height) + cab + M_), "#E9E9E9")
dh = ImageDraw.Draw(hoja)
ft = ImageFont.truetype(f"{MARCA}/fuentes/BrownStd-Bold.otf", 22)
dh.text((M_, 20), "Ventana amplia (1000 px): la tabla y los campos se ensanchan", font=ft, fill=GRIS_OSC)
dh.text((a.width + 2 * M_, 20), "Ventana mínima (560 px): se apila", font=ft, fill=GRIS_OSC)
hoja.paste(a, (M_, cab))
hoja.paste(m, (a.width + 2 * M_, cab))
hoja.save(f"{OUT}/ventana_responsiva.png")

# ---------- 3) hoja con los textos de ayuda (6 tarjetas) ----------
ts = [tarjeta(AYUDAS[k], 430) for k in ("carpeta", "vigencia", "archivos")]
ts2 = [tarjeta(AYUDAS[k], 360) for k in ("previsualizar", "config", "revision")]
gap = 20
w1 = sum(t_["rgb"].width / S for t_ in ts) + 4 * gap
h1 = max(t_["rgb"].height / S for t_ in ts)
h2 = max(t_["rgb"].height / S for t_ in ts2)
hoja = Image.new("RGB", (int(w1 * S), int((h1 + h2 + 120) * S)), "#E9E9E9")
x = gap
for t_ in ts:
    poner(hoja, t_, x, 70); x += t_["rgb"].width / S + gap
x = gap
for t_ in ts2:
    poner(hoja, t_, x, 70 + h1 + 20); x += t_["rgb"].width / S + gap
k = 1.5
hoja = hoja.resize((int(hoja.width * k / S), int(hoja.height * k / S)), Image.LANCZOS)
ImageDraw.Draw(hoja).text((20, 20), "Textos de los signos de ayuda (?)", font=ft, fill=GRIS_OSC)
hoja.save(f"{OUT}/textos_ayuda.png")

# ---------- 3b) estados de los controles ----------
E = Lienzo(760, 520, fondo=BLANCO)
E.txt(28, 30, "Estados de los controles", fuente("Bold", 18), GRIS_OSC, "lm")
E.txt(28, 52, "Los colores de hover y pulsado son el verde de llamado a la acción del manual (#67882C) más oscuro.", fuente("Light", 11), GRIS, "lm")
y = 84


def fila(titulo, y):
    E.txt(28, y, titulo, fuente("Bold", 12), GRIS_OSC, "lm")
    E.d.line([E.P(28), E.P(y + 14), E.P(732), E.P(y + 14)], fill=LINEA, width=E.P(1))


def etq(x, y, t):
    E.txt(x, y, t, fuente("Light", 10.5), GRIS, "mm")


fila("Botón principal", y)
for i, (est, t_) in enumerate((("normal", "#67882C"), ("hover", "#587425 (hover)"), ("press", "#4A6320 (pulsado)"))):
    boton_primario(E, 28 + i * 190, y + 26, 28 + i * 190 + 170, y + 66, "Generar", est)
    etq(28 + i * 190 + 85, y + 78, t_)
E.rect(28 + 3 * 190, y + 26, 28 + 3 * 190 + 130, y + 66, fill="#D9D9D9", r=8)
E.txt(28 + 3 * 190 + 65, y + 46, "Generar", fuente("Bold", 14), "#9A9A9A", "mm")
etq(28 + 3 * 190 + 65, y + 78, "desactivado")
y += 108
fila("Botón secundario", y)
boton_secundario(E, 28, y + 26, 198, y + 66, "Configuración", "normal"); etq(113, y + 78, "normal")
boton_secundario(E, 218, y + 26, 388, y + 66, "Configuración", "hover"); etq(303, y + 78, "hover: relleno verde claro #EAF2DD")
E.rect(408, y + 26, 578, y + 66, fill=BLANCO, line="#C8C8C8", w=1.5, r=8)
E.txt(493, y + 46, "Previsualizar cuadro", fuente("Bold", 13), "#9A9A9A", "mm"); etq(493, y + 78, "desactivado")
for k_, t_ in enumerate(("Previsualizar: hasta elegir", "carpeta y programa.", "Ver revisión: hasta generar.")):
    E.txt(596, y + 34 + k_ * 16, t_, fuente("Light", 10.5), GRIS, "lm")
y += 108
fila("Campos", y)
campo(E, 28, y + 26, 238, y + 58, "Fisioterapia", flecha=True); etq(133, y + 72, "normal")
campo(E, 258, y + 26, 468, y + 58, "Fisioterapia", flecha=True, foco=True); etq(363, y + 72, "con foco: borde verde grueso")
E.rect(488, y + 26, 732, y + 58, fill=BLANCO, line=MAGENTA, w=2, r=6)
E.txt(500, y + 42, "2024", fuente("Regular", 12), NEGRO, "lm")
etq(610, y + 72, "error: borde magenta + mensaje")
E.txt(488, y + 88, "“Desde” no puede ser mayor que “Hasta”.", fuente("Regular", 11), MAGENTA, "lm")
y += 120
fila("Signo de ayuda (?)", y)
icono_ayuda(E, 28, y + 40, False); etq(38, y + 66, "normal")
icono_ayuda(E, 118, y + 40, True); etq(128, y + 66, "hover")
E.txt(190, y + 40, "Al pasar el cursor o hacer clic se abre la tarjeta de ayuda; se cierra con otro clic o con Esc.", fuente("Light", 11), GRIS_OSC, "lm")
y += 90
E.rect(0, 0, 759, 519, line="#9A9A9A", w=1)
reducir(E.img).save(f"{OUT}/estados_controles.png")

# ---------- 3c) alerta de confirmación sobre la ventana (atenuada) ----------
base = ventana(760, None, hover="generar_press").img
oscuro = Image.new("RGB", base.size, "#000000")
base = Image.blend(base, oscuro, 0.45)
dl = dialogo(580)
dx = int((base.width - dl.width) / 2)
dy = int((base.height - dl.height) / 2)
mk = Image.new("L", dl.size, 0)
ImageDraw.Draw(mk).rounded_rectangle([0, 0, dl.width - 1, dl.height - 1], radius=RADIO_ALERTA * S, fill=255)
m3 = 40 * S // 3
sm_big = Image.new("L", (dl.width + 2 * m3, dl.height + 2 * m3), 0)
ImageDraw.Draw(sm_big).rounded_rectangle([m3, m3 + 12, sm_big.width - m3, sm_big.height - m3 + 12], radius=RADIO_ALERTA * S, fill=120)
sm_big = sm_big.filter(ImageFilter.GaussianBlur(14))
base.paste(Image.new("RGB", sm_big.size, "#000000"), (dx - m3, dy - m3), sm_big)
base.paste(dl, (dx, dy), mk)
reducir(base).save(f"{OUT}/alerta_confirmacion.png")

# ---------- 4) textos en Markdown (editables) ----------
def md(segs):
    out = []
    for t, neg in segs:
        if neg:
            lead, trail = t[:len(t) - len(t.lstrip())], t[len(t.rstrip()):]
            out.append(f"{lead}**{t.strip()}**{trail}")
        else:
            out.append(t)
    return "".join(out).strip()


with open(f"{OUT}/textos_ayuda.md", "w", encoding="utf-8") as fh:
    fh.write("# Textos de ayuda de la ventana (signos de interrogación)\n\n"
             "Texto de cada ayuda tal como se muestra en la ventana. Se editan aquí y se copian al programa.\n")
    for k, a_ in AYUDAS.items():
        fh.write(f"\n## {a_['titulo']}\n\n")
        for tipo, dato in a_["bloques"]:
            if tipo == "p":
                fh.write(md(dato) + "\n\n")
            elif tipo == "h":
                fh.write(f"**{dato}**\n\n")
            elif tipo == "chips":
                fh.write("Ejemplos: " + ", ".join(f"`{c}`" for c in dato) + "\n\n")
            elif tipo == "b":
                fh.write("- " + md(dato) + "\n")
            elif tipo == "ok":
                fh.write("- ✔ " + md(dato) + "\n")
            elif tipo == "mal":
                fh.write("- ✖ " + md(dato) + "\n")
        fh.write("\n")
    fh.write("## Alerta al pulsar «Generar cuadro maestro»\n\n"
             "Ventana modal: el usuario debe confirmar o cancelar. El foco inicial está en **Cancelar** "
             "(Enter cancela). Los datos del resumen son de ejemplo; en el programa salen de lo elegido.\n\n")
    fh.write(f"**{ALERTA['titulo']}**\n\n")
    for k_, v_ in ALERTA["resumen"]:
        fh.write(f"- {k_}: {v_}\n")
    fh.write(f"\n> ⚠ {ALERTA['aviso']} *(solo aparece si faltan archivos)*\n\n")
    for tipo, dato in ALERTA["bloques"]:
        if tipo == "p":
            fh.write(md(dato) + "\n\n")
        elif tipo == "h":
            fh.write(f"**{dato}**\n\n")
        elif tipo == "b":
            fh.write("- " + md(dato) + "\n")
    fh.write(f"\n**{ALERTA['pregunta']}**\n\nBotones: [{ALERTA['botones'][0]}] [{ALERTA['botones'][1]}]\n")
print("listo")
