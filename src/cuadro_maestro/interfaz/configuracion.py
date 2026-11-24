"""Configuración (mockup 06) y sus modales de listas: Programas (07), Equivalencias (16, 17), Tipos de persona (18) y
Copias y almacenamiento (24). Fuentes de datos, Campos y Reglas están en fuentes.py, campos.py y reglas.py. Todo se guarda al instante; los Excel nunca se tocan."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from ..configuracion.almacen import (ANTES_DE_IMPORTAR, ANTES_DE_RESTAURAR, AUTOMATICA, CREADA_POR_TI, DANADA,
                                     DESCARTADA, VERSION_NUEVA)
from ..configuracion.valores_iniciales import REGLAS_CONFIRMADAS, identificador
from ..texto import normalizar
from . import dialogos as D
from . import tema as T
from .modelo import cuando
from .sistema import abrir

ORIGEN = {"tu": ("Tú", "#E3EED2", T.OK_TXT), "gemini": ("Gemini", "#EDEDED", T.GRIS_OSC),
          "revision": ("Revisión", T.AVISO_BG, T.AVISO_TXT)}
MOTIVO = {AUTOMATICA: "Automática", ANTES_DE_IMPORTAR: "Antes de importar", ANTES_DE_RESTAURAR: "Antes de restaurar",
          CREADA_POR_TI: "Creada por ti", DANADA: "Copia dañada guardada aparte",
          VERSION_NUEVA: "De una versión más nueva", DESCARTADA: "La otra copia (más antigua)"}


def reglas_cambiadas(config) -> int:
    return sum(1 for k, v in config["reglas"].items() if k != "confirmadas_el" and v != REGLAS_CONFIRMADAS.get(k))


# ---------------------------------------------------------------- iconos dibujados
def icono_lapiz(padre, bg, d=26):
    c = tk.Canvas(padre, width=d, height=d, bg=bg, highlightthickness=0, cursor="hand2")
    c.create_line(d * .25, d * .75, d * .72, d * .28, fill=T.GRIS, width=4, capstyle="butt")
    c.create_polygon(d * .18, d * .82, d * .22, d * .66, d * .34, d * .78, fill=T.GRIS, outline=T.GRIS)
    return c


def icono_papelera(padre, bg, d=26, bloqueado=False):
    c = tk.Canvas(padre, width=d, height=d, bg=bg, highlightthickness=0, cursor="arrow" if bloqueado else "hand2")
    if bloqueado:            # candado: campo o tipo base, no se elimina
        c.create_arc(d * .32, d * .14, d * .68, d * .52, start=0, extent=180, style="arc", outline=T.GRIS, width=2)
        c.create_rectangle(d * .26, d * .42, d * .74, d * .82, fill=T.GRIS, outline=T.GRIS)
        return c
    c.create_line(d * .2, d * .28, d * .8, d * .28, fill=T.GRIS, width=2)
    c.create_rectangle(d * .4, d * .16, d * .6, d * .28, outline=T.GRIS, width=2)
    c.create_rectangle(d * .28, d * .3, d * .72, d * .84, outline=T.GRIS, width=2)
    for x in (.42, .58):
        c.create_line(d * x, d * .4, d * x, d * .74, fill=T.GRIS, width=2)
    return c


def con_ayuda(widget, texto):
    """Tooltip simple («Editar», «Eliminar», «Campo base: no se puede eliminar»)."""
    estado = {}

    def mostrar(e):
        t = tk.Toplevel(widget)
        t.overrideredirect(True)
        tk.Label(t, text=texto, font=T.F["pequena"], bg=T.GRIS_OSC, fg=T.BLANCO, padx=8, pady=4).pack()
        t.geometry(f"+{e.x_root + 12}+{e.y_root - 30}")
        estado["t"] = t

    def ocultar(_):
        if estado.get("t"):
            estado.pop("t").destroy()
    widget.bind("<Enter>", mostrar, add="+")
    widget.bind("<Leave>", ocultar, add="+")
    return widget


# ---------------------------------------------------------------- pantalla
TARJETAS = [
    ("programas", "Programas", "prog", "Los programas que se pueden elegir al generar un cuadro: se listan, se modifican, "
     "se crean o se eliminan."),
    ("campos", "Campos del cuadro maestro", "campos", "Las columnas del cuadro. Crea, edita o elimina campos y elige de "
     "dónde sale cada uno."),
    ("fuentes", "Fuentes de datos", "fuentes", "Cómo lee el programa cada Excel: fila de encabezados, columnas y filtros."),
    ("eq_inst", "Equivalencias de instituciones", "eq_inst", "Nombres distintos que son la misma universidad (por "
     "ejemplo, con un error de escritura)."),
    ("eq_prog", "Equivalencias de programas", "eq_prog", "Por ejemplo: Ingeniería Industrial Distancia = Ingeniería "
     "Industrial."),
    ("tipos", "Tipos de persona", "tipos", "Cómo se nombra cada tipo en el cuadro: Docente saliente, Experto "
     "internacional…"),
    ("reglas", "Reglas de cruce", "reglas", "Cómo se asigna cada registro a un convenio y cómo se cuenta."),
    ("gemini", "Asistente con Gemini", "gemini", "Ayuda a emparejar columnas y nombres. Solo usa títulos de columnas y "
     "nombres de instituciones."),
]


class PantallaConfiguracion(tk.Frame):
    def __init__(self, app, al_volver):
        super().__init__(app.raiz, bg=T.BLANCO)
        self.app, self.al_volver = app, al_volver
        cab = tk.Frame(self, bg=T.BLANCO, padx=28, pady=16)
        cab.pack(fill="x")
        app.ventana._logo(cab).pack(side="left")
        der = tk.Frame(cab, bg=T.BLANCO)
        der.pack(side="right")
        tk.Label(der, text="Configuración", font=T.F["app_titulo"], bg=T.BLANCO, fg=T.GRIS_OSC).pack(anchor="e")
        tk.Label(der, text="Oficina de Relaciones Internacionales", font=T.F["app_sub"], bg=T.BLANCO, fg=T.GRIS).pack(anchor="e")
        tk.Frame(self, bg=T.VERDE, height=4).pack(fill="x")
        self.cuerpo = tk.Frame(self, bg=T.BLANCO, padx=28, pady=16)
        self.cuerpo.pack(fill="both", expand=True)
        self.pintar()

    def pintar(self):
        c = self.cuerpo
        for w in c.winfo_children():
            w.destroy()
        T.Enlace(c, "‹ Volver al cuadro maestro", self.al_volver).pack(anchor="w")
        tk.Label(c, text="Aquí adaptas el programa a cambios en los Excel. Todo se puede listar, modificar, crear y "
                         "eliminar, y se guarda al instante.", font=T.F["cuerpo"], bg=T.BLANCO, anchor="w",
                 justify="left").pack(fill="x", pady=(8, 12))
        rejilla = tk.Frame(c, bg=T.BLANCO)
        rejilla.pack(fill="both", expand=True)
        cfg = self.app.config
        for i, (clave, titulo, ayuda, texto) in enumerate(TARJETAS):
            borde = tk.Frame(rejilla, bg=T.LINEA, padx=1, pady=1)
            borde.grid(row=i // 2, column=i % 2, sticky="nsew", padx=(0 if i % 2 == 0 else 8, 0), pady=(0, 10))
            rejilla.grid_columnconfigure(i % 2, weight=1, uniform="t")
            t = tk.Frame(borde, bg=T.BLANCO, padx=18, pady=12)
            t.pack(fill="both", expand=True)
            f = tk.Frame(t, bg=T.BLANCO)
            f.pack(fill="x")
            tk.Label(f, text=titulo, font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
            T.Ayuda(f, ayuda).pack(side="left", padx=8)
            tk.Label(t, text=texto, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=380).pack(fill="x", pady=(6, 10))
            abajo = tk.Frame(t, bg=T.BLANCO)
            abajo.pack(fill="x")
            etiqueta, fondo, fg = self._conteo(clave, cfg)
            tk.Label(abajo, text=etiqueta, font=T.F["pequena_b"], bg=fondo, fg=fg, padx=10, pady=4).pack(side="left")
            T.Boton(abajo, "Abrir asistente" if clave == "gemini" else "Administrar",
                    lambda k=clave: self.app.abrir_modal(k, self.app.raiz, self.pintar), tipo="secundario",
                    fuente="boton_peq", ancho=170, alto=38).pack(side="right")
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(8, 0))
        izq = tk.Frame(pie, bg=T.BLANCO)
        izq.pack(side="left")
        guardado = self.app.almacen.actual["guardado_en"] if self.app.almacen.actual else None
        hora = datetime.fromisoformat(guardado).astimezone().replace(tzinfo=None) if guardado else None
        tk.Label(izq, text=f"Última modificación: {cuando(hora) if hora else '—'}", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(anchor="w")
        T.Enlace(izq, "Copias y almacenamiento ›", lambda: self.app.abrir_modal("copias", self.app.raiz, self.pintar),
                 fuente="pequena_b").pack(anchor="w")
        T.Boton(pie, "Volver al cuadro maestro", self.al_volver, ancho=280).pack(side="right")
        T.Boton(pie, "Exportar / importar", lambda: self.app.abrir_modal("exportar", self.app.raiz, self.pintar),
                tipo="secundario", ancho=210).pack(side="right", padx=14)


    def _conteo(self, clave, cfg):
        verde = ("#E3EED2", T.OK_TXT)
        if clave == "programas":
            return (f"{len(cfg['programas'])} programas", *verde)
        if clave == "campos":
            return (f"{len(cfg['campos'])} campos", *verde)
        if clave == "fuentes":
            return (f"{len(cfg['fuentes'])} fuentes", *verde)
        if clave == "eq_inst":
            return (f"{len(cfg['equivalencias_instituciones'])} guardadas", *verde)
        if clave == "eq_prog":
            return (f"{len(cfg['equivalencias_programas'])} guardadas", *verde)
        if clave == "tipos":
            return (f"{len(cfg['tipos_persona'])} tipos", *verde)
        if clave == "reglas":
            n = reglas_cambiadas(cfg)
            return (f"5 reglas · {n} cambiada{'s' if n != 1 else ''}", T.AVISO_BG, T.AVISO_TXT) if n else ("5 reglas", *verde)
        return ("Opcional", "#EDEDED", T.GRIS_OSC)


# ---------------------------------------------------------------- base de los modales de listas
class ModalLista(D.Modal):
    TITULO, AYUDA, DESCRIPCION, CREAR, ANCHO, GUIA = "", "", "", "", 900, "Buscar…"

    def __init__(self, app, duena=None):
        super().__init__(duena or app.raiz, self.TITULO, ancho=self.ANCHO)
        self.app = app
        self.editando = None          # índice del elemento en edición (-1 = nuevo)
        self.eliminando = None
        cab = tk.Frame(self.cuerpo, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text=self.TITULO, font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, self.AYUDA).pack(side="left", padx=10)
        self.chip = tk.Label(cab, font=T.F["pequena_b"], bg="#E3EED2", fg=T.OK_TXT, padx=12, pady=4)
        self.chip.pack(side="right")
        tk.Label(self.cuerpo, text=self.DESCRIPCION, font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=self.ANCHO - 80).pack(fill="x", pady=(8, 12))
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x", pady=(0, 12))
        self.v_buscar = tk.StringVar()
        T.Campo(fila, self.v_buscar, guia=self.GUIA).pack(side="left", fill="x", expand=True)
        self.v_buscar.trace_add("write", lambda *a: self.pintar())
        T.Boton(fila, f"+  {self.CREAR}", self.crear, ancho=T.F["boton"].measure(self.CREAR) + 80).pack(side="left", padx=(14, 0))
        marco = tk.Frame(self.cuerpo, bg=T.LINEA, padx=1, pady=1)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, bg=T.BLANCO, highlightthickness=0, height=430)
        barra = tk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.lista = tk.Frame(self.lienzo, bg=T.BLANCO)
        vid = self.lienzo.create_window(0, 0, window=self.lista, anchor="nw")
        self.lista.bind("<Configure>", lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfigure(vid, width=e.width))
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        pie = self.botones()
        self.lbl_pie = tk.Label(pie, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left")
        self.lbl_pie.pack(side="left")
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=160).pack(side="right")
        self.bind("<Return>", lambda e: None)
        self.pintar()

    # a implementar por cada lista
    def elementos(self) -> list:
        return []

    def texto_busqueda(self, e) -> str:
        return ""

    def fila(self, padre, i, e, fondo):
        pass

    def editor(self, padre, i, e):
        pass

    def eliminar_elemento(self, i):
        pass

    def pie(self, mostrados, total) -> str:
        return f"Mostrando {mostrados} de {total} · Los cambios se guardan al instante."

    def chip_texto(self, total) -> str:
        return str(total)

    # comunes
    def pintar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        elementos = self.elementos()
        q = normalizar(self.v_buscar.get())
        visibles = [(i, e) for i, e in enumerate(elementos) if not q or q in normalizar(self.texto_busqueda(e))]
        if self.editando == -1:
            self._caja_editor(-1, None)
        for n, (i, e) in enumerate(visibles):
            if self.editando == i:
                self._caja_editor(i, e)
            elif self.eliminando == i:
                self._confirmar_eliminar(i, e)
            else:
                fondo = T.BLANCO if n % 2 == 0 else T.FONDO
                f = tk.Frame(self.lista, bg=fondo, padx=14, pady=8)
                f.pack(fill="x")
                self.fila(f, i, e, fondo)
        if not visibles and self.editando != -1:
            tk.Label(self.lista, text="No hay nada que coincida con la búsqueda." if q else "Todavía no hay ninguno.",
                     font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS, pady=18).pack()
        self.chip.configure(text=self.chip_texto(len(elementos)))
        self.lbl_pie.configure(text=self.pie(len(visibles), len(elementos)))

    def acciones(self, f, i, fondo, bloqueado=False, ayuda_bloqueo=""):
        caja = tk.Frame(f, bg=fondo)
        caja.pack(side="right")
        lapiz = con_ayuda(icono_lapiz(caja, fondo), "Editar")
        lapiz.pack(side="left", padx=6)
        lapiz.bind("<Button-1>", lambda e: self.editar(i))
        tacho = icono_papelera(caja, fondo, bloqueado=bloqueado)
        tacho.pack(side="left", padx=6)
        if bloqueado:
            con_ayuda(tacho, ayuda_bloqueo)
        else:
            con_ayuda(tacho, "Eliminar").bind("<Button-1>", lambda e: self.pedir_eliminar(i))

    def crear(self):
        self.editando, self.eliminando = -1, None
        self.pintar()
        self.lienzo.yview_moveto(0)

    def editar(self, i):
        self.editando, self.eliminando = i, None
        self.pintar()

    def pedir_eliminar(self, i):
        self.eliminando, self.editando = i, None
        self.pintar()

    def cancelar(self):
        self.editando = self.eliminando = None
        self.pintar()

    def guardado(self):
        self.editando = self.eliminando = None
        self.app.guardar_config()
        self.pintar()

    def _caja_editor(self, i, e):
        borde = tk.Frame(self.lista, bg=T.VERDE_CTA, padx=2, pady=2)
        borde.pack(fill="x", padx=8, pady=6)
        d = tk.Frame(borde, bg=T.TINTE_VERDE, padx=16, pady=12)
        d.pack(fill="both")
        tk.Label(d, text="Nuevo" if i == -1 else "Editando", font=T.F["cuerpo_b"], bg=T.TINTE_VERDE, fg=T.OK_TXT,
                 anchor="w").pack(fill="x", pady=(0, 6))
        guardar = self.editor(d, i, e)
        self.guardar_edicion = guardar             # lo mismo que pulsar Enter o «Guardar»
        pie = tk.Frame(d, bg=T.TINTE_VERDE)
        pie.pack(fill="x", pady=(10, 0))
        tk.Label(pie, text="Enter guarda · Esc cancela", font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.GRIS).pack(side="left")
        T.Boton(pie, "Guardar", guardar, fuente="boton_peq", ancho=130, alto=36).pack(side="right")
        T.Boton(pie, "Cancelar", self.cancelar, tipo="secundario", fuente="boton_peq", ancho=120,
                alto=36).pack(side="right", padx=(0, 10))
        self.bind("<Return>", lambda ev: guardar())
        self.bind("<Escape>", lambda ev: self.cancelar())

    def _confirmar_eliminar(self, i, e):
        borde = tk.Frame(self.lista, bg=T.NARANJA, padx=1, pady=1)
        borde.pack(fill="x", padx=8, pady=6)
        d = tk.Frame(borde, bg=T.AVISO_BG, padx=14, pady=10)
        d.pack(fill="both")
        T.icono(d, "aviso", 22, bg=T.AVISO_BG).pack(side="left", anchor="n")
        tx = tk.Frame(d, bg=T.AVISO_BG)
        tx.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(tx, text=self.pregunta_eliminar(e), font=T.F["cuerpo_b"], bg=T.AVISO_BG, anchor="w").pack(fill="x")
        tk.Label(tx, text=self.efecto_eliminar(e), font=T.F["pequena"], bg=T.AVISO_BG, fg=T.GRIS, anchor="w",
                 justify="left", wraplength=self.ANCHO - 400).pack(fill="x")
        b = tk.Frame(d, bg=T.AVISO_BG)
        b.pack(side="right")
        T.Boton(b, "Cancelar", self.cancelar, tipo="secundario", fuente="boton_peq", ancho=110, alto=34).pack(side="left", padx=6)
        eliminar = tk.Label(b, text="Eliminar", font=T.F["boton_peq"], bg=T.MAGENTA, fg=T.BLANCO, padx=18, pady=7,
                            cursor="hand2")
        eliminar.pack(side="left")
        eliminar.bind("<Button-1>", lambda ev: (self.eliminar_elemento(i), self.guardado()))

    def pregunta_eliminar(self, e):
        return "¿Eliminar este elemento?"

    def efecto_eliminar(self, e):
        return "Solo se quita de la lista; tus Excel no se tocan."


def entrada(padre, valor="", ancho=None, bg=T.TINTE_VERDE):
    v = tk.StringVar(value=valor)
    c = T.Campo(padre, v)
    if ancho:
        c.entrada.configure(width=ancho)
    return v, c


# ---------------------------------------------------------------- Programas (07)
class ModalProgramas(ModalLista):
    TITULO, AYUDA, CREAR, ANCHO, GUIA = "Programas", "prog", "Crear programa", 860, "Buscar programa…"
    DESCRIPCION = ("Son los programas que podrás elegir al generar un cuadro. Cambia un nombre con el lápiz, quita uno con "
                   "la papelera o crea uno nuevo. Cada programa lleva el nombre de su columna en la matriz de convenios.")

    def elementos(self):
        return self.app.config["programas"]

    def texto_busqueda(self, e):
        return e["nombre"] + " " + e["columna_matriz"]

    def chip_texto(self, total):
        return f"{total} programas · sede Pereira"

    def fila(self, f, i, e, fondo):
        self.acciones(f, i, fondo)
        tx = tk.Frame(f, bg=fondo)
        tx.pack(side="left", fill="x", expand=True)
        tk.Label(tx, text=e["nombre"], font=T.F["cuerpo"], bg=fondo, anchor="w").pack(fill="x")
        tk.Label(tx, text=f"Columna en la matriz: «{e['columna_matriz']}»", font=T.F["pequena"], bg=fondo, fg=T.GRIS,
                 anchor="w").pack(fill="x")

    def editor(self, d, i, e):
        tk.Label(d, text="Nombre del programa", font=T.F["pequena_b"], bg=T.TINTE_VERDE, anchor="w").pack(fill="x")
        v_nombre, c1 = entrada(d, e["nombre"] if e else "")
        c1.pack(fill="x", pady=(2, 8))
        c1.entrada.focus_set()
        tk.Label(d, text="Columna en la matriz de convenios (tal como está escrita)", font=T.F["pequena_b"],
                 bg=T.TINTE_VERDE, anchor="w").pack(fill="x")
        v_col, c2 = entrada(d, e["columna_matriz"] if e else "")
        c2.pack(fill="x", pady=(2, 0))
        error = tk.Label(d, text="", font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.MAGENTA, anchor="w")
        error.pack(fill="x")

        def guardar():
            nombre, col = " ".join(v_nombre.get().split()), " ".join(v_col.get().split()) or \
                f"{' '.join(v_nombre.get().split())} - Pereira"
            otros = [p for j, p in enumerate(self.app.config["programas"]) if j != i]
            if not nombre:
                error.configure(text="Escribe el nombre del programa.")
                return
            if any(normalizar(p["nombre"]) == normalizar(nombre) for p in otros):
                error.configure(text="Ya hay un programa con ese nombre.")
                return
            if i == -1:
                ident = identificador(nombre)
                while any(p["id"] == ident for p in otros):
                    ident += "-2"
                self.app.config["programas"].append({"id": ident, "nombre": nombre, "columna_matriz": col})
            else:
                e.update(nombre=nombre, columna_matriz=col)      # el id no cambia: la última generación lo sigue
            self.app.config["programas"].sort(key=lambda p: normalizar(p["nombre"]))
            self.guardado()
        return guardar

    def eliminar_elemento(self, i):
        del self.app.config["programas"][i]

    def pregunta_eliminar(self, e):
        return f"¿Eliminar «{e['nombre']}»?"


# ---------------------------------------------------------------- Equivalencias (16, 17)
class ModalEquivalencias(ModalLista):
    CREAR, ANCHO, GUIA = "Crear equivalencia", 1000, "Buscar equivalencia…"
    SECCION, ES = "", ""

    def __init__(self, app, duena=None, opciones=None):
        self.opciones = opciones or []
        super().__init__(app, duena)

    def elementos(self):
        return self.app.config[self.SECCION]

    def texto_busqueda(self, e):
        return e["como_aparece"] + " " + e["es"]

    def chip_texto(self, total):
        return f"{total} guardada{'s' if total != 1 else ''}"

    def pie(self, mostrados, total):
        return (f"Mostrando {mostrados} de {total}.\nLas equivalencias se aplican a todos los archivos, de este año y de "
                "otros. Los cambios se guardan al instante.")

    def fila(self, f, i, e, fondo):
        self.acciones(f, i, fondo)
        texto, bg, fg = ORIGEN.get(e.get("origen"), ORIGEN["tu"])
        tk.Label(f, text=texto, font=T.F["pequena_b"], bg=bg, fg=fg, padx=10, pady=3).pack(side="right", padx=12)
        tk.Label(f, text=e["como_aparece"], font=T.F["cuerpo"], bg=fondo, anchor="w", width=34).pack(side="left")
        T.flecha(f, fondo).pack(side="left", padx=10)
        tk.Label(f, text=e["es"], font=T.F["cuerpo_b"], bg=fondo, anchor="w", justify="left",
                 wraplength=360).pack(side="left", fill="x", expand=True)

    def editor(self, d, i, e):
        fila = tk.Frame(d, bg=T.TINTE_VERDE)
        fila.pack(fill="x")
        izq = tk.Frame(fila, bg=T.TINTE_VERDE)
        izq.pack(side="left", fill="x", expand=True)
        tk.Label(izq, text="Como aparece en el Excel", font=T.F["pequena_b"], bg=T.TINTE_VERDE, anchor="w").pack(fill="x")
        v_como, c = entrada(izq, e["como_aparece"] if e else "")
        c.pack(fill="x", pady=(2, 0))
        c.entrada.focus_set()
        tk.Label(izq, text="Escríbelo tal cual aparece en el Excel, con sus errores.", font=T.F["pequena"],
                 bg=T.TINTE_VERDE, fg=T.GRIS, anchor="w").pack(fill="x")
        T.flecha(fila, T.TINTE_VERDE).pack(side="left", padx=12, anchor="n", pady=30)
        der = tk.Frame(fila, bg=T.TINTE_VERDE)
        der.pack(side="left", fill="x", expand=True)
        tk.Label(der, text=self.ES, font=T.F["pequena_b"], bg=T.TINTE_VERDE, anchor="w").pack(fill="x")
        v_es = tk.StringVar(value=e["es"] if e else "")
        cb = ttk.Combobox(der, textvariable=v_es, values=self.opciones, style="CM.TCombobox", font=T.F["cuerpo"], height=12)
        cb.pack(fill="x", pady=(2, 0))

        def filtrar(*_):
            q = normalizar(v_es.get())
            cb.configure(values=[o for o in self.opciones if q in normalizar(o)][:60] if q else self.opciones)
        v_es.trace_add("write", filtrar)
        tk.Label(der, text="Escribe para buscar en la lista.", font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.GRIS,
                 anchor="w").pack(fill="x")
        error = tk.Label(d, text="", font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.MAGENTA, anchor="w")
        error.pack(fill="x")

        def guardar():
            como, es = " ".join(v_como.get().split()), " ".join(v_es.get().split())
            if not como or not es:
                error.configure(text="Completa los dos nombres.")
                return
            if self.opciones and es not in self.opciones:
                error.configure(text=f"Elige «{self.ES.lower()}» de la lista.")
                return
            lista = self.app.config[self.SECCION]
            if any(normalizar(x["como_aparece"]) == normalizar(como) for j, x in enumerate(lista) if j != i):
                error.configure(text="Ya hay una equivalencia para ese nombre.")
                return
            nuevo = {"como_aparece": como, "es": es, "origen": "tu"}
            if i == -1:
                lista.insert(0, nuevo)
            else:
                lista[i] = nuevo
            self.guardado()
        return guardar

    def eliminar_elemento(self, i):
        del self.app.config[self.SECCION][i]

    def pregunta_eliminar(self, e):
        return "¿Eliminar esta equivalencia?"

    def efecto_eliminar(self, e):
        return "El programa volverá a preguntar la próxima vez que encuentre este nombre. Tus Excel no se tocan."


class ModalEqInstituciones(ModalEquivalencias):
    TITULO, AYUDA, SECCION, ES = "Equivalencias de instituciones", "eq_inst", "equivalencias_instituciones", \
        "Institución de la matriz de convenios"
    DESCRIPCION = ("Nombres que en un Excel se escriben distinto pero son la misma institución. El programa los trata como "
                   "una sola y no vuelve a preguntar.")


class ModalEqProgramas(ModalEquivalencias):
    TITULO, AYUDA, SECCION, ES = "Equivalencias de programas", "eq_prog", "equivalencias_programas", "Programa"
    DESCRIPCION = ("Nombres de programa que aparecen distinto en los reportes (por ejemplo «Ingeniería Industrial "
                   "Distancia») y son un programa de la lista.")


# ---------------------------------------------------------------- Tipos de persona (18)
class ModalTipos(ModalLista):
    TITULO, AYUDA, CREAR, ANCHO, GUIA = "Tipos de persona", "tipos", "Crear tipo", 1000, "Buscar tipo o valor…"
    DESCRIPCION = ("El cuadro agrupa a las personas en estos tipos. Cada tipo reconoce los valores que aparecen en la "
                   "columna de vínculo de los Excel. Si aparece un valor nuevo, agrégalo al tipo que le corresponde.")

    def __init__(self, app, duena=None, no_reconocidos=None):
        self.no_reconocidos = no_reconocidos or []
        super().__init__(app, duena)

    def elementos(self):
        return self.app.config["tipos_persona"]

    def texto_busqueda(self, e):
        return e["nombre"] + " " + " ".join(e["valores"])

    def chip_texto(self, total):
        return f"{total} tipos"

    def pie(self, mostrados, total):
        return ("El tipo Internacionalización en casa es base: se asigna a todo el reporte de internacionalización en "
                "casa y no se elimina.\nLos cambios se guardan al instante.")

    def fila(self, f, i, e, fondo):
        self.acciones(f, i, fondo, bloqueado=e.get("base"), ayuda_bloqueo="Tipo base: no se puede eliminar")
        tk.Label(f, text=e["nombre"], font=T.F["cuerpo_b"], bg=fondo, anchor="w", width=26).pack(side="left", anchor="n")
        chips = tk.Frame(f, bg=fondo)
        chips.pack(side="left", fill="x", expand=True)
        if e.get("base"):
            tk.Label(chips, text="Todo lo que viene del reporte de internacionalización en casa", font=T.F["pequena"],
                     bg=fondo, fg=T.GRIS).pack(anchor="w")
        _chips(chips, e["valores"], fondo, por_linea=3)

    def editor(self, d, i, e):
        valores = list(e["valores"]) if e else []
        tk.Label(d, text="Nombre en el cuadro", font=T.F["pequena_b"], bg=T.TINTE_VERDE, anchor="w").pack(fill="x")
        v_nombre, c = entrada(d, e["nombre"] if e else "")
        c.pack(fill="x", pady=(2, 8))
        c.entrada.focus_set()
        zona = tk.Frame(d, bg=T.TINTE_VERDE)
        zona.pack(fill="x")

        def pintar_valores():
            for w in zona.winfo_children():
                w.destroy()
            if e and e.get("base"):
                tk.Label(zona, text="Tipo base: recibe todo el reporte de internacionalización en casa; no lleva valores.",
                         font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.GRIS, anchor="w").pack(fill="x")
                return
            tk.Label(zona, text="Valores que reconoce en el Excel", font=T.F["pequena_b"], bg=T.TINTE_VERDE,
                     anchor="w").pack(fill="x")
            _chips(zona, valores, T.TINTE_VERDE, quitar=lambda v: (valores.remove(v), pintar_valores()))
            fila = tk.Frame(zona, bg=T.TINTE_VERDE)
            fila.pack(fill="x", pady=(6, 0))
            v_nuevo, cn = entrada(fila)
            cn.pack(side="left", fill="x", expand=True)
            T.Boton(fila, "+  Agregar valor", lambda: agregar(v_nuevo.get()), tipo="secundario", fuente="boton_peq",
                    ancho=170, alto=36).pack(side="left", padx=(10, 0))
            vistos = [v for v in self.no_reconocidos if normalizar(v) not in map(normalizar, valores)]
            if vistos:
                caja = tk.Frame(zona, bg=T.BLANCO, padx=12, pady=8)
                caja.pack(fill="x", pady=(8, 0))
                tk.Label(caja, text="Valores que el programa vio y no reconoció", font=T.F["pequena_b"], bg=T.BLANCO,
                         anchor="w").pack(fill="x")
                fv = tk.Frame(caja, bg=T.BLANCO)
                fv.pack(fill="x", pady=(4, 0))
                for v in vistos:
                    b = tk.Label(fv, text=f"+ {v}", font=T.F["pequena_b"], bg=T.AVISO_BG, fg=T.AVISO_TXT, padx=10,
                                 pady=3, cursor="hand2")
                    b.pack(side="left", padx=(0, 6))
                    b.bind("<Button-1>", lambda ev, x=v: agregar(x))
                tk.Label(caja, text="Toca un valor para agregarlo a este tipo.", font=T.F["pequena"], bg=T.BLANCO,
                         fg=T.GRIS, anchor="w").pack(fill="x")

        def agregar(v):
            v = " ".join(v.split())
            if v and normalizar(v) not in map(normalizar, valores):
                valores.append(v)
            pintar_valores()
        pintar_valores()
        error = tk.Label(d, text="", font=T.F["pequena"], bg=T.TINTE_VERDE, fg=T.MAGENTA, anchor="w")
        error.pack(fill="x")

        def guardar():
            nombre = " ".join(v_nombre.get().split())
            if not nombre:
                error.configure(text="Escribe el nombre del tipo.")
                return
            usados = {normalizar(v): t["nombre"] for j, t in enumerate(self.app.config["tipos_persona"]) if j != i
                      for v in t["valores"]}
            repetido = next((v for v in valores if normalizar(v) in usados), None)
            if repetido:
                error.configure(text=f"«{repetido}» ya está en el tipo {usados[normalizar(repetido)]}.")
                return
            if i == -1:
                self.app.config["tipos_persona"].insert(-1, {"id": identificador(nombre), "nombre": nombre,
                                                              "valores": valores, "base": False})
            else:
                e.update(nombre=nombre, valores=valores)
            self.guardado()
        return guardar

    def eliminar_elemento(self, i):
        del self.app.config["tipos_persona"][i]

    def pregunta_eliminar(self, e):
        return f"¿Eliminar el tipo «{e['nombre']}»?"

    def efecto_eliminar(self, e):
        return "Las personas con esos valores dejarán de contarse y aparecerán como avisos. Tus Excel no se tocan."


def _chips(padre, valores, fondo, quitar=None, por_linea=4):
    fila = None
    for n, v in enumerate(valores):
        if n % por_linea == 0:
            fila = tk.Frame(padre, bg=fondo)
            fila.pack(fill="x", pady=2)
        chip = tk.Frame(fila, bg=T.LINEA, padx=1, pady=1)
        chip.pack(side="left", padx=(0, 6))
        dentro = tk.Frame(chip, bg=T.BLANCO)
        dentro.pack()
        tk.Label(dentro, text=v, font=T.F["pequena"], bg=T.BLANCO, padx=8, pady=2).pack(side="left")
        if quitar:
            x = tk.Label(dentro, text="×", font=T.F["cuerpo_b"], bg=T.BLANCO, fg=T.GRIS, padx=4, cursor="hand2")
            x.pack(side="left")
            x.bind("<Button-1>", lambda e, val=v: quitar(val))


# ---------------------------------------------------------------- Copias y almacenamiento (24)
class ModalCopias(D.Modal):
    def __init__(self, app, duena=None):
        super().__init__(duena or app.raiz, "Copias y almacenamiento", ancho=900)
        self.app = app
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.pintar()

    def pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        a = self.app.almacen
        fila = tk.Frame(c, bg=T.BLANCO)
        fila.pack(fill="x")
        tk.Label(fila, text="Copias y almacenamiento", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(fila, "copias").pack(side="left", padx=10)
        tk.Label(c, text="Dónde se guarda la configuración", font=T.F["seccion"], bg=T.BLANCO, anchor="w").pack(fill="x", pady=(14, 6))
        from ..configuracion.almacen import NOMBRE_ARCHIVO
        for nombre, carpeta in (("Carpeta del usuario", a.lugares["usuario"]), ("Junto al programa", a.lugares["programa"])):
            borde = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
            borde.pack(fill="x", pady=(0, 6))
            d = tk.Frame(borde, bg=T.BLANCO, padx=14, pady=8)
            d.pack(fill="both")
            ruta = carpeta / NOMBRE_ARCHIVO
            existe = ruta.exists()
            tx = tk.Frame(d, bg=T.BLANCO)
            tx.pack(side="left", fill="x", expand=True)
            tk.Label(tx, text=nombre, font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(fill="x")
            tk.Label(tx, text=str(ruta), font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
            T.Boton(d, "Abrir carpeta", lambda x=carpeta: abrir(x), tipo="secundario", fuente="boton_peq", ancho=150,
                    alto=34).pack(side="right")
            tk.Label(d, text="Al día" if existe else "No se pudo escribir", font=T.F["pequena_b"],
                     bg="#E3EED2" if existe else T.ROSA_SUAVE, fg=T.OK_TXT if existe else T.MAGENTA, padx=10,
                     pady=3).pack(side="right", padx=10)
        T.Franja(c, "info", "Al abrir se usa la copia más reciente; si falta una o está dañada, se restaura desde la otra "
                 "y se avisa.").pack(fill="x", pady=(4, 12))
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        copias = a.copias_de_seguridad()
        tk.Label(cab, text=f"Copias de seguridad ({len(copias)} de 10)", font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
        T.Boton(cab, "Crear copia ahora", self.crear, tipo="secundario", fuente="boton_peq", ancho=190,
                alto=36).pack(side="right")
        lista = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        lista.pack(fill="x", pady=(8, 0))
        if not copias:
            tk.Label(lista, text="Todavía no hay copias. Se crea una automática antes del primer cambio de cada sesión.",
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, pady=12).pack(fill="x")
        for n, cp in enumerate(copias):
            fondo = T.BLANCO if n % 2 == 0 else T.FONDO
            f = tk.Frame(lista, bg=fondo, padx=14, pady=6)
            f.pack(fill="x")
            hora = datetime.fromisoformat(cp.creada_en).astimezone().replace(tzinfo=None)
            tk.Label(f, text=cuando(hora), font=T.F["cuerpo"], bg=fondo, width=22, anchor="w").pack(side="left")
            tk.Label(f, text=MOTIVO.get(cp.motivo, cp.motivo), font=T.F["pequena"], bg=fondo, fg=T.GRIS).pack(side="left")
            if cp.restaurable:
                T.Enlace(f, "Restaurar", lambda x=cp: self.restaurar(x), fuente="pequena_b").pack(side="right")
            else:
                tk.Label(f, text="No se puede restaurar", font=T.F["pequena"], bg=fondo, fg=T.DESACT_TXT).pack(side="right")
        pie = self.botones()
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=150).pack(side="right")

    def crear(self):
        self.app.almacen.crear_copia()
        self.pintar()

    def restaurar(self, copia):
        hora = datetime.fromisoformat(copia.creada_en).astimezone().replace(tzinfo=None)
        if D.aviso(self, "¿Restaurar esta copia?", "aviso",
                   f"Se reemplaza la configuración actual por la copia de {cuando(hora)}. Antes se guarda la actual como "
                   "copia nueva, así que puedes volver atrás.", [("Restaurar", "si", "primario"),
                                                                ("Cancelar", "no", "secundario")]) != "si":
            return
        self.app.almacen.restaurar(copia)
        self.app.guardar_config(ya_guardada=True)
        self.pintar()
