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
    estilo.configure("Cambiada.CM.TCombobox", bordercolor=NARANJA)
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

    def __init__(self, padre, variable, solo_lectura=False, guia=None):
        super().__init__(padre, bg=GRIS, padx=1, pady=1)
        interior = tk.Frame(self, bg=BLANCO)
        interior.pack(fill="both", expand=True)
        self.variable = variable
        self.entrada = tk.Entry(interior, textvariable=variable, font=F["cuerpo"], bd=0, bg=BLANCO, fg=NEGRO,
                                readonlybackground=BLANCO, highlightthickness=0, relief="flat")
        self.entrada.pack(fill="both", expand=True, ipady=9, padx=(12, 8))
        if solo_lectura:
            self.entrada.configure(state="readonly")
        self.entrada.bind("<FocusIn>", lambda e: self.configure(bg=VERDE_CTA, padx=2, pady=2), add="+")
        self.entrada.bind("<FocusOut>", lambda e: self.configure(bg=GRIS, padx=1, pady=1), add="+")
        if guia:                     # texto guía en gris mientras el campo está vacío (no se guarda en la variable)
            self.guia = tk.Label(interior, text=guia, font=F["cuerpo"], bg=BLANCO, fg=DESACT_TXT, cursor="xterm")
            self.guia.bind("<Button-1>", lambda e: self.entrada.focus_set())
            variable.trace_add("write", lambda *a: self._guia())
            self.entrada.bind("<FocusIn>", lambda e: self.guia.place_forget(), add="+")
            self.entrada.bind("<FocusOut>", lambda e: self._guia(), add="+")
            self._guia()

    def _guia(self):
        if self.variable.get() or self.focus_get() is self.entrada:
            self.guia.place_forget()
        else:
            self.guia.place(x=13, rely=0.5, anchor="w")

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


def flecha(padre, bg=None, w=28, h=16):
    c = tk.Canvas(padre, width=w, height=h, bg=bg or padre["bg"], highlightthickness=0)
    c.create_line(2, h / 2, w - 3, h / 2, fill=GRIS, width=2, arrow="last", arrowshape=(8, 9, 4))
    return c


def texto_abrir(ruta) -> str:
    """«Abrir Convenios.xlsx» si el nombre es corto; si no, «Abrir el archivo» (el nombre ya está en «Dónde»)."""
    return f"Abrir {ruta.name}" if len(ruta.name) <= 24 else "Abrir el archivo"


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


# ---------------------------------------------------------------- interruptor, casilla y lista de opciones
class Interruptor(tk.Frame):
    """Interruptor Sí/No dibujado (mockups 15 y 19). `al_cambiar(valor)` se llama al pulsarlo."""

    def __init__(self, padre, valor: bool, al_cambiar=None, texto_si="Sí", texto_no="No", activo=True):
        super().__init__(padre, bg=padre["bg"])
        self.valor, self.al_cambiar, self.activo = bool(valor), al_cambiar, activo
        self.textos = (texto_no, texto_si)
        self.etiqueta = tk.Label(self, font=F["pequena_b"], bg=padre["bg"], fg=GRIS_OSC)
        self.etiqueta.pack(side="left", padx=(0, 10))
        self.lienzo = tk.Canvas(self, width=56, height=30, bg=padre["bg"], highlightthickness=0,
                                cursor="hand2" if activo else "arrow")
        self.lienzo.pack(side="left")
        for w in (self.lienzo, self.etiqueta):
            w.bind("<Button-1>", lambda e: self.alternar())
        self._pintar()

    def _pintar(self):
        c, si = self.lienzo, self.valor
        c.delete("all")
        color = (VERDE_CTA if si else "#BDBDBD") if self.activo else DESACT_BG
        c.create_oval(1, 1, 29, 29, fill=color, outline=color)
        c.create_oval(27, 1, 55, 29, fill=color, outline=color)
        c.create_rectangle(15, 1, 41, 29, fill=color, outline=color)
        x = 41 if si else 15
        c.create_oval(x - 11, 4, x + 11, 26, fill=BLANCO, outline=BLANCO)
        self.etiqueta.configure(text=self.textos[si])

    def alternar(self):
        if not self.activo:
            return
        self.valor = not self.valor
        self._pintar()
        if self.al_cambiar:
            self.al_cambiar(self.valor)


