"""Colores, tipografías y controles con la identidad de Areandina (docs/identidad.md, mockup 05).

Tkinter no dibuja esquinas redondeadas ni sombras: los controles son rectos, con los colores y estados del manual.
Brown Std se carga solo para el programa (Windows: AddFontResourceExW con FR_PRIVATE); si no está, Segoe UI.
"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from ..recursos import carpeta_recursos
from .ayudas import AYUDAS

VERDE, VERDE_CTA, VERDE_HOVER, VERDE_PULSADO = "#7FB536", "#67882C", "#587425", "#4A6320"
MAGENTA, NARANJA, GRIS, GRIS_OSC = "#E6007E", "#F59C2F", "#606060", "#282828"
BLANCO, NEGRO, FONDO, LINEA = "#FFFFFF", "#000000", "#F5F5F5", "#D9D9D9"
TINTE_VERDE, AVISO_BG, AVISO_TXT, ROSA_SUAVE = "#EAF2DD", "#FFF3E3", "#9A5B00", "#FDE6F2"
OK_BG, OK_TXT, DESACT_BG, DESACT_TXT, DESACT_BORDE = "#EEF5E3", "#4A6320", "#D9D9D9", "#9A9A9A", "#C8C8C8"

F: dict[str, tkfont.Font] = {}


def cargar_fuentes(raiz: tk.Tk) -> str:
    """Carga Brown Std (si está junto al programa) y crea las fuentes con nombre. Devuelve la familia usada."""
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
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure("CM.TCombobox", padding=(10, 8), fieldbackground=BLANCO, background=BLANCO,
                     bordercolor=GRIS, lightcolor=BLANCO, darkcolor=BLANCO, arrowcolor=GRIS_OSC, arrowsize=14)
    estilo.map("CM.TCombobox", bordercolor=[("focus", VERDE_CTA)], fieldbackground=[("readonly", BLANCO)],
               foreground=[("disabled", DESACT_TXT)])
    estilo.configure("Error.CM.TCombobox", bordercolor=MAGENTA)
    raiz.option_add("*TCombobox*Listbox.font", F["cuerpo"])
    raiz.option_add("*TCombobox*Listbox.selectBackground", TINTE_VERDE)
    raiz.option_add("*TCombobox*Listbox.selectForeground", NEGRO)
    estilo.configure("CM.Horizontal.TProgressbar", troughcolor="#E3E3E3", background=VERDE_CTA, bordercolor="#E3E3E3",
                     lightcolor=VERDE_CTA, darkcolor=VERDE_CTA, thickness=10)
    return familia


# ---------------------------------------------------------------- botones y enlaces
class Boton(tk.Frame):
    """Botón principal (relleno verde) o secundario (borde verde). Estados: normal, hover, pulsado, desactivado."""

    def __init__(self, padre, texto, comando=None, tipo="primario", fuente="boton", ancho=None, alto=44):
        super().__init__(padre, bg=padre["bg"], highlightthickness=0, bd=0)
        self.tipo, self.comando, self.activo = tipo, comando, True
        self.marco = tk.Frame(self, bd=0, highlightthickness=0, height=alto)
        self.marco.pack(fill="both", expand=True)
        if ancho:
            self.marco.configure(width=ancho)
        self.marco.pack_propagate(False)
        self.etiqueta = tk.Label(self.marco, text=texto, font=F[fuente], cursor="hand2", bd=0)
        self.etiqueta.pack(fill="both", expand=True, padx=2, pady=2)
        for w in (self.marco, self.etiqueta):
            w.bind("<Enter>", lambda e: self._pintar("hover"))
            w.bind("<Leave>", lambda e: self._pintar("normal"))
            w.bind("<ButtonPress-1>", lambda e: self._pintar("pulsado"))
            w.bind("<ButtonRelease-1>", self._soltar)
        self._pintar("normal")

    def _soltar(self, evento):
        dentro = self.etiqueta.winfo_containing(evento.x_root, evento.y_root) in (self.etiqueta, self.marco)
        self._pintar("hover" if dentro else "normal")
        if dentro and self.activo and self.comando:
            self.comando()

    def _pintar(self, estado):
        if not self.activo:
            borde, fondo, texto = (DESACT_BG, DESACT_BG, DESACT_TXT) if self.tipo == "primario" else \
                (DESACT_BORDE, BLANCO, DESACT_TXT)
            self.etiqueta.configure(cursor="arrow")
        elif self.tipo == "primario":
            fondo = {"hover": VERDE_HOVER, "pulsado": VERDE_PULSADO}.get(estado, VERDE_CTA)
            borde, texto = fondo, BLANCO
            self.etiqueta.configure(cursor="hand2")
        else:
            borde, texto = VERDE_CTA, VERDE_CTA
            fondo = TINTE_VERDE if estado in ("hover", "pulsado") else BLANCO
            self.etiqueta.configure(cursor="hand2")
        self.marco.configure(bg=borde)
        self.etiqueta.configure(bg=fondo, fg=texto, activebackground=fondo)

    def activar(self, si=True):
        self.activo = bool(si)
        self._pintar("normal")

    def texto(self, t):
        self.etiqueta.configure(text=t)


class Enlace(tk.Label):
    """Texto verde subrayado (Actualizar, Ver revisión, Abrir carpeta). Gris cuando está desactivado."""

    def __init__(self, padre, texto, comando=None, fuente="cuerpo_b"):
        self._fuente = tkfont.Font(font=F[fuente])
        self._fuente.configure(underline=True)
        super().__init__(padre, text=texto, font=self._fuente, bg=padre["bg"], fg=VERDE_CTA, cursor="hand2")
        self.comando, self.activo = comando, True
        self.bind("<Button-1>", lambda e: self.activo and self.comando and self.comando())

    def activar(self, si=True):
        self.activo = bool(si)
        self._fuente.configure(underline=self.activo)
        self.configure(fg=VERDE_CTA if si else DESACT_TXT, cursor="hand2" if si else "arrow")


# ---------------------------------------------------------------- signo de ayuda
class Ayuda(tk.Canvas):
    """Círculo «?»: al pasar el puntero se rellena; al hacer clic abre la ayuda (mockup 04). Esc o clic fuera la cierran."""

    abierta: "Ayuda | None" = None

    def __init__(self, padre, clave, d=26):
        super().__init__(padre, width=d, height=d, bg=padre["bg"], highlightthickness=0, cursor="hand2")
        self.clave, self.d, self.ventana = clave, d, None
        self._dibujar(False)
        self.bind("<Enter>", lambda e: self._dibujar(True))
        self.bind("<Leave>", lambda e: self._dibujar(self.ventana is not None))
        self.bind("<Button-1>", lambda e: self.alternar())

    def _dibujar(self, lleno):
        self.delete("all")
        d = self.d
        self.create_oval(2, 2, d - 2, d - 2, outline=VERDE_CTA, width=2, fill=VERDE_CTA if lleno else self["bg"])
        self.create_text(d / 2, d / 2 + 1, text="?", font=F["pequena_b"], fill=BLANCO if lleno else VERDE_CTA)

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


class PanelAyuda(tk.Toplevel):
    def __init__(self, ancla: Ayuda, ayuda: dict, ancho=470):
        super().__init__(ancla)
        self.overrideredirect(True)
        self.configure(bg=VERDE, padx=2, pady=2)
        cuerpo = tk.Frame(self, bg=BLANCO, padx=18, pady=14)
        cuerpo.pack(fill="both", expand=True)
        tk.Label(cuerpo, text=ayuda["titulo"], font=F["seccion"], bg=BLANCO, fg=GRIS_OSC, anchor="w").pack(fill="x")
        tk.Frame(cuerpo, bg=VERDE, height=3, width=60).pack(anchor="w", pady=(4, 8))
        texto = tk.Text(cuerpo, wrap="word", bd=0, bg=BLANCO, font=F["pequena"], width=1, height=1,
                        padx=0, pady=0, cursor="arrow", highlightthickness=0, spacing1=2, spacing3=4)
        texto.tag_configure("b", font=F["pequena_b"])
        texto.tag_configure("h", font=F["pequena_b"], foreground=VERDE_CTA, spacing1=8)
        texto.tag_configure("vineta", lmargin1=4, lmargin2=18)
        texto.tag_configure("chip", background=FONDO, font=F["pequena"])
        for tipo, contenido in ayuda["bloques"]:
            if tipo == "h":
                texto.insert("end", contenido + "\n", "h")
            elif tipo == "chips":
                for c in contenido:
                    texto.insert("end", f" {c} ", "chip")
                    texto.insert("end", "  ")
                texto.insert("end", "\n")
            else:
                prefijo = {"b": "•  ", "ok": "✓  ", "mal": "✗  "}.get(tipo, "")
                etiquetas = ("vineta",) if prefijo else ()
                texto.insert("end", prefijo, etiquetas)
                for t, negrita in contenido:
                    texto.insert("end", t, etiquetas + (("b",) if negrita else ()))
                texto.insert("end", "\n")
        texto.configure(state="disabled")
        texto.pack(fill="both", expand=True)
        self.update_idletasks()
        cuerpo.configure(width=ancho)
        texto.configure(width=56)
        lineas = int(texto.count("1.0", "end", "displaylines")[0]) if texto.count("1.0", "end", "displaylines") else 10
        texto.configure(height=min(lineas, 24))
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


# ---------------------------------------------------------------- otros
class Campo(tk.Frame):
    """Entrada de texto con borde gris (verde al tener el foco, magenta con error)."""

    def __init__(self, padre, variable, solo_lectura=False):
        super().__init__(padre, bg=GRIS, padx=1, pady=1)
        interior = tk.Frame(self, bg=BLANCO)
        interior.pack(fill="both", expand=True)
        self.entrada = tk.Entry(interior, textvariable=variable, font=F["cuerpo"], bd=0, bg=BLANCO, fg=NEGRO,
                                readonlybackground=BLANCO, highlightthickness=0, relief="flat")
        self.entrada.pack(fill="both", expand=True, ipady=9, padx=(12, 8))
        if solo_lectura:
            self.entrada.configure(state="readonly")
        self.entrada.bind("<FocusIn>", lambda e: self.configure(bg=VERDE_CTA, padx=2, pady=2))
        self.entrada.bind("<FocusOut>", lambda e: self.configure(bg=GRIS, padx=1, pady=1))

    def error(self, si=True):
        self.configure(bg=MAGENTA if si else GRIS, padx=2 if si else 1, pady=2 if si else 1)


COLOR_SIMBOLO = {"ok": VERDE_CTA, "info": VERDE_CTA, "aviso": NARANJA, "error": MAGENTA, "mal": MAGENTA,
                 "gris": "#9A9A9A", "pendiente": DESACT_TXT, "curso": VERDE_CTA}


def dibujar_simbolo(c: tk.Canvas, tipo: str, d: int, relleno=True):
    """Dibuja con figuras (no con letras) para que se vea igual con cualquier tipografía.

    ok ✓ · mal ✗ (sin círculo) · aviso/error ! · info/gris i (en círculo) · pendiente ○ · curso ◔.
    """
    c.delete("all")
    color = COLOR_SIMBOLO[tipo]
    w = max(2, d // 9)
    if tipo == "mal":
        m = d * 0.22
        c.create_line(m, m, d - m, d - m, fill=color, width=w + 1, capstyle="round")
        c.create_line(m, d - m, d - m, m, fill=color, width=w + 1, capstyle="round")
        return
    if tipo == "pendiente":
        c.create_oval(2, 2, d - 2, d - 2, outline=color, width=w)
        return
    if tipo == "curso":
        c.create_oval(2, 2, d - 2, d - 2, outline="#DADADA", width=w)
        c.create_arc(2, 2, d - 2, d - 2, start=90, extent=-250, style="arc", outline=color, width=w)
        return
    if tipo == "ok" and not relleno:
        c.create_line(d * .18, d * .52, d * .42, d * .76, d * .84, d * .26, fill=color, width=w + 1,
                      capstyle="round", joinstyle="round")
        return
    c.create_oval(1, 1, d - 1, d - 1, fill=color, outline=color)
    if tipo == "ok":
        c.create_line(d * .27, d * .52, d * .44, d * .69, d * .74, d * .34, fill=BLANCO, width=w,
                      capstyle="round", joinstyle="round")
    elif tipo in ("aviso", "error"):
        c.create_line(d / 2, d * .24, d / 2, d * .58, fill=BLANCO, width=w, capstyle="round")
        c.create_oval(d / 2 - w * .7, d * .70, d / 2 + w * .7, d * .70 + w * 1.4, fill=BLANCO, outline=BLANCO)
    else:
        c.create_oval(d / 2 - w * .7, d * .22, d / 2 + w * .7, d * .22 + w * 1.4, fill=BLANCO, outline=BLANCO)
        c.create_line(d / 2, d * .42, d / 2, d * .76, fill=BLANCO, width=w, capstyle="round")


def icono(padre, tipo, d=22, bg=None):
    """Círculo con «!», «i» o «✓» (dibujado): nunca se comunica el estado solo con color."""
    c = tk.Canvas(padre, width=d, height=d, bg=bg or padre["bg"], highlightthickness=0)
    dibujar_simbolo(c, tipo, d)
    return c


def marca(padre, tipo, bg=None, d=20):
    """✓ verde o ✗ magenta de la tabla de archivos (dibujados)."""
    c = tk.Canvas(padre, width=d, height=d, bg=bg or padre["bg"], highlightthickness=0)
    dibujar_simbolo(c, "ok" if tipo == "ok" else "mal", d, relleno=False)
    return c


def punto(padre, color, d=10):
    c = tk.Canvas(padre, width=d, height=d, bg=padre["bg"], highlightthickness=0)
    c.create_oval(1, 1, d - 1, d - 1, fill=color, outline=color)
    return c


class Franja(tk.Frame):
    """Caja de aviso con icono: naranja (aviso), magenta (error), verde (info) o gris."""

    COLORES = {"aviso": (AVISO_BG, NARANJA), "error": (ROSA_SUAVE, MAGENTA), "info": (OK_BG, VERDE),
               "gris": (FONDO, LINEA)}

    def __init__(self, padre, tipo="aviso", texto=""):
        fondo, borde = self.COLORES[tipo]
        super().__init__(padre, bg=borde, padx=1, pady=1)
        self.interior = tk.Frame(self, bg=fondo, padx=14, pady=10)
        self.interior.pack(fill="both", expand=True)
        self.icono = icono(self.interior, "gris" if tipo == "gris" else tipo, bg=fondo)
        self.icono.pack(side="left", anchor="n", pady=1)
        self.texto = tk.Label(self.interior, text=texto, font=F["cuerpo"], bg=fondo, fg=NEGRO, justify="left",
                              anchor="w", wraplength=600)
        self.texto.pack(side="left", fill="x", expand=True, padx=(12, 0))
        self.bind("<Configure>", lambda e: self.texto.configure(wraplength=max(200, e.width - 70)))
