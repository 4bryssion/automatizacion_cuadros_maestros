"""Fuentes de datos (mockup 15), Elegir columna… y Probar lectura de la carpeta (mockup 22).

Los estados (exacta, por confirmar, sin identificar) salen de leer la carpeta de la ventana principal con la
configuración actual: lo que se cambia aquí se guarda al instante y se vuelve a leer para mostrar cómo queda.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from .. import ajustes as A
from ..lectura import leer_carpeta
from ..lectura.modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR
from ..texto import normalizar
from . import dialogos as D
from . import tema as T
from .modelo import vigencia

ESTADO_TXT = {EXACTA: ("ok", "Exacta", T.OK_TXT), POR_CONFIRMAR: ("aviso", "Por confirmar", T.AVISO_TXT),
              SIN_IDENTIFICAR: ("mal", "Sin identificar", T.MAGENTA), A.SIN_LEER: ("gris", "Sin leer", T.GRIS)}
FONDO_ESTADO = {POR_CONFIRMAR: T.AVISO_BG, SIN_IDENTIFICAR: T.ROSA_SUAVE}
PUNTO = {EXACTA: T.VERDE, POR_CONFIRMAR: T.NARANJA, SIN_IDENTIFICAR: T.MAGENTA}
EXPLICACION = {
    POR_CONFIRMAR: "El programa cree que «{enc}» trae {dato}, pero el nombre no es idéntico; mientras no lo confirmes "
                   "no la usa. Confírmala o elige otra: se guarda para los próximos archivos.",
    SIN_IDENTIFICAR: "El programa buscó la columna de {dato} por nombre y no encontró una que se parezca lo bastante. "
                     "Elige cuál es; se guarda para los próximos archivos.",
}
MODOS = [(A.POR_ANIO, "Se lee el año del nombre (2022)"), (A.POR_SEMESTRE, "Se leen del nombre (2022-1)")]


def contexto_de_lectura(app):
    """Carpeta y vigencia de la ventana principal. Sin vigencia válida se lee solo la matriz."""
    carpeta = A.carpeta_valida(app.ventana.v_carpeta.get()) or A.carpeta_valida(app.carpeta_actual())
    desde, hasta = app.ventana.anios_elegidos()
    if desde is None or hasta is None or desde > hasta:
        desde, hasta = 1, 0
    return carpeta, desde, hasta


def leer(app, duena):
    carpeta, desde, hasta = contexto_de_lectura(app)
    if not carpeta:
        return None
    config = app.config
    return D.en_espera(duena, lambda: leer_carpeta(carpeta, config, desde, hasta))


# ---------------------------------------------------------------- Fuentes de datos (15)
class ModalFuentes(D.Modal):
    def __init__(self, app, duena=None, fuente_id=None, dato=None, lectura=None):
        super().__init__(duena or app.raiz, "Fuentes de datos", ancho=1100)
        self.app = app
        self.elegida = fuente_id or app.config["fuentes"][0]["id"]
        self.resaltar = dato
        self.renombrando = False
        self.lectura = lectura
        self.carpeta, self.desde, self.hasta = contexto_de_lectura(app)
        if self.lectura is None:
            self._leer()
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.pintar()

    # lectura
    def _leer(self):
        try:
            self.lectura = leer(self.app, self.master if not self.winfo_viewable() else self)
        except Exception:   # noqa: BLE001 — si algo falla al leer, se muestra «Sin leer»; generar dirá qué pasó
            self.lectura = None

    def releer(self):
        self._leer()
        self.pintar()

    def cambio(self, releer=True):
        """Guarda al instante y, si el cambio afecta a la lectura, vuelve a leer para mostrar cómo queda."""
        self.app.guardar_config()
        if releer and self.carpeta:
            self.releer()
        else:
            self.pintar()

    # pintura
    def pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        self.estados = {e.id: e for e in A.estado_fuentes(self.app.config, self.lectura)}
        todos = [d for e in self.estados.values() for d in e.datos]
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Fuentes de datos", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "fuentes").pack(side="left", padx=10)
        for estado, texto, tipo in ((SIN_IDENTIFICAR, "sin identificar", "error"), (POR_CONFIRMAR, "por confirmar", "aviso"),
                                    (EXACTA, "exactas", "ok")):
            n = sum(1 for d in todos if d.estado == estado)
            if n:
                T.chip(cab, f"{n} {texto}", tipo).pack(side="right", padx=(8, 0))
        if not self.lectura:
            T.chip(cab, "Sin leer", "gris").pack(side="right")
        tk.Label(c, text="Aquí dices cómo reconoce el programa cada tipo de Excel: qué archivos son, dónde están los "
                         "encabezados y qué columna trae cada dato. Lo exacto se aplica solo; lo dudoso te lo pide "
                         "confirmar.", font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=self.ancho - 80).pack(fill="x", pady=(8, 4))
        if not self.carpeta:
            T.Franja(c, "gris", "Elige la carpeta en la ventana principal para ver cómo se lee cada archivo. Sin ella "
                     "puedes cambiar la configuración, pero no ver los estados.").pack(fill="x", pady=(4, 0))
        else:
            tk.Label(c, text=f"Leído de: {self.carpeta}  ·  Vigencia: "
                             f"{vigencia(self.desde, self.hasta) if self.hasta >= self.desde else 'solo la matriz'}",
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
        cuerpo = tk.Frame(c, bg=T.BLANCO)
        cuerpo.pack(fill="both", expand=True, pady=(12, 0))
        izq = tk.Frame(cuerpo, bg=T.BLANCO, width=310)
        izq.pack(side="left", fill="y", anchor="n")
        izq.pack_propagate(False)
        for f in self.app.config["fuentes"]:
            self._tarjeta(izq, self.estados[f["id"]])
        tk.Label(izq, text="Las fuentes son fijas: el cálculo necesita estos tres tipos de Excel. Si un Excel cambia, "
                           "ajústalo aquí.", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                 wraplength=290).pack(fill="x", pady=(4, 0))
        der = T.desplazable(cuerpo, 540)
        der.pack(side="left", fill="both", expand=True, padx=(24, 0))
        self._detalle(der.interior, self.estados[self.elegida])
        self.lienzo_detalle = der.lienzo
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        tk.Frame(pie, bg=T.LINEA, height=1).pack(fill="x", pady=(0, 14))
        probar = T.Boton(pie, "Probar lectura de la carpeta", self.probar, tipo="secundario", ancho=300)
        probar.pack(side="left")
        probar.activar(bool(self.carpeta))
        tk.Label(pie, text="Los cambios se guardan al instante." if self.carpeta else
                 "Para probar la lectura, elige la carpeta en la ventana principal.", font=T.F["pequena"],
                 bg=T.BLANCO, fg=T.GRIS).pack(side="left", padx=16)
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=160).pack(side="right")

    def _tarjeta(self, padre, e: A.EstadoFuente):
        sel = e.id == self.elegida
        borde = tk.Frame(padre, bg=T.VERDE_CTA if sel else T.LINEA, padx=2 if sel else 1, pady=2 if sel else 1)
        borde.pack(fill="x", pady=(0, 12))
        fondo = T.TINTE_VERDE if sel else T.BLANCO
        t = tk.Frame(borde, bg=fondo, padx=16, pady=12, cursor="hand2")
        t.pack(fill="both")
        partes = [tk.Label(t, text=e.nombre, font=T.F["seccion"], bg=fondo, anchor="w", cursor="hand2"),
                  tk.Label(t, text=e.archivos, font=T.F["pequena"], bg=fondo, fg=T.GRIS, anchor="w", cursor="hand2")]
        for p in partes:
            p.pack(fill="x")
        fila = tk.Frame(t, bg=fondo)
        fila.pack(fill="x", pady=(8, 0))
        for estado, texto in ((EXACTA, "exactas"), (POR_CONFIRMAR, "por confirmar"), (SIN_IDENTIFICAR, "sin identificar")):
            n = e.cuenta(estado)
            if n:
                T.punto(fila, PUNTO[estado], 11).pack(side="left", padx=(0, 5))
                tk.Label(fila, text=f"{n} {texto}", font=T.F["pequena_b"], bg=fondo).pack(side="left", padx=(0, 12))
        if not e.leidos:
            tk.Label(fila, text="Sin leer" if self.carpeta else "Sin carpeta", font=T.F["pequena_b"], bg=fondo,
                     fg=T.GRIS).pack(side="left")
        for w in (t, *partes, fila, *fila.winfo_children()):
            w.bind("<Button-1>", lambda ev, i=e.id: self.seleccionar(i))

    def seleccionar(self, fuente_id):
        self.elegida, self.resaltar, self.renombrando = fuente_id, None, False
        self.pintar()

    def _seccion(self, padre, n, texto):
        tk.Label(padre, text=f"{n}  {texto}", font=T.F["seccion"], bg=T.BLANCO, fg=T.VERDE_CTA,
                 anchor="w").pack(fill="x", pady=(14, 8))

    def _detalle(self, d, e: A.EstadoFuente):
        f = A.fuente(self.app.config, e.id)
        cab = tk.Frame(d, bg=T.BLANCO)
        cab.pack(fill="x")
        if self.renombrando:
            v = tk.StringVar(value=f["nombre"])
            campo = T.Campo(cab, v)
            campo.pack(side="left", fill="x", expand=True)
            campo.entrada.focus_set()
            error = tk.Label(d, font=T.F["pequena"], bg=T.BLANCO, fg=T.MAGENTA, anchor="w")

            def guardar(_=None):
                try:
                    A.renombrar_fuente(self.app.config, e.id, v.get())
                except ValueError as err:
                    error.configure(text=str(err))
                    campo.error()
                    return
                self.renombrando = False
                self.cambio(releer=False)
            self.guardar_nombre = guardar
            campo.entrada.bind("<Return>", guardar)
            campo.entrada.bind("<Escape>", lambda ev: (setattr(self, "renombrando", False), self.pintar(), "break")[2])
            T.Boton(cab, "Guardar", guardar, fuente="boton_peq", ancho=110, alto=38).pack(side="left", padx=(10, 0))
            error.pack(fill="x")
        else:
            tk.Label(cab, text=f["nombre"], font=T.F["modal_titulo"], bg=T.BLANCO, anchor="w").pack(side="left")
            T.Boton(cab, "Cambiar nombre", lambda: (setattr(self, "renombrando", True), self.pintar()),
                    tipo="secundario", fuente="boton_peq", ancho=T.F["boton_peq"].measure("Cambiar nombre") + 40, alto=36).pack(side="right")

        # 1 Cómo se encuentra el archivo
        self._seccion(d, 1, "Cómo se encuentra el archivo")
        fila = tk.Frame(d, bg=T.BLANCO)
        fila.pack(fill="x")
        fila.grid_columnconfigure(0, weight=1, uniform="a")
        fila.grid_columnconfigure(1, weight=1, uniform="a")
        tk.Label(fila, text="El nombre del archivo contiene", font=T.F["pequena_b"], bg=T.BLANCO,
                 anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(fila, text="Año y semestre", font=T.F["pequena_b"], bg=T.BLANCO, anchor="w").grid(row=0, column=1,
                                                                                                   sticky="w", padx=(16, 0))
        v_contiene = tk.StringVar(value=", ".join(f["archivo"]["contiene"]))
        c_contiene = T.Campo(fila, v_contiene)
        c_contiene.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        error = tk.Label(fila, font=T.F["pequena"], bg=T.BLANCO, fg=T.MAGENTA, anchor="w")
        error.grid(row=2, column=0, sticky="w")

        def guardar_contiene(_=None):
            if normalizar(v_contiene.get()) == normalizar(", ".join(f["archivo"]["contiene"])):
                return
            try:
                A.poner_contiene(f, v_contiene.get())
            except ValueError as err:
                error.configure(text=str(err))
                c_contiene.error()
                return
            self.cambio()
        self.guardar_contiene = guardar_contiene
        c_contiene.entrada.bind("<Return>", guardar_contiene)
        c_contiene.entrada.bind("<FocusOut>", guardar_contiene, add="+")
        if e.id == "matriz":
            T.campo_bloqueado(fila, "Un solo archivo (el más reciente)").grid(row=1, column=1, sticky="ew", padx=(16, 0),
                                                                              pady=(4, 0))
        else:
            self.opc_modo = T.Opciones(fila, MODOS, A.modo_periodo(f),
                                       lambda modo: (A.poner_modo_periodo(f, modo), self.cambio()))
            self.opc_modo.grid(row=1, column=1, sticky="ew", padx=(16, 0), pady=(4, 0))
        excluye = f["archivo"].get("excluye") or []
        if excluye:
            tk.Label(fila, text="Se ignoran los archivos cuyo nombre lleva: " + ", ".join(f"«{x}»" for x in excluye),
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").grid(row=3, column=0, columnspan=2,
                                                                                    sticky="w", pady=(4, 0))

        # 2 Fila de encabezados
        self._seccion(d, 2, "Fila de encabezados")
        fila = tk.Frame(d, bg=T.BLANCO)
        fila.pack(fill="x")
        conf = f.get("fila_encabezado") or {"automatica": True, "fila": 1}
        self.int_fila = T.Interruptor(fila, conf.get("automatica", True),
                                      lambda si: (A.poner_fila_encabezados(self.app.config, e.id, si), self.cambio()),
                                      texto_si="", texto_no="")
        self.int_fila.pack(side="left")
        tk.Label(fila, text="Detectarla automáticamente", font=T.F["cuerpo_b"], bg=T.BLANCO).pack(side="left", padx=10)
        if conf.get("automatica", True):
            T.chip(fila, A.texto_filas_detectadas(e.filas_encabezado), "gris").pack(side="right")
        else:
            tk.Label(fila, text="Fila", font=T.F["cuerpo"], bg=T.BLANCO).pack(side="left", padx=(20, 6))
            v_fila = tk.StringVar(value=str(conf.get("fila") or 1))
            sp = tk.Spinbox(fila, from_=1, to=50, width=4, textvariable=v_fila, font=T.F["cuerpo"], justify="center",
                            relief="solid", bd=1)
            sp.pack(side="left")

            def guardar_fila(_=None):
                try:
                    n = int(v_fila.get())
                    if n == conf.get("fila"):
                        return
                    A.poner_fila_encabezados(self.app.config, e.id, False, n)
                except ValueError:
                    v_fila.set(str(conf.get("fila") or 1))
                    return
                self.cambio()
            self.guardar_fila = guardar_fila
            sp.configure(command=guardar_fila)
            sp.bind("<Return>", guardar_fila)
            sp.bind("<FocusOut>", guardar_fila)
            tk.Label(fila, text="(la primera fila del Excel es la 1)", font=T.F["pequena"], bg=T.BLANCO,
                     fg=T.GRIS).pack(side="left", padx=8)

        # 3 Qué columna trae cada dato
        self._seccion(d, 3, "Qué columna trae cada dato")
        self._tabla_datos(d, e)

        # 4 Qué filas se usan
        self._seccion(d, 4, "Qué filas se usan")
        filtros = f.setdefault("filtros", {})
        if e.id == "matriz":
            tk.Label(d, text="Se usan todas las filas con institución. Qué convenios entran a cada cuadro lo deciden la "
                             "columna del programa (Programas) y las Reglas de cruce.", font=T.F["cuerpo"], bg=T.BLANCO,
                     anchor="w", justify="left", wraplength=680).pack(fill="x")
            return

        def poner(clave, valor):
            filtros[clave] = valor
            self.cambio(releer=False)
        T.Casilla(d, "Solo las filas del programa elegido al generar", filtros.get("solo_programa_elegido", True),
                  lambda v: poner("solo_programa_elegido", v)).pack(fill="x", pady=(0, 8))
        sede = filtros.get("solo_sede")
        T.Casilla(d, f"Solo las filas de la sede {sede or 'Pereira'}", bool(sede),
                  lambda v: poner("solo_sede", "Pereira" if v else None)).pack(fill="x", pady=(0, 8))
        if e.id == "internacionalizacion_en_casa":
            T.Casilla(d, "Omitir las actividades sin institución (se cuentan aparte, no se listan)",
                      filtros.get("omitir_sin_institucion", True),
                      lambda v: poner("omitir_sin_institucion", v)).pack(fill="x", pady=(0, 8))

    def _tabla_datos(self, d, e: A.EstadoFuente):
        caja = tk.Frame(d, bg=T.LINEA, padx=1, pady=1)
        caja.pack(fill="x")
        cab = tk.Frame(caja, bg=T.GRIS_OSC, padx=14, pady=9)
        cab.pack(fill="x")
        anchos = (200, 230, 150)
        for j, (texto, w) in enumerate(zip(("Dato que necesita", "Columna en el Excel", "Estado"), anchos)):
            cab.grid_columnconfigure(j, minsize=w)
            tk.Label(cab, text=texto, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO, anchor="w").grid(row=0, column=j,
                                                                                                          sticky="w")
        primero = None
        for i, dato in enumerate(e.datos):
            fondo = FONDO_ESTADO.get(dato.estado, T.BLANCO if i % 2 == 0 else T.FONDO)
            if self.resaltar == dato.dato:
                fondo = T.TINTE_VERDE
            f = tk.Frame(caja, bg=fondo, padx=14, pady=7)
            f.pack(fill="x")
            for j, w in enumerate(anchos):
                f.grid_columnconfigure(j, minsize=w)
            f.grid_columnconfigure(3, weight=1)
            tk.Label(f, text=dato.nombre, font=T.F["cuerpo_b"], bg=fondo, anchor="w", justify="left",
                     wraplength=190).grid(row=0, column=0, sticky="w")
            enc = dato.encabezado or "—"
            if dato.elegida and dato.estado in (EXACTA, A.SIN_LEER):
                enc = dato.elegida
            tk.Label(f, text=enc, font=T.F["cuerpo"], bg=fondo, anchor="w", justify="left",
                     wraplength=220).grid(row=0, column=1, sticky="w")
            simbolo, texto, color = ESTADO_TXT[dato.estado]
            est = tk.Frame(f, bg=fondo)
            est.grid(row=0, column=2, sticky="w")
            if simbolo == "ok":
                T.marca(est, "ok", bg=fondo, d=18).pack(side="left")
            elif simbolo == "mal":
                T.marca(est, "mal", bg=fondo, d=18).pack(side="left")
            else:
                T.icono(est, simbolo, 18, bg=fondo).pack(side="left")
            tk.Label(est, text=texto, font=T.F["pequena_b"], bg=fondo, fg=color).pack(side="left", padx=(6, 0))
            acciones = tk.Frame(f, bg=fondo)
            acciones.grid(row=0, column=3, sticky="e")
            if dato.estado == POR_CONFIRMAR:
                T.Boton(acciones, "Confirmar", lambda x=dato: self.confirmar(e.id, x), fuente="boton_peq",
                        ancho=T.F["boton_peq"].measure("Confirmar") + 36, alto=32).pack(side="left", padx=(0, 6))
            if dato.estado in (POR_CONFIRMAR, SIN_IDENTIFICAR):
                T.Boton(acciones, "Elegir columna…", lambda x=dato: self.elegir(e, x), tipo="secundario",
                        fuente="boton_peq", ancho=T.F["boton_peq"].measure("Elegir columna…") + 36, alto=32).pack(side="left")
                primero = primero or dato
            else:
                T.Enlace(acciones, "Cambiar", lambda x=dato: self.elegir(e, x), fuente="pequena_b").pack(side="left")
            if dato.elegida:
                tk.Label(f, text=f"Elegida por ti: «{dato.elegida}»", font=T.F["pequena"], bg=fondo, fg=T.GRIS,
                         anchor="w").grid(row=1, column=1, columnspan=2, sticky="w")
        if primero:
            tk.Label(d, text=EXPLICACION[primero.estado].format(enc=primero.encabezado, dato=f"«{primero.nombre}»"),
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=680).pack(fill="x", pady=(6, 0))
        if e.id == "matriz":
            tk.Label(d, text="La columna de cada programa se cambia en Programas.", font=T.F["pequena"], bg=T.BLANCO,
                     fg=T.GRIS, anchor="w").pack(fill="x", pady=(6, 0))

    # acciones
    def confirmar(self, fuente_id, dato: A.EstadoDato):
        A.elegir_columna(self.app.config, fuente_id, dato.dato, dato.encabezado)
        self.resaltar = dato.dato
        self.cambio()

    def elegir(self, e: A.EstadoFuente, dato: A.EstadoDato):
        usadas = {normalizar(x.encabezado): x.nombre for x in e.datos
                  if x.dato != dato.dato and x.encabezado and x.estado == EXACTA}
        eleccion = ElegirColumna(self, e.nombre, dato, e.encabezados, usadas).mostrar()
        if eleccion is None:
            return
        A.elegir_columna(self.app.config, e.id, dato.dato, eleccion or None)
        self.resaltar = dato.dato
        self.cambio()

    def probar(self):
        arreglar = ProbarLectura(self, self.app, self.lectura).mostrar()
        if arreglar:
            self.seleccionar(arreglar)


# ---------------------------------------------------------------- Elegir columna…
class ElegirColumna(D.Modal):
    """Lista de los encabezados del Excel para decir cuál trae el dato. Devuelve el encabezado, "" para quitar la
    elegida (vuelve a buscar por nombre) o None si se cancela."""

    def __init__(self, duena, fuente, dato: A.EstadoDato, encabezados, usadas):
        super().__init__(duena, "Elegir columna", ancho=640)
        self.dato, self.usadas = dato, usadas
        self.encabezados = encabezados
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x")
        tk.Label(fila, text=f"¿Qué columna trae «{dato.nombre}»?", font=T.F["modal_titulo"], bg=T.BLANCO, anchor="w",
                 justify="left", wraplength=560).pack(side="left", fill="x")
        tk.Label(self.cuerpo, text=f"{fuente} · Son los encabezados de los archivos leídos. Lo que elijas se guarda y "
                                   "sirve también para los próximos archivos.", font=T.F["cuerpo"], bg=T.BLANCO,
                 fg=T.GRIS, anchor="w", justify="left", wraplength=570).pack(fill="x", pady=(6, 10))
        self.v_buscar = tk.StringVar()
        T.Campo(self.cuerpo, self.v_buscar, guia="Buscar columna…").pack(fill="x")
        self.v_buscar.trace_add("write", lambda *a: self.pintar())
        marco = tk.Frame(self.cuerpo, bg=T.LINEA, padx=1, pady=1)
        marco.pack(fill="x", pady=(10, 0))
        self.lista = T.desplazable(marco, 300)
        self.lista.pack(fill="both", expand=True)
        actual = dato.elegida or (dato.encabezado if dato.estado != SIN_IDENTIFICAR else None) or ""
        self.v_elegida = tk.StringVar(value=actual)
        tk.Label(self.cuerpo, text="¿No está en la lista? Escríbela tal como está en el Excel:", font=T.F["pequena_b"],
                 bg=T.BLANCO, anchor="w").pack(fill="x", pady=(12, 4))
        self.v_escrita = tk.StringVar(value=actual if actual and normalizar(actual) not in
                                      {normalizar(h) for h in encabezados} else "")
        T.Campo(self.cuerpo, self.v_escrita, guia="Encabezado de la columna").pack(fill="x")
        self.v_escrita.trace_add("write", lambda *a: self.v_escrita.get() and self.v_elegida.set(""))
        self.error = tk.Label(self.cuerpo, font=T.F["pequena"], bg=T.BLANCO, fg=T.MAGENTA, anchor="w")
        self.error.pack(fill="x")
        pie = self.botones()
        if dato.elegida:
            T.Enlace(pie, "Quitar la elegida", lambda: self.cerrar(""), fuente="pequena_b").pack(side="left")
        T.Boton(pie, "Usar esta columna", self.aceptar, ancho=200).pack(side="right")
        T.Boton(pie, "Cancelar", lambda: self.cerrar(None), tipo="secundario", ancho=130).pack(side="right", padx=10)
        self.bind("<Return>", lambda e: self.aceptar())
        self.pintar()

    def pintar(self):
        caja = self.lista.interior
        for w in caja.winfo_children():
            w.destroy()
        q = normalizar(self.v_buscar.get())
        visibles = [h for h in self.encabezados if not q or q in normalizar(h)]
        if not self.encabezados:
            tk.Label(caja, text="No hay encabezados leídos de esta fuente (no se encontró el archivo en la carpeta o no "
                                "tiene encabezados). Puedes escribir el nombre de la columna abajo.", font=T.F["cuerpo"],
                     bg=T.BLANCO, fg=T.GRIS, justify="left", wraplength=540, pady=16, padx=14).pack(fill="x")
        elif not visibles:
            tk.Label(caja, text="Ninguna columna coincide con la búsqueda.", font=T.F["cuerpo"], bg=T.BLANCO,
                     fg=T.GRIS, pady=16).pack()
        for i, h in enumerate(visibles):
            fondo = T.BLANCO if i % 2 == 0 else T.FONDO
            f = tk.Frame(caja, bg=fondo, padx=12, pady=6)
            f.pack(fill="x")
            rb = tk.Radiobutton(f, variable=self.v_elegida, value=h, bg=fondo, activebackground=fondo,
                                highlightthickness=0, text=h, font=T.F["cuerpo"], anchor="w", justify="left",
                                wraplength=380, tristatevalue="\x00", command=lambda: self.v_escrita.set(""))
            rb.pack(side="left")
            if self.dato.estado == POR_CONFIRMAR and normalizar(h) == normalizar(self.dato.encabezado or ""):
                T.chip(f, "Sugerida", "aviso", ).pack(side="right")
            elif normalizar(h) in self.usadas:
                tk.Label(f, text=f"Ya la usa: {self.usadas[normalizar(h)]}", font=T.F["pequena"], bg=fondo,
                         fg=T.GRIS).pack(side="right")

    def aceptar(self):
        valor = " ".join((self.v_escrita.get() or self.v_elegida.get()).split())
        if not valor:
            self.error.configure(text="Elige una columna de la lista o escribe su nombre.")
            return
        if normalizar(valor) in self.usadas:
            self.error.configure(text=f"Esa columna ya trae «{self.usadas[normalizar(valor)]}». Elige otra.")
            return
        self.cerrar(valor)


# ---------------------------------------------------------------- Probar lectura de la carpeta (22)
ESTADO_PRUEBA = {A.LISTO: ("ok", T.OK_TXT), POR_CONFIRMAR: ("aviso", T.AVISO_TXT), SIN_IDENTIFICAR: ("mal", T.MAGENTA),
                 A.NO_SE_ENCONTRO: ("mal", T.MAGENTA), A.NO_SE_PUDO_LEER: ("mal", T.MAGENTA),
                 A.SIN_ENCABEZADOS: ("mal", T.MAGENTA)}


class ProbarLectura(D.Modal):
    """Lee la carpeta con la configuración actual y muestra cómo se leyó cada archivo. Devuelve el id de la fuente
    a arreglar (al pulsar «Arreglar ›») o None."""

    def __init__(self, duena, app, lectura=None, desde_vista_previa=False):
        super().__init__(duena, "Probar lectura de la carpeta", ancho=1060)
        self.app, self.lectura, self.desde_vista_previa = app, lectura, desde_vista_previa
        self.solo_problemas = False
        self.carpeta, self.desde, self.hasta = contexto_de_lectura(app)
        if lectura is not None:
            self.carpeta, self.desde, self.hasta = lectura.carpeta, lectura.anio_inicio, lectura.anio_fin
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        if self.lectura is None or self.lectura.anio_fin < self.lectura.anio_inicio:
            self._leer()
        self.pintar()

    def _leer(self):
        if not self.carpeta:
            self.lectura = None
            return
        if self.hasta < self.desde:                         # sin vigencia: la matriz y el año en curso
            from datetime import date
            self.desde = self.hasta = date.today().year
        config, carpeta, desde, hasta = self.app.config, Path(self.carpeta), self.desde, self.hasta
        duena = self if self.winfo_viewable() else self.master
        self.lectura = D.en_espera(duena, lambda: leer_carpeta(carpeta, config, desde, hasta))

    def pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Probar lectura de la carpeta", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "lectura").pack(side="left", padx=10)
        T.chip(cab, "Solo vista previa", "gris").pack(side="right")
        chips = tk.Frame(c, bg=T.BLANCO)
        chips.pack(fill="x", pady=(10, 10))
        for texto in (f"Vigencia: {vigencia(self.desde, self.hasta)}", f"Carpeta: {self.carpeta or '—'}"):
            tk.Label(chips, text=texto, font=T.F["pequena_b"], bg=T.FONDO, padx=12, pady=4).pack(side="left", padx=(0, 8))
        T.Franja(c, "info", "Prueba cómo lee el programa cada archivo con lo que hay en Fuentes de datos. No crea "
                 "archivos ni cambia tu configuración.").pack(fill="x", pady=(0, 12))
        if not self.lectura:
            tk.Label(c, text="Elige la carpeta en la ventana principal para probar la lectura.", font=T.F["cuerpo"],
                     bg=T.BLANCO, fg=T.GRIS, pady=20).pack()
            self._pie(c)
            return
        filas = A.filas_prueba(self.app.config, self.lectura)
        cuenta = A.contar_prueba(filas)
        problemas = [f for f in filas if f.con_problema]
        barra = tk.Frame(c, bg=T.BLANCO)
        barra.pack(fill="x", pady=(0, 10))
        for estado, texto, tipo in ((A.LISTO, "listo|listos", "ok"), (POR_CONFIRMAR, "por confirmar", "aviso"),
                                    (SIN_IDENTIFICAR, "sin identificar", "error"),
                                    (A.SIN_ENCABEZADOS, "sin encabezados", "error"),
                                    (A.NO_SE_PUDO_LEER, "no se pudo leer|no se pudieron leer", "error"),
                                    (A.NO_SE_ENCONTRO, "no se encontró|no se encontraron", "error")):
            n = cuenta[estado]
            if n:
                uno, *varios = texto.split("|")
                T.chip(barra, f"{n} {uno if n == 1 or not varios else varios[0]}", tipo).pack(side="left", padx=(0, 8))
        selector = tk.Frame(barra, bg=T.LINEA, padx=1, pady=1)
        selector.pack(side="right")
        for valor, texto in ((False, f"Todos ({len(filas)})"), (True, f"Con problemas ({len(problemas)})")):
            activo = self.solo_problemas == valor
            b = tk.Label(selector, text=texto, font=T.F["pequena_b"], padx=16, pady=6, cursor="hand2",
                         bg=T.VERDE_CTA if activo else T.BLANCO, fg=T.BLANCO if activo else T.GRIS_OSC)
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, v=valor: (setattr(self, "solo_problemas", v), self.pintar()))
        visibles = problemas if self.solo_problemas else filas
        caja = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        caja.pack(fill="x")
        anchos = (260, 210, 110, 100, 190)
        cab = tk.Frame(caja, bg=T.GRIS_OSC, padx=14, pady=9)
        cab.pack(fill="x")
        for j, (texto, w) in enumerate(zip(("Archivo", "Se leyó como", "Encabezados", "Columnas", "Estado"), anchos)):
            cab.grid_columnconfigure(j, minsize=w)
            tk.Label(cab, text=texto, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO, anchor="w").grid(row=0, column=j,
                                                                                                          sticky="w")
        lista = T.desplazable(caja, min(420, max(60, 42 * len(visibles))))
        lista.pack(fill="x")
        if not visibles:
            tk.Label(lista.interior, text="No hay archivos con problemas.", font=T.F["cuerpo"], bg=T.BLANCO,
                     fg=T.GRIS, pady=14).pack()
        for i, f in enumerate(visibles):
            fondo = T.BLANCO if i % 2 == 0 else T.FONDO
            x = tk.Frame(lista.interior, bg=fondo, padx=14, pady=8)
            x.pack(fill="x")
            for j, w in enumerate(anchos):
                x.grid_columnconfigure(j, minsize=w)
            x.grid_columnconfigure(5, weight=1)
            valores = (f.archivo, f.se_leyo_como or "—", f"fila {f.fila}" if f.fila else "—",
                       f"{f.exactas} de {f.total}" if f.total is not None else "—")
            for j, v in enumerate(valores):
                tk.Label(x, text=v, font=T.F["cuerpo_b"] if j == 0 else T.F["cuerpo"], bg=fondo, anchor="w",
                         justify="left", wraplength=anchos[j] - 12).grid(row=0, column=j, sticky="w")
            simbolo, color = ESTADO_PRUEBA[f.estado]
            est = tk.Frame(x, bg=fondo)
            est.grid(row=0, column=4, sticky="w")
            if simbolo == "aviso":
                T.icono(est, "aviso", 18, bg=fondo).pack(side="left")
            else:
                T.marca(est, simbolo, bg=fondo, d=18).pack(side="left")
            tk.Label(est, text=f.texto_estado, font=T.F["pequena_b"], bg=fondo, fg=color).pack(side="left", padx=(6, 0))
            if f.se_puede_arreglar:
                T.Enlace(x, "Arreglar ›", lambda fid=f.fuente: self.cerrar(fid), fuente="pequena_b").grid(row=0, column=5,
                                                                                                        sticky="e")
        tk.Label(c, text=f"Mostrando {len(visibles)} de {len(filas)} · «Arreglar» abre la fuente para confirmar o elegir "
                         "la columna. Lo que falta se agrega a la carpeta.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS, anchor="w").pack(fill="x", pady=(8, 0))
        self._pie(c)

    def _pie(self, c):
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        tk.Frame(pie, bg=T.LINEA, height=1).pack(fill="x", pady=(0, 14))
        T.Boton(pie, "Cerrar", lambda: self.cerrar(None), tipo="secundario", ancho=140).pack(side="left")
        if self.carpeta:
            T.Boton(pie, "Volver a leer", lambda: (self._leer(), self.pintar()), tipo="secundario",
                    ancho=170).pack(side="left", padx=12)
        if not self.desde_vista_previa:
            tk.Label(pie, text="Para ver cómo queda el cuadro, usa Previsualizar cuadro en la ventana principal.",
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS).pack(side="right")