class Casilla(tk.Frame):
    """Casilla de verificación dibujada con su texto (mockup 15, «Qué filas se usan»)."""

    def __init__(self, padre, texto, valor: bool, al_cambiar=None, wraplength=640):
        super().__init__(padre, bg=padre["bg"], cursor="hand2")
        self.valor, self.al_cambiar = bool(valor), al_cambiar
        self.lienzo = tk.Canvas(self, width=24, height=24, bg=padre["bg"], highlightthickness=0, cursor="hand2")
        self.lienzo.pack(side="left", anchor="n")
        self.etiqueta = tk.Label(self, text=texto, font=F["cuerpo"], bg=padre["bg"], anchor="w", justify="left",
                                 wraplength=wraplength, cursor="hand2")
        self.etiqueta.pack(side="left", fill="x", padx=(10, 0))
        for w in (self, self.lienzo, self.etiqueta):
            w.bind("<Button-1>", lambda e: self.alternar())
        self._pintar()

    def _pintar(self):
        c = self.lienzo
        c.delete("all")
        if self.valor:
            c.create_rectangle(2, 2, 22, 22, fill=VERDE_CTA, outline=VERDE_CTA)
            c.create_line(6, 12, 10, 17, 18, 7, fill=BLANCO, width=3, capstyle="round", joinstyle="round")
        else:
            c.create_rectangle(2, 2, 22, 22, fill=BLANCO, outline=GRIS, width=2)

    def alternar(self):
        self.valor = not self.valor
        self._pintar()
        if self.al_cambiar:
            self.al_cambiar(self.valor)


class Opciones(ttk.Combobox):
    """Lista desplegable de solo lectura que muestra textos y devuelve valores internos.

    `pares` = [(valor, texto), ...]. Si el valor actual no está en la lista se muestra tal cual (no se pierde).
    """

    def __init__(self, padre, pares, valor, al_cambiar=None, ancho=None, editable=False):
        self.pares = list(pares)
        if valor is not None and all(v != valor for v, _ in self.pares):
            self.pares.append((valor, str(valor)))
        self.variable = tk.StringVar(value=self.texto_de(valor))
        super().__init__(padre, textvariable=self.variable, values=[t for _, t in self.pares],
                         state="normal" if editable else "readonly", style="CM.TCombobox", font=F["cuerpo"],
                         height=14, **({"width": ancho} if ancho else {}))
        self.al_cambiar, self.editable = al_cambiar, editable
        self.bind("<<ComboboxSelected>>", lambda e: self._cambio())
        if editable:
            self.bind("<FocusOut>", lambda e: self._cambio(), add="+")
            self.bind("<Return>", lambda e: self._cambio(), add="+")
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


def campo_bloqueado(padre, texto, ancho_px=None):
    """Campo gris con candado: un valor que se muestra pero no se puede cambiar (mockup 19, regla 4)."""
    borde = tk.Frame(padre, bg=LINEA, padx=1, pady=1)
    d = tk.Frame(borde, bg=FONDO)
    d.pack(fill="both", expand=True)
    tk.Label(d, text=texto, font=F["cuerpo"], bg=FONDO, fg=GRIS, anchor="w").pack(side="left", padx=12, pady=8)
    c = tk.Canvas(d, width=18, height=20, bg=FONDO, highlightthickness=0)
    c.create_arc(4, 2, 14, 12, start=0, extent=180, style="arc", outline=GRIS, width=2)
    c.create_rectangle(2, 8, 16, 18, fill=GRIS, outline=GRIS)
    c.pack(side="right", padx=10)
    return borde


def chip(padre, texto, tipo="ok", bg=None):
    """Etiqueta redondeada de estado: ok (verde), aviso (naranja), error (magenta), gris."""
    fondo, color = {"ok": ("#E3EED2", OK_TXT), "aviso": (AVISO_BG, AVISO_TXT), "error": (ROSA_SUAVE, MAGENTA),
                    "gris": ("#EDEDED", GRIS_OSC)}[tipo]
    return tk.Label(padre, text=texto, font=F["pequena_b"], bg=fondo, fg=color, padx=10, pady=4)


def desplazable(padre, alto, bg=BLANCO):
    """Marco con barra vertical; la rueda del ratón lo mueve solo mientras el puntero está encima."""
    marco = tk.Frame(padre, bg=bg)
    lienzo = tk.Canvas(marco, bg=bg, highlightthickness=0, height=alto)
    barra = tk.Scrollbar(marco, orient="vertical", command=lienzo.yview)
    interior = tk.Frame(lienzo, bg=bg)
    ventana = lienzo.create_window(0, 0, window=interior, anchor="nw")
    interior.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(ventana, width=e.width))
    lienzo.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    lienzo.pack(side="left", fill="both", expand=True)

    def rueda(e):
        if lienzo.yview() != (0.0, 1.0):
            lienzo.yview_scroll(-1 if (e.delta > 0 or e.num == 4) else 1, "units")
    marco.bind("<Enter>", lambda e: (lienzo.bind_all("<MouseWheel>", rueda), lienzo.bind_all("<Button-4>", rueda),
                                     lienzo.bind_all("<Button-5>", rueda)))
    marco.bind("<Leave>", lambda e: (lienzo.unbind_all("<MouseWheel>"), lienzo.unbind_all("<Button-4>"),
                                     lienzo.unbind_all("<Button-5>")))
    marco.lienzo, marco.interior = lienzo, interior
    return marco
