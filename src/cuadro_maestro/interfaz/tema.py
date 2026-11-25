"""Colores, tipografías y controles con la identidad de Areandina (docs/identidad.md, mockup 05).

Lo redondeado y los iconos se dibujan con Pillow y se suavizan (graficos.py): botones, campos, listas, cajas,
chips, interruptores, casillas y los «?». Las cajas son marcos de ttk con una imagen que se estira por el centro
(las esquinas no se deforman). Brown Std se carga solo para el programa (Windows: AddFontResourceExW con FR_PRIVATE).
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from PIL import ImageTk

from ..recursos import carpeta_recursos
from . import graficos as G
from .ayudas import AYUDAS

VERDE, VERDE_CTA, VERDE_HOVER, VERDE_PULSADO = "#7FB536", "#67882C", "#587425", "#4A6320"
MAGENTA, NARANJA, GRIS, GRIS_OSC = "#E6007E", "#F59C2F", "#606060", "#282828"
BLANCO, NEGRO, FONDO, LINEA = "#FFFFFF", "#000000", "#F5F5F5", "#D9D9D9"
TINTE_VERDE, AVISO_BG, AVISO_TXT, ROSA_SUAVE = "#EAF2DD", "#FFF3E3", "#9A5B00", "#FDE6F2"
OK_BG, OK_TXT, DESACT_BG, DESACT_TXT, DESACT_BORDE = "#EEF5E3", "#4A6320", "#D9D9D9", "#9A9A9A", "#C8C8C8"
CHIP_VERDE = "#E3EED2"
RADIO = 8            # esquinas de botones, campos y cajas (mockups)
RADIO_GRANDE = 12    # tarjetas y paneles de ayuda

F: dict[str, tkfont.Font] = {}


def fondo_de(w) -> str:
    """Color de fondo de un control (los marcos de ttk guardan el suyo en `_fondo`)."""
    if hasattr(w, "_fondo"):
        return w._fondo
    try:
        return w.cget("bg")
    except tk.TclError:
        try:
            return w.cget("background") or BLANCO
        except tk.TclError:
            return BLANCO


# ---------------------------------------------------------------- tipografías y estilos de ttk
def cargar_fuentes(raiz: tk.Tk) -> str:
    """Carga Brown Std (si está junto al programa), crea las fuentes con nombre y los estilos. Devuelve la familia."""
    carpeta = carpeta_recursos() / "marca" / "fuentes"
    if sys.platform == "win32" and carpeta.is_dir():
        try:
            import ctypes
            for otf in carpeta.glob("*.otf"):
                ctypes.windll.gdi32.AddFontResourceExW(str(otf), 0x10, 0)   # FR_PRIVATE: sin instalar
        except Exception:   # noqa: BLE001
            pass
    familias = set(tkfont.families(raiz))
    base = next((f for f in ("Brown Std", "BrownStd") if f in familias), None)
    respaldo = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"
    familia = base or respaldo
    ligera = next((f for f in ("Brown Std Light", "BrownStd Light") if f in familias), familia)
    tam = {  # tamaños en píxeles (negativos en Tk), medidos en los mockups a escala 1
        "app_titulo": (familia, -26, "bold"), "app_sub": (ligera, -15, "normal"),
        "seccion": (familia, -16, "bold"), "cuerpo": (familia, -15, "normal"), "cuerpo_b": (familia, -15, "bold"),
        "suave": (ligera, -14, "normal"), "pequena": (familia, -13, "normal"), "pequena_b": (familia, -13, "bold"),
        "boton": (familia, -16, "bold"), "boton_peq": (familia, -14, "bold"), "modal_titulo": (familia, -24, "bold"),
        "cifra": (familia, -30, "bold"), "barra": (familia, -13, "normal"),
    }
    for nombre, (fam, px, peso) in tam.items():
        F[nombre] = tkfont.Font(raiz, family=fam, size=px, weight=peso)
    _estilos(raiz)
    return familia


def _guardar(raiz, imagen):
    """Las imágenes de ttk deben seguir vivas mientras exista la ventana."""
    if not hasattr(raiz, "_imagenes_ttk"):
        raiz._imagenes_ttk = []
    foto = ImageTk.PhotoImage(imagen, master=raiz)
    raiz._imagenes_ttk.append(foto)
    return foto


def _estilos(raiz):
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    # Campo: borde gris de 1 px; verde de 2 px con foco; magenta con error; naranja si la regla cambió.
    n = 36

    def campo(borde, grosor, relleno=BLANCO):
        return _guardar(raiz, G.caja_pil(n * 4, n + 24, RADIO, relleno, borde, grosor, exterior=BLANCO))

    normal, foco = campo(GRIS, 1), campo(VERDE_CTA, 2)
    desact = campo(LINEA, 1, FONDO)
    for nombre, img in (("CM.campo", normal), ("CM.campo.error", campo(MAGENTA, 2)),
                        ("CM.campo.cambiada", campo(NARANJA, 2))):
        if nombre == "CM.campo":
            estilo.element_create(nombre, "image", img, ("disabled", desact), ("focus", foco), border=10,
                                  padding=(14, 11, 10, 11), sticky="nsew", width=36, height=36)
        else:
            estilo.element_create(nombre, "image", img, border=10, padding=(14, 11, 10, 11), sticky="nsew",
                                  width=36, height=36)
    flecha = _guardar(raiz, G.triangulo(28, 20, GRIS_OSC))
    flecha_d = _guardar(raiz, G.triangulo(28, 20, DESACT_TXT))
    estilo.element_create("CM.flecha", "image", flecha, ("disabled", flecha_d), sticky="")
    for estilo_nombre, campo_el in (("CM.TCombobox", "CM.campo"), ("Error.CM.TCombobox", "CM.campo.error"),
                                    ("Cambiada.CM.TCombobox", "CM.campo.cambiada")):
        estilo.layout(estilo_nombre, [(campo_el, {"sticky": "nsew", "children": [
            ("CM.flecha", {"side": "right", "sticky": ""}),
            ("Combobox.padding", {"expand": "1", "sticky": "nsew", "children": [
                ("Combobox.textarea", {"sticky": "nsew"})]})]})])
        estilo.configure(estilo_nombre, padding=0, foreground=NEGRO, arrowsize=0)
        estilo.map(estilo_nombre, foreground=[("disabled", DESACT_TXT)], fieldbackground=[("readonly", BLANCO)],
                   selectbackground=[("!focus", BLANCO), ("focus", BLANCO)], selectforeground=[("", NEGRO)])
    for estilo_nombre, campo_el in (("CM.TEntry", "CM.campo"), ("Error.CM.TEntry", "CM.campo.error")):
        estilo.layout(estilo_nombre, [(campo_el, {"sticky": "nsew", "children": [
            ("Entry.padding", {"sticky": "nsew", "children": [("Entry.textarea", {"sticky": "nsew"})]})]})])
        estilo.configure(estilo_nombre, padding=0, foreground=NEGRO, insertcolor=NEGRO)
        estilo.map(estilo_nombre, foreground=[("disabled", DESACT_TXT)])
    raiz.option_add("*TCombobox*Listbox.font", F["cuerpo"])
    raiz.option_add("*TCombobox*Listbox.selectBackground", TINTE_VERDE)
    raiz.option_add("*TCombobox*Listbox.selectForeground", NEGRO)
    raiz.option_add("*TCombobox*Listbox.borderWidth", 0)
    # Barra de desplazamiento delgada y redondeada, sin flechas.
    barra = _guardar(raiz, G.caja_pil(10, 160, 5, "#C4C4C4"))
    barra_h = _guardar(raiz, G.caja_pil(10, 160, 5, "#9A9A9A"))
    estilo.element_create("CM.pulgar", "image", barra, ("active", barra_h), ("pressed", barra_h), border=(0, 6),
                          sticky="ns", width=10, height=40)
    estilo.layout("CM.Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [
        ("CM.pulgar", {"expand": "1", "sticky": "nsew"})]})])
    estilo.configure("CM.Vertical.TScrollbar", troughcolor=BLANCO, background=BLANCO, bordercolor=BLANCO,
                     lightcolor=BLANCO, darkcolor=BLANCO, gripcount=0, width=10)
    estilo.configure("CM.Horizontal.TProgressbar", troughcolor="#E3E3E3", background=VERDE_CTA, bordercolor="#E3E3E3",
                     lightcolor=VERDE_CTA, darkcolor=VERDE_CTA, thickness=10)


# Las esquinas de los campos se pintan con el color de lo que tienen detrás: en Windows lo transparente de una imagen de
# ttk se ve gris. Por eso hay una variante de cada estilo por color de fondo ("F" + color + "." + estilo).
_BASES_CAMPO = {"CM.TCombobox": ("CM.campo", True), "Error.CM.TCombobox": ("CM.campo.error", True),
                "Cambiada.CM.TCombobox": ("CM.campo.cambiada", True), "CM.TEntry": ("CM.campo", False),
                "Error.CM.TEntry": ("CM.campo.error", False)}
_COLORES_CAMPO = {"CM.campo": (GRIS, 1), "CM.campo.error": (MAGENTA, 2), "CM.campo.cambiada": (NARANJA, 2)}


def _estilo_campo(raiz, base, fondo):
    fondo = fondo.upper() if fondo.startswith("#") else fondo
    if base not in _BASES_CAMPO or fondo == BLANCO:
        return base
    try:
        r, g, b = (v // 257 for v in raiz.winfo_rgb(fondo))
    except tk.TclError:
        return base
    hexa = "%02X%02X%02X" % (r, g, b)
    if hexa == BLANCO[1:]:
        return base
    nombre = f"F{hexa}.{base}"
    hechos = raiz.__dict__.setdefault("_estilos_campo", set())
    if nombre in hechos:
        return nombre
    estilo = ttk.Style(raiz)
    el, es_combo = _BASES_CAMPO[base]
    el_f = f"{el}@{hexa}"
    if el_f not in hechos:
        borde, grosor = _COLORES_CAMPO[el]
        ext = "#" + hexa
        img = _guardar(raiz, G.caja_pil(144, 60, RADIO, BLANCO, borde, grosor, exterior=ext))
        if el == "CM.campo":
            foco = _guardar(raiz, G.caja_pil(144, 60, RADIO, BLANCO, VERDE_CTA, 2, exterior=ext))
            desact = _guardar(raiz, G.caja_pil(144, 60, RADIO, FONDO, LINEA, 1, exterior=ext))
            estilo.element_create(el_f, "image", img, ("disabled", desact), ("focus", foco), border=10,
                                  padding=(14, 11, 10, 11), sticky="nsew", width=36, height=36)
        else:
            estilo.element_create(el_f, "image", img, border=10, padding=(14, 11, 10, 11), sticky="nsew",
                                  width=36, height=36)
        hechos.add(el_f)
    if es_combo:
        estilo.layout(nombre, [(el_f, {"sticky": "nsew", "children": [
            ("CM.flecha", {"side": "right", "sticky": ""}),
            ("Combobox.padding", {"expand": "1", "sticky": "nsew", "children": [
                ("Combobox.textarea", {"sticky": "nsew"})]})]})])
    else:
        estilo.layout(nombre, [(el_f, {"sticky": "nsew", "children": [
            ("Entry.padding", {"sticky": "nsew", "children": [("Entry.textarea", {"sticky": "nsew"})]})]})])
    for opcion in ("padding", "foreground", "arrowsize", "insertcolor"):
        v = estilo.lookup(base, opcion)
        if v != "":
            estilo.configure(nombre, **{opcion: v})
    for opcion in ("foreground", "fieldbackground", "selectbackground", "selectforeground"):
        m = estilo.map(base, opcion)
        if m:
            estilo.map(nombre, **{opcion: m})
    hechos.add(nombre)
    return nombre


def poner_estilo(w, base=None):
    """Pone a un campo o lista desplegable el estilo `base` con las esquinas del color de su fondo."""
    if base is None:
        base = str(w.cget("style"))
        if base.startswith("F") and "." in base and base.split(".", 1)[1] in _BASES_CAMPO:
            base = base.split(".", 1)[1]
    try:
        w.configure(style=_estilo_campo(w.winfo_toplevel(), base, fondo_de(w.master)))
    except tk.TclError:
        pass


def estilo_marco(padre, relleno, borde=None, grosor=0, radio=RADIO, exterior=None, recorte=0,
                 esquinas=(True, True, True, True), banda=None) -> str:
    """Estilo de ttk.Frame con fondo redondeado que se estira por el centro. `recorte` quita píxeles de cada lado
    (para la cabecera de una tabla, que va pegada por dentro al borde de la tabla)."""
    raiz = padre._root()
    estilos = raiz.__dict__.setdefault("_estilos_marco", {})
    clave = (relleno, borde, grosor, radio, exterior, recorte, esquinas, banda)
    if clave not in estilos:
        nombre = f"M{len(estilos)}"
        b = max(radio + grosor, banda[1] + 2 if banda else 0)
        n = 2 * b + 96 + 2 * recorte   # centro grande: ttk lo repite en mosaico y con 6 px eran miles de copias
        img = G.caja_pil(n, n, radio, relleno, borde, grosor, exterior, esquinas, banda)
        if recorte:
            img = img.crop((recorte, recorte, n - recorte, n - recorte))
        # El tamaño mínimo es el de antes (2·borde + 6): la imagen es más grande solo para que el centro se
        # repita menos veces, no para agrandar las cajas pequeñas.
        minimo = 2 * b + 6
        ttk.Style(raiz).element_create(nombre + ".fondo", "image", _guardar(raiz, img), border=b, sticky="nsew",
                                       width=minimo, height=minimo)
        ttk.Style(raiz).layout(nombre + ".TFrame", [(nombre + ".fondo", {"sticky": "nsew"})])
        estilos[clave] = nombre + ".TFrame"
    return estilos[clave]


class Caja(ttk.Frame):
    """Marco redondeado: `borde` de `grosor` px, relleno `fondo`. Sus hijos van con fondo `fondo`.

    El relleno interno (padx, pady) debe ser al menos ~ un tercio del radio para que lo de dentro no tape las esquinas.
    """

    def __init__(self, padre, fondo=BLANCO, borde=LINEA, grosor=1, radio=RADIO, padx=None, pady=None, exterior=None,
                 esquinas=(True, True, True, True), recorte=0, exacto=False, banda=None, relleno=None):
        exterior = exterior or fondo_de(padre)
        estilo = estilo_marco(padre, fondo, borde if grosor else None, grosor, radio, exterior, recorte, esquinas,
                              banda)
        minimo = 0 if exacto else grosor + max(2, radio // 3)
        if banda:
            minimo = max(minimo, banda[1])
        px = minimo if padx is None else max(padx, minimo)
        py = minimo if pady is None else max(pady, minimo)
        super().__init__(padre, style=estilo, padding=relleno or (px, py))
        self._fondo = fondo


def borde(padre, color=LINEA, grosor=1, fondo=BLANCO, radio=RADIO, padx=None, pady=None):
    """Reemplazo de «tk.Frame(bg=color, padx=1, pady=1)»: caja redondeada; lo de dentro con fondo `fondo`."""
    return Caja(padre, fondo=fondo, borde=color, grosor=grosor, radio=radio, padx=padx, pady=pady)


def tarjeta(padre, color, borde=LINEA, fondo=BLANCO, padx=16, pady=10, banda=5):
    """Tarjeta redondeada con una franja de color a la izquierda (cifras, avisos de la revisión, errores)."""
    return Caja(padre, fondo=fondo, borde=borde, grosor=1, radio=RADIO + 2, padx=padx + banda, pady=pady,
                banda=(color, banda))


def tabla(padre, fondo=BLANCO, pie=False):
    """Contenedor de una tabla: borde gris redondeado de 1 px y sin relleno (la cabecera va pegada al borde).

    `pie=True` deja abajo un margen del tamaño de la esquina (tablas cuyas filas no pueden redondearse: rejillas y
    listas con desplazamiento); si no, la última fila debe hacerse con `fila(..., ultima=True)`."""
    c = Caja(padre, fondo=fondo, borde=LINEA, grosor=1, radio=RADIO + 2, padx=1, pady=1, exacto=True,
             relleno=(1, 1, 1, RADIO + 1) if pie else None)
    c._tabla = True
    return c


def cabecera(tabla_, padx=14, pady=9, relleno=None):
    """Cabecera oscura de una tabla con las esquinas de arriba redondeadas (mockups 01, 15, 22…). Lo de dentro no
    debe tocar las esquinas: con `padx` o `pady` en 0 usar `relleno=(4, 4, 4, 0)`."""
    exterior = fondo_de(tabla_.master)
    c = Caja(tabla_, fondo=GRIS_OSC, borde=LINEA, grosor=1, radio=RADIO + 2, padx=padx, pady=pady, exterior=exterior,
             esquinas=(True, True, False, False), recorte=1, exacto=True, relleno=relleno)
    return c


def fila(tabla_, fondo, padx=14, pady=8, ultima=False):
    """Fila de una tabla; la última lleva las esquinas de abajo redondeadas para no tapar el borde."""
    if not ultima:
        return tk.Frame(tabla_, bg=fondo, padx=padx, pady=pady)
    c = Caja(tabla_, fondo=fondo, borde=LINEA, grosor=1, radio=RADIO + 2, padx=padx, pady=pady,
             exterior=fondo_de(tabla_.master), esquinas=(False, False, True, True), recorte=1, exacto=True)
    return c


# ---------------------------------------------------------------- botones y enlaces
class Boton(tk.Label):
    """Botón principal (relleno verde) o secundario (borde verde), redondeado. Estados: normal, hover, pulsado,
    desactivado (mockup 05)."""

    def __init__(self, padre, texto, comando=None, tipo="primario", fuente="boton", ancho=None, alto=44):
        self.exterior = fondo_de(padre)
        super().__init__(padre, text=texto, font=F[fuente], compound="center", bd=0, highlightthickness=0,
                         bg=self.exterior, activebackground=self.exterior, cursor="hand2", padx=0, pady=0)
        self.tipo, self.comando, self.activo, self.fuente = tipo, comando, True, fuente
        self.ancho = ancho or F[fuente].measure(texto) + 56
        self.alto = alto
        self.etiqueta = self
        self.bind("<Enter>", lambda e: self._pintar("hover"))
        self.bind("<Leave>", lambda e: self._pintar("normal"))
        self.bind("<ButtonPress-1>", lambda e: self._pintar("pulsado"))
        self.bind("<ButtonRelease-1>", self._soltar)
        self._pintar("normal")

    def _soltar(self, evento):
        dentro = self.winfo_containing(evento.x_root, evento.y_root) is self
        self._pintar("hover" if dentro else "normal")
        if dentro and self.activo and self.comando:
            self.comando()

    def _pintar(self, estado):
        if not self.activo:
            relleno, borde, texto = (DESACT_BG, None, DESACT_TXT) if self.tipo == "primario" else \
                (BLANCO, DESACT_BORDE, DESACT_TXT)
            cursor = "arrow"
        elif self.tipo == "peligro":
            relleno = {"hover": "#C4006B", "pulsado": "#A3005A"}.get(estado, MAGENTA)
            borde, texto, cursor = None, BLANCO, "hand2"
        elif self.tipo == "primario":
            relleno = {"hover": VERDE_HOVER, "pulsado": VERDE_PULSADO}.get(estado, VERDE_CTA)
            borde, texto, cursor = None, BLANCO, "hand2"
        else:
            relleno = {"hover": TINTE_VERDE, "pulsado": "#DCE9C8"}.get(estado, BLANCO)
            borde, texto, cursor = VERDE_CTA, VERDE_CTA, "hand2"
        img = G.caja(self, self.ancho, self.alto, RADIO, relleno, borde, 2 if borde else 0)
        self.configure(image=img, fg=texto, activeforeground=texto, cursor=cursor)
        self._img = img

    def activar(self, si=True):
        self.activo = bool(si)
        self._pintar("normal")

    def texto(self, t):
        self.configure(text=t)


class Enlace(tk.Label):
    """Texto verde subrayado (Actualizar, Ver revisión, Abrir carpeta). Gris cuando está desactivado."""

    def __init__(self, padre, texto, comando=None, fuente="cuerpo_b"):
        self._fuente = tkfont.Font(font=F[fuente])
        self._fuente.configure(underline=True)
        super().__init__(padre, text=texto, font=self._fuente, bg=fondo_de(padre), fg=VERDE_CTA, cursor="hand2")
        self.comando, self.activo = comando, True
        self.bind("<Button-1>", lambda e: self.activo and self.comando and self.comando())

    def activar(self, si=True):
        self.activo = bool(si)
        self._fuente.configure(underline=self.activo)
        self.configure(fg=VERDE_CTA if si else DESACT_TXT, cursor="hand2" if si else "arrow")


# ---------------------------------------------------------------- signo de ayuda
class Ayuda(tk.Label):
    """Círculo «?»: al pasar el puntero se rellena; al hacer clic abre la ayuda (mockup 04). Esc o clic fuera la cierran."""

    abierta: "Ayuda | None" = None

    def __init__(self, padre, clave, d=26):
        self.fondo = fondo_de(padre)
        super().__init__(padre, bd=0, highlightthickness=0, bg=self.fondo, cursor="hand2")
        self.clave, self.d, self.ventana = clave, d, None
        self._dibujar(False)
        self.bind("<Enter>", lambda e: self._dibujar(True))
        self.bind("<Leave>", lambda e: self._dibujar(self.ventana is not None))
        self.bind("<Button-1>", lambda e: self.alternar())

    def _dibujar(self, lleno):
        self.configure(image=G.ayuda(self, self.d, lleno, self.fondo))

    def alternar(self):
        if self.ventana:
            self.cerrar()
            return
        if Ayuda.abierta:
            Ayuda.abierta.cerrar()
        Ayuda.abierta = self
        self.ventana = PanelAyuda(self, AYUDAS[self.clave])
        self._dibujar(True)

    def cerrar(self):
        if self.ventana:
            self.ventana.destroy()
        self.ventana = None
        Ayuda.abierta = None
        self._dibujar(False)


def ancho_ayuda(ayuda: dict) -> int:
    """El ancho se adapta al contenido (mockup 04): las ayudas cortas son más angostas que las largas."""
    largo = len(ayuda["titulo"]) + sum(len(t) for tipo, c in ayuda["bloques"] if tipo not in ("h", "chips")
                                       for t, _ in c)
    return 400 if largo < 320 else 480 if largo < 650 else 560


class PanelAyuda(tk.Toplevel):
    TRANSPARENTE = "#FF00FE"

    def __init__(self, ancla: Ayuda, ayuda: dict, ancho=None):
        super().__init__(ancla)
        self.overrideredirect(True)
        ancho = ancho or ancho_ayuda(ayuda)
        exterior = BLANCO
        if sys.platform == "win32":           # esquinas redondeadas de verdad: lo de fuera se vuelve transparente
            try:
                self.attributes("-transparentcolor", self.TRANSPARENTE)
                exterior = self.TRANSPARENTE
            except tk.TclError:
                pass
        self.configure(bg=exterior)
        marco = Caja(self, fondo=BLANCO, borde=VERDE, grosor=2, radio=RADIO_GRANDE, padx=20, pady=16,
                     exterior=exterior)
        marco.pack(fill="both", expand=True)
        cuerpo = tk.Frame(marco, bg=BLANCO)
        cuerpo.pack(fill="both", expand=True)
        tk.Label(cuerpo, text=ayuda["titulo"], font=F["seccion"], bg=BLANCO, fg=GRIS_OSC, anchor="w").pack(fill="x")
        tk.Frame(cuerpo, bg=VERDE, height=4, width=64).pack(anchor="w", pady=(5, 10))
        texto = tk.Text(cuerpo, wrap="word", bd=0, bg=BLANCO, font=F["pequena"], width=1, height=1,
                        padx=0, pady=0, cursor="arrow", highlightthickness=0, spacing1=2, spacing2=3, spacing3=6)
        texto.tag_configure("b", font=F["pequena_b"])
        texto.tag_configure("h", font=F["pequena_b"], foreground=VERDE_CTA, spacing1=8)
        texto.tag_configure("vineta", lmargin1=0, lmargin2=20)
        for tipo, contenido in ayuda["bloques"]:
            if tipo == "h":
                texto.insert("end", contenido + "\n", "h")
            elif tipo == "chips":
                fila_chips = tk.Frame(texto, bg=BLANCO)
                for c in contenido:
                    chip(fila_chips, c, "gris", fuente="pequena").pack(side="left", padx=(0, 6), pady=2)
                texto.window_create("end", window=fila_chips)
                texto.insert("end", "\n")
            else:
                etiquetas = ("vineta",) if tipo in ("b", "ok", "mal") else ()
                if tipo == "b":
                    texto.image_create("end", image=G.punto(texto, VERDE_CTA, 7, BLANCO), padx=4)
                    texto.insert("end", "   ", etiquetas)
                elif tipo in ("ok", "mal"):
                    texto.image_create("end", image=G.simbolo(texto, tipo, 15, BLANCO, relleno=False))
                    texto.insert("end", "  ", etiquetas)
                for t, negrita in contenido:
                    texto.insert("end", t, etiquetas + (("b",) if negrita else ()))
                texto.insert("end", "\n")
        texto.delete("end-2c", "end-1c")
        texto.configure(state="disabled")
        texto.configure(width=max(10, ancho // max(1, F["pequena"].measure("0"))))
        texto.pack(fill="both", expand=True)
        cuerpo.configure(width=ancho)
        self.update_idletasks()
        texto.configure(width=max(10, round(ancho / F["pequena"].measure("0"))))
        self.update_idletasks()
        lineas = texto.count("1.0", "end-1c", "displaylines")
        texto.configure(height=min(int(lineas[0]) if lineas else 10, 30))
        self.update_idletasks()
        x = min(ancla.winfo_rootx() - 20, ancla.winfo_screenwidth() - self.winfo_reqwidth() - 10)
        y = ancla.winfo_rooty() + ancla.winfo_height() + 6
        if y + self.winfo_reqheight() > ancla.winfo_screenheight():
            y = max(10, ancla.winfo_rooty() - self.winfo_reqheight() - 6)
        self.geometry(f"+{max(10, x)}+{y}")
        raiz = ancla.winfo_toplevel()
        self._cierre = raiz.bind("<Button-1>", self._clic_fuera, add="+")
        raiz.bind("<Escape>", lambda e: ancla.cerrar(), add="+")
        self.bind("<Escape>", lambda e: ancla.cerrar())
        self.ancla = ancla

    def _clic_fuera(self, evento):
        w = evento.widget
        if w is self.ancla or str(w).startswith(str(self)):
            return
        self.ancla.cerrar()


# ---------------------------------------------------------------- campos
class Campo(tk.Frame):
    """Entrada de texto redondeada: borde gris; verde con el foco; magenta con error (mockup 05)."""

    def __init__(self, padre, variable, solo_lectura=False, guia=None):
        fondo = fondo_de(padre)
        super().__init__(padre, bg=fondo)
        self.variable = variable
        self.entrada = ttk.Entry(self, textvariable=variable, font=F["cuerpo"], style="CM.TEntry")
        poner_estilo(self.entrada, "CM.TEntry")
        self.entrada.pack(fill="both", expand=True)
        if solo_lectura:
            self.entrada.configure(state="readonly")
        if guia:                     # texto guía en gris mientras el campo está vacío (no se guarda en la variable)
            self.guia = tk.Label(self, text=guia, font=F["cuerpo"], bg=BLANCO, fg=DESACT_TXT, cursor="xterm")
            self.guia.bind("<Button-1>", lambda e: self.entrada.focus_set())
            variable.trace_add("write", lambda *a: self._guia())
            self.entrada.bind("<FocusIn>", lambda e: self.guia.place_forget(), add="+")
            self.entrada.bind("<FocusOut>", lambda e: self._guia(), add="+")
            self._guia()

    def _guia(self):
        try:
            if self.variable.get() or self.focus_get() is self.entrada:
                self.guia.place_forget()
            else:
                self.guia.place(x=14, rely=0.5, anchor="w")
        except (tk.TclError, KeyError):
            pass

    def error(self, si=True):
        poner_estilo(self.entrada, "Error.CM.TEntry" if si else "CM.TEntry")


class Opciones(ttk.Combobox):
    """Lista desplegable de solo lectura que muestra textos y devuelve valores internos.

    `pares` = [(valor, texto), ...]. Si el valor actual no está en la lista se muestra tal cual (no se pierde).
    La rueda del ratón encima no cambia la opción: desplaza la ventana (antes cambiaba reglas sin querer).
    """

    def __init__(self, padre, pares, valor, al_cambiar=None, ancho=None, editable=False, estilo="CM.TCombobox"):
        self.pares = list(pares)
        if valor is not None and all(v != valor for v, _ in self.pares):
            self.pares.append((valor, str(valor)))
        self.variable = tk.StringVar(value=self.texto_de(valor))
        super().__init__(padre, textvariable=self.variable, values=[t for _, t in self.pares],
                         state="normal" if editable else "readonly", style=estilo, font=F["cuerpo"],
                         height=14, **({"width": ancho} if ancho else {}))
        self.al_cambiar, self.editable = al_cambiar, editable
        self.bind("<<ComboboxSelected>>", lambda e: (self.selection_clear(), self._cambio()))
        if editable:
            self.bind("<FocusOut>", lambda e: self._cambio(), add="+")
            self.bind("<Return>", lambda e: self._cambio(), add="+")
        sin_rueda(self)
        poner_estilo(self, estilo)
        self._ultimo = valor

    def texto_de(self, valor):
        return next((t for v, t in self.pares if v == valor), "" if valor is None else str(valor))

    def valor(self):
        t = self.variable.get()
        v = next((v for v, x in self.pares if x == t), None)
        if v is None and self.editable:
            v = " ".join(t.split())
        return v

    def elegir(self, valor):
        """Lo mismo que elegir la opción con el ratón (lo usan las pruebas)."""
        self.variable.set(self.texto_de(valor))
        self._cambio()

    def _cambio(self):
        v = self.valor()
        if v == self._ultimo or (self.editable and not v):
            if self.editable and not v:
                self.variable.set(self.texto_de(self._ultimo))
            return
        self._ultimo = v
        if self.al_cambiar:
            self.al_cambiar(v)


def sin_rueda(combo):
    """La rueda sobre una lista desplegable desplaza lo que la contiene en vez de cambiar la opción."""
    def rueda(e):
        w = combo.master
        while w is not None and not hasattr(w, "_rueda"):
            w = w.master
        if w is not None:
            w._rueda(e)
        return "break"
    for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        combo.bind(evento, rueda)


def lista(padre, combo_kw: dict, **kw):
    """ttk.Combobox con el estilo del programa (para quien no usa Opciones)."""
    c = ttk.Combobox(padre, style="CM.TCombobox", font=F["cuerpo"], **combo_kw, **kw)
    sin_rueda(c)
    poner_estilo(c, "CM.TCombobox")
    return c


def campo_bloqueado(padre, texto, ancho_px=None):
    """Campo gris con candado: un valor que se muestra pero no se puede cambiar (mockup 19, regla 4)."""
    caja_ = Caja(padre, fondo=FONDO, borde=LINEA, grosor=1, padx=12, pady=6)
    tk.Label(caja_, text=texto, font=F["cuerpo"], bg=FONDO, fg=GRIS, anchor="w").pack(side="left", pady=2)
    tk.Label(caja_, image=G.candado(padre, 20, GRIS, FONDO), bg=FONDO).pack(side="right")
    return caja_


# ---------------------------------------------------------------- iconos
COLOR_SIMBOLO = G.COLOR


def icono(padre, tipo, d=22, bg=None):
    """Círculo con «!», «i» o «✓» (dibujado): nunca se comunica el estado solo con color."""
    bg = bg or fondo_de(padre)
    return tk.Label(padre, image=G.simbolo(padre, tipo, d, bg), bg=bg, bd=0)


def poner_simbolo(etiqueta, tipo, d):
    etiqueta.configure(image=G.simbolo(etiqueta, tipo, d, fondo_de(etiqueta), relleno=tipo not in ("ok_linea",)))


def marca(padre, tipo, bg=None, d=20):
    """✓ verde o ✗ magenta de las tablas (sin círculo)."""
    bg = bg or fondo_de(padre)
    return tk.Label(padre, image=G.simbolo(padre, "ok" if tipo == "ok" else "mal", d, bg, relleno=False), bg=bg, bd=0)


def flecha(padre, bg=None, w=28, h=16):
    bg = bg or fondo_de(padre)
    return tk.Label(padre, image=G.flecha(padre, w, h, GRIS, bg), bg=bg, bd=0)


def punto(padre, color, d=10):
    bg = fondo_de(padre)
    return tk.Label(padre, image=G.punto(padre, color, d, bg), bg=bg, bd=0)


def numero(padre, n, d=30, color=VERDE_CTA, bg=None):
    bg = bg or fondo_de(padre)
    return tk.Label(padre, image=G.numero(padre, n, d, color, bg), bg=bg, bd=0)


def texto_abrir(ruta) -> str:
    """«Abrir Convenios.xlsx» si el nombre es corto; si no, «Abrir el archivo» (el nombre ya está en «Dónde»)."""
    return f"Abrir {ruta.name}" if len(ruta.name) <= 24 else "Abrir el archivo"


# ---------------------------------------------------------------- chips, franjas, interruptores y casillas
COLOR_CHIP = {"ok": (CHIP_VERDE, OK_TXT), "aviso": (AVISO_BG, AVISO_TXT), "error": (ROSA_SUAVE, MAGENTA),
              "gris": ("#EDEDED", GRIS_OSC), "naranja": (NARANJA, GRIS_OSC), "blanco": (BLANCO, GRIS_OSC)}


class Chip(tk.Label):
    """Etiqueta en forma de píldora (mockups): «3 de 6 encontrados», «Exacta», «Confirmada · 23-nov-2026»…"""

    def __init__(self, padre, texto, tipo="ok", fuente="pequena_b", fondo=None, color=None, borde=None, alto=None,
                 padx=12):
        self.exterior = fondo_de(padre)
        self.relleno, self.color = fondo or COLOR_CHIP[tipo][0], color or COLOR_CHIP[tipo][1]
        self.borde, self.fuente, self.padx = borde, fuente, padx
        self.alto = alto or F[fuente].metrics("linespace") + 10
        super().__init__(padre, compound="center", font=F[fuente], fg=self.color, bg=self.exterior, bd=0,
                         padx=0, pady=0)
        self.configure(text=texto)

    def configure(self, cnf=None, **kw):
        if "text" in kw or (cnf and "text" in cnf):
            texto = kw.get("text") if "text" in kw else cnf["text"]
            ancho = F[self.fuente].measure(texto) + 2 * self.padx
            img = G.caja(self, ancho, self.alto, self.alto // 2, self.relleno, self.borde, 1 if self.borde else 0)
            kw["image"] = img
            self._img = img
        return super().configure(cnf, **kw)

    config = configure


def chip(padre, texto, tipo="ok", bg=None, **kw):
    return Chip(padre, texto, tipo, **kw)


def chip_contexto(padre, texto):
    """Píldora gris con borde: «Programa: …», «Vigencia: …», «Carpeta: …» (mockups 20, 21, 22, 29)."""
    return Chip(padre, texto, "gris", fondo=FONDO, color=GRIS_OSC, borde=LINEA, alto=34, padx=14)


class Franja(Caja):
    """Caja de aviso redondeada con icono: naranja (aviso), magenta (error), verde (info) o gris."""

    COLORES = {"aviso": (AVISO_BG, NARANJA), "error": (ROSA_SUAVE, MAGENTA), "info": (OK_BG, VERDE),
               "gris": (FONDO, LINEA)}

    def __init__(self, padre, tipo="aviso", texto="", centrado=False):
        fondo, borde_ = self.COLORES[tipo]
        super().__init__(padre, fondo=fondo, borde=borde_, grosor=1, radio=RADIO + 2, padx=14, pady=10)
        self.interior = self
        self.icono = icono(self, "gris" if tipo == "gris" else tipo, bg=fondo)
        self.icono.pack(side="left", anchor="center" if centrado else "n", pady=0 if centrado else 1)
        self.texto = tk.Label(self, text=texto, font=F["cuerpo"], bg=fondo, fg=NEGRO, justify="left",
                              anchor="w", wraplength=600)
        self.texto.pack(side="left", fill="x", expand=True, padx=(12, 0))
        self.bind("<Configure>", lambda e: self.texto.configure(wraplength=max(200, e.width - 70)))


class Interruptor(tk.Frame):
    """Interruptor Sí/No (mockups 15 y 19). `al_cambiar(valor)` se llama al pulsarlo."""

    def __init__(self, padre, valor: bool, al_cambiar=None, texto_si="Sí", texto_no="No", activo=True):
        self.fondo = fondo_de(padre)
        super().__init__(padre, bg=self.fondo)
        self.valor, self.al_cambiar, self.activo = bool(valor), al_cambiar, activo
        self.textos = (texto_no, texto_si)
        self.etiqueta = tk.Label(self, font=F["pequena_b"], bg=self.fondo, fg=GRIS_OSC)
        if texto_si or texto_no:
            self.etiqueta.pack(side="left", padx=(0, 10))
        self.imagen = tk.Label(self, bg=self.fondo, bd=0, cursor="hand2" if activo else "arrow")
        self.imagen.pack(side="left")
        for w in (self.imagen, self.etiqueta):
            w.bind("<Button-1>", lambda e: self.alternar())
        self._pintar()

    def _pintar(self):
        self.imagen.configure(image=G.interruptor(self, self.valor, self.activo, self.fondo))
        self.etiqueta.configure(text=self.textos[self.valor])

    def alternar(self):
        if not self.activo:
            return
        self.valor = not self.valor
        self._pintar()
        if self.al_cambiar:
            self.al_cambiar(self.valor)


class Casilla(tk.Frame):
    """Casilla de verificación con su texto (mockup 15, «Qué filas se usan»)."""

    def __init__(self, padre, texto, valor: bool, al_cambiar=None, wraplength=640):
        self.fondo = fondo_de(padre)
        super().__init__(padre, bg=self.fondo, cursor="hand2")
        self.valor, self.al_cambiar = bool(valor), al_cambiar
        self.imagen = tk.Label(self, bg=self.fondo, bd=0, cursor="hand2")
        self.imagen.pack(side="left", anchor="n", pady=1)
        partes = [self, self.imagen]
        if texto:
            self.etiqueta = tk.Label(self, text=texto, font=F["cuerpo"], bg=self.fondo, anchor="w", justify="left",
                                     wraplength=wraplength, cursor="hand2")
            self.etiqueta.pack(side="left", fill="x", padx=(10, 0))
            partes.append(self.etiqueta)
        for w in partes:
            w.bind("<Button-1>", lambda e: self.alternar())
        self._pintar()

    def _pintar(self):
        self.imagen.configure(image=G.casilla(self, self.valor, self.fondo))

    def alternar(self):
        self.valor = not self.valor
        self._pintar()
        if self.al_cambiar:
            self.al_cambiar(self.valor)


def radio(padre, variable, valor, texto="", comando=None, fuente="cuerpo", wraplength=0):
    """Botón de opción con círculo dibujado (mockups 23 y 28)."""
    bg = fondo_de(padre)
    rb = tk.Radiobutton(padre, variable=variable, value=valor, text=texto, font=F[fuente], bg=bg, activebackground=bg,
                        image=G.radio(padre, False, bg), selectimage=G.radio(padre, True, bg), compound="left",
                        indicatoron=False, bd=0, relief="flat", offrelief="flat", overrelief="flat",
                        highlightthickness=0, selectcolor=bg, padx=0, pady=2, anchor="w", justify="left",
                        wraplength=wraplength, cursor="hand2", command=comando, tristatevalue="\x00")
    rb.configure(text=("  " + texto) if texto else "")
    return rb


def desplazable(padre, alto, bg=BLANCO):
    """Marco con barra vertical delgada, separada 8 px del contenido. La rueda del ratón lo mueve mientras el
    puntero está encima (también sobre las listas desplegables de dentro, sin cambiarlas)."""
    marco = tk.Frame(padre, bg=bg)
    lienzo = tk.Canvas(marco, bg=bg, highlightthickness=0, height=alto, bd=0)
    barra = ttk.Scrollbar(marco, orient="vertical", command=lienzo.yview, style="CM.Vertical.TScrollbar")
    interior = tk.Frame(lienzo, bg=bg)
    ventana = lienzo.create_window(0, 0, window=interior, anchor="nw")

    def ajustar(e=None):
        lienzo.configure(scrollregion=lienzo.bbox("all"))
        cabe = interior.winfo_reqheight() <= lienzo.winfo_height() + 1
        if cabe and barra.winfo_ismapped():
            barra.pack_forget()
        elif not cabe and not barra.winfo_ismapped():
            barra.pack(side="right", fill="y", padx=(8, 0), before=lienzo)
    interior.bind("<Configure>", ajustar)
    lienzo.bind("<Configure>", lambda e: (lienzo.itemconfigure(ventana, width=e.width), ajustar()))
    lienzo.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y", padx=(8, 0))
    lienzo.pack(side="left", fill="both", expand=True)

    def rueda(e):
        if lienzo.yview() != (0.0, 1.0):
            lienzo.yview_scroll(-1 if (getattr(e, "delta", 0) > 0 or e.num == 4) else 1, "units")
    for w in (marco, lienzo, interior):
        w._rueda = rueda
    marco.bind("<Enter>", lambda e: (lienzo.bind_all("<MouseWheel>", rueda), lienzo.bind_all("<Button-4>", rueda),
                                     lienzo.bind_all("<Button-5>", rueda)))
    marco.bind("<Leave>", lambda e: (lienzo.unbind_all("<MouseWheel>"), lienzo.unbind_all("<Button-4>"),
                                     lienzo.unbind_all("<Button-5>")))
    marco.lienzo, marco.interior = lienzo, interior
    return marco


def segmentado(padre, opciones, actual, al_cambiar):
    """Selector de dos o más opciones en una píldora (mockup 22: «Todos (16) · Con problemas (3)»)."""
    caja_ = Caja(padre, fondo=BLANCO, borde=LINEA, grosor=1, radio=21, padx=4, pady=4)
    for valor, texto in opciones:
        if valor == actual:
            w = Chip(caja_, texto, fondo=VERDE_CTA, color=BLANCO, alto=34, padx=22)
        else:
            w = tk.Label(caja_, text=texto, font=F["pequena_b"], bg=BLANCO, fg=GRIS_OSC, padx=22, pady=7,
                         cursor="hand2")
            w.bind("<Button-1>", lambda e, v=valor: al_cambiar(v))
        w.pack(side="left")
    return caja_
