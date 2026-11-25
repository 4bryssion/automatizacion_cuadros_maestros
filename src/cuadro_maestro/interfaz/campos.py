"""Campos del cuadro maestro (mockup 14): las columnas del cuadro, en orden, y de dónde sale cada dato.

Se ordenan arrastrando el asa; el lápiz abre el editor en la misma fila. Los campos base (Institución, Resultados,
Vigencia y Activo) solo se renombran: el cálculo los necesita. Un campo de la matriz puede usar cualquier columna de
la matriz; si es una columna que el programa todavía no leía, se agrega a la fuente «Matriz de convenios».
"""
from __future__ import annotations

import tkinter as tk

from .. import ajustes as A
from ..lectura import leer_carpeta
from ..lectura.modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR
from . import dialogos as D
from . import graficos as G
from . import tema as T
from .configuracion import con_ayuda, icono_lapiz, icono_papelera

CHIP_FUENTE = {"matriz": ("Matriz", "ok"), "calculado": ("Calculado", "gris"), "vacio": ("Vacío", "blanco")}
ESTADO_COLUMNA = {EXACTA: ("ok", "Exacta", "Encontrada con este nombre en la matriz."),
                  POR_CONFIRMAR: ("aviso", "Por confirmar", "Hay una columna parecida en la matriz: confírmala en "
                                                            "Fuentes de datos."),
                  SIN_IDENTIFICAR: ("error", "Sin identificar", "No está en la matriz que se leyó: el campo saldría "
                                                                "vacío."),
                  A.SIN_LEER: ("gris", "Sin leer", "Elige la carpeta en la ventana principal para comprobar la columna.")}
ANCHOS = (34, 34, 250, 330, 140)


def _handle(padre, bg):
    return tk.Label(padre, image=G.asa(padre, bg), bg=bg, bd=0, cursor="fleur")


class ModalCampos(D.Modal):
    def __init__(self, app, duena=None, matriz=None):
        super().__init__(duena or app.raiz, "Campos del cuadro maestro", ancho=1000)
        self.app = app
        self.editando = None             # índice en edición (-1 = nuevo)
        self.eliminando = None
        self.arrastre = None             # (desde, hasta)
        self.matriz = matriz if matriz is not None else self._leer_matriz(duena or app.raiz)
        cab = tk.Frame(self.cuerpo, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Campos del cuadro maestro", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "campos").pack(side="left", padx=10)
        self.chip = T.chip(cab, "", "ok")
        self.chip.pack(side="right")
        tk.Label(self.cuerpo, text="Son las columnas del cuadro que se genera, en el orden en que aparecen. Cada campo "
                                   "dice de dónde sale su dato. Arrástralos para ordenarlos, edítalos con el lápiz o crea "
                                   "uno nuevo.", font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=self.ancho - 80).pack(fill="x", pady=(8, 10))
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x", pady=(0, 12))
        tk.Label(fila, text="Arrastra", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS).pack(side="left")
        _handle(fila, T.BLANCO).pack(side="left", padx=6)
        tk.Label(fila, text="para cambiar el orden en el cuadro", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="left")
        T.Boton(fila, "+  Crear campo", self.crear, ancho=200).pack(side="right")
        caja = T.tabla(self.cuerpo, pie=True)
        caja.pack(fill="x")
        cabt = T.cabecera(caja)
        cabt.pack(fill="x")
        for j, (texto, w) in enumerate(zip(("", "#", "Nombre en el cuadro", "De dónde sale el dato", "Tipo"), ANCHOS)):
            cabt.grid_columnconfigure(j, minsize=w)
            tk.Label(cabt, text=texto, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO, anchor="w").grid(row=0, column=j,
                                                                                                           sticky="w")
        self.marco = T.desplazable(caja, 470)
        self.marco.pack(fill="x")
        self.lista = self.marco.interior
        pie = self.botones()
        tk.Label(pie, text="Los campos base son los que el programa necesita para calcular. Los demás se pueden quitar "
                           "o agregar. Los cambios se guardan al instante.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS, anchor="w", justify="left", wraplength=self.ancho - 300).pack(side="left")
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=160).pack(side="right")
        self.pintar()

    def _leer_matriz(self, duena):
        from .fuentes import contexto_de_lectura
        carpeta, _, _ = contexto_de_lectura(self.app)
        if not carpeta:
            return None
        config = self.app.config
        try:
            return D.en_espera(duena, lambda: leer_carpeta(carpeta, config, 1, 0)).matriz
        except Exception:   # noqa: BLE001
            return None

    # lista
    def pintar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        campos = self.app.config["campos"]
        self.filas = []
        if self.editando == -1:
            self._editor(-1, None)
        for i, campo in enumerate(campos):
            if self.editando == i:
                self._editor(i, campo)
                continue
            if self.eliminando == i:
                self._confirmar_eliminar(i, campo)
                continue
            destino = self.arrastre and self.arrastre[1] == i and self.arrastre[0] != i
            fondo = T.TINTE_VERDE if destino else (T.BLANCO if i % 2 == 0 else T.FONDO)
            f = tk.Frame(self.lista, bg=fondo, padx=14, pady=8)
            f.pack(fill="x")
            self.filas.append((i, f))
            for j, w in enumerate(ANCHOS):
                f.grid_columnconfigure(j, minsize=w)
            f.grid_columnconfigure(5, weight=1)
            asa = _handle(f, fondo)
            asa.grid(row=0, column=0, sticky="w")
            asa.bind("<ButtonPress-1>", lambda e, k=i: self._empezar(k))
            asa.bind("<B1-Motion>", self._mover)
            asa.bind("<ButtonRelease-1>", self._soltar)
            tk.Label(f, text=str(i + 1), font=T.F["cuerpo"], bg=fondo, fg=T.GRIS).grid(row=0, column=1, sticky="w")
            tk.Label(f, text=campo["nombre"], font=T.F["cuerpo_b"], bg=fondo, anchor="w", justify="left",
                     wraplength=ANCHOS[2] - 14).grid(row=0, column=2, sticky="w")
            de = tk.Frame(f, bg=fondo)
            de.grid(row=0, column=3, sticky="w")
            texto, tipo = CHIP_FUENTE[campo["fuente"]]
            T.Chip(de, texto, tipo, borde=T.GRIS if campo["fuente"] == "vacio" else None).pack(side="left")
            tk.Label(de, text=A.describir_campo(self.app.config, campo), font=T.F["cuerpo"], bg=fondo, anchor="w",
                     justify="left", wraplength=ANCHOS[3] - 110).pack(side="left", padx=(10, 0))
            tk.Label(f, text=A.TIPOS_CAMPO.get(campo["tipo"], campo["tipo"]), font=T.F["cuerpo"], bg=fondo,
                     anchor="w").grid(row=0, column=4, sticky="w")
            acciones = tk.Frame(f, bg=fondo)
            acciones.grid(row=0, column=5, sticky="e")
            lapiz = con_ayuda(icono_lapiz(acciones, fondo), "Editar")
            lapiz.pack(side="left", padx=6)
            lapiz.bind("<Button-1>", lambda e, k=i: self.editar(k))
            tacho = icono_papelera(acciones, fondo, bloqueado=campo.get("base"))
            tacho.pack(side="left", padx=6)
            if campo.get("base"):
                con_ayuda(tacho, "Campo base: no se puede eliminar")
            else:
                con_ayuda(tacho, "Eliminar").bind("<Button-1>", lambda e, k=i: self.pedir_eliminar(k))
        n = len(campos)
        self.chip.configure(text=f"{n} campo{'s' if n != 1 else ''}")

    # arrastrar para ordenar
    def _empezar(self, i):
        if self.editando is not None:
            return
        self.arrastre = (i, i)

    def _mover(self, e):
        if not self.arrastre:
            return
        hasta = self.arrastre[0]
        for i, f in self.filas:
            if f.winfo_rooty() <= e.y_root:
                hasta = i
        if hasta != self.arrastre[1]:
            self.arrastre = (self.arrastre[0], hasta)
            for i, f in self.filas:              # resalta la fila de destino sin repintar (no corta el arrastre)
                fondo = T.TINTE_VERDE if i == hasta and i != self.arrastre[0] else (T.BLANCO if i % 2 == 0 else T.FONDO)
                self._fondo(f, fondo)

    def _fondo(self, w, fondo):
        try:
            if not isinstance(w, tk.Label) or w["bg"] in (T.BLANCO, T.FONDO, T.TINTE_VERDE):
                w.configure(bg=fondo)
        except tk.TclError:
            pass
        for h in w.winfo_children():
            if isinstance(h, (tk.Frame, tk.Canvas, tk.Label)):
                self._fondo(h, fondo)

    def _soltar(self, _=None):
        if not self.arrastre:
            return
        desde, hasta = self.arrastre
        self.arrastre = None
        self.mover(desde, hasta)

    def mover(self, desde, hasta):
        if A.mover_campo(self.app.config, desde, hasta):
            self.app.guardar_config()
        self.pintar()

    # editar
    def crear(self):
        self.editando, self.eliminando = -1, None
        self.pintar()
        self.marco.lienzo.yview_moveto(0)

    def editar(self, i):
        self.editando, self.eliminando = i, None
        self.pintar()

    def pedir_eliminar(self, i):
        self.eliminando, self.editando = i, None
        self.pintar()

    def cancelar(self):
        self.editando = self.eliminando = None
        self.bind("<Return>", lambda e: None)
        self.bind("<Escape>", lambda e: self.al_cerrar())
        self.pintar()

    def _editor(self, i, campo):
        base = bool(campo and campo.get("base"))
        d = T.Caja(self.lista, fondo=T.BLANCO, borde=T.VERDE_CTA, grosor=2, radio=T.RADIO_GRANDE, padx=18, pady=14)
        d.pack(fill="x", padx=8, pady=6)
        tk.Label(d, text=f"Editando: {campo['nombre']}" if campo else "Nuevo campo", font=T.F["cuerpo_b"], bg=T.BLANCO,
                 fg=T.OK_TXT, anchor="w").pack(fill="x", pady=(0, 8))
        g = tk.Frame(d, bg=T.BLANCO)
        g.pack(fill="x")
        g.grid_columnconfigure(0, weight=1, uniform="e")
        g.grid_columnconfigure(1, weight=1, uniform="e")

        def etiqueta(texto, fila, col):
            tk.Label(g, text=texto, font=T.F["pequena_b"], bg=T.BLANCO, anchor="w").grid(
                row=fila, column=col, sticky="w", padx=(0 if col == 0 else 16, 0), pady=(6, 2))

        etiqueta("Nombre en el cuadro", 0, 0)
        v_nombre = tk.StringVar(value=campo["nombre"] if campo else "")
        c_nombre = T.Campo(g, v_nombre)
        c_nombre.grid(row=1, column=0, sticky="ew")
        c_nombre.entrada.focus_set()
        etiqueta("Tipo de dato", 0, 1)
        etiqueta("Fuente del dato", 2, 0)
        etiqueta("Columna del Excel", 2, 1)
        estado = {"fuente": campo["fuente"] if campo else "matriz", "dato": campo.get("dato") if campo else None,
                  "tipo": campo["tipo"] if campo else "texto"}
        nota = tk.Frame(g, bg=T.BLANCO)
        nota.grid(row=4, column=1, sticky="w", padx=(16, 0), pady=(6, 0))
        celda_tipo = tk.Frame(g, bg=T.BLANCO)
        celda_tipo.grid(row=1, column=1, sticky="ew", padx=(16, 0))
        celda_col = tk.Frame(g, bg=T.BLANCO)
        celda_col.grid(row=3, column=1, sticky="ew", padx=(16, 0))
        opciones_col = A.columnas_de_la_matriz(self.app.config, self.matriz)

        def pintar_nota():
            for w in nota.winfo_children():
                w.destroy()
            if estado["fuente"] != "matriz" or not estado["dato"]:
                return
            est = next((e for v, _, e in opciones_col if v == estado["dato"]), A.SIN_LEER)
            if estado["dato"].startswith("enc:"):
                est = EXACTA
            tipo, texto, explicacion = ESTADO_COLUMNA[est]
            T.chip(nota, texto, tipo).pack(side="left")
            tk.Label(nota, text=explicacion, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=300).pack(side="left", padx=8)

        def pintar_dependientes():
            for w in (*celda_tipo.winfo_children(), *celda_col.winfo_children()):
                w.destroy()
            if base:
                T.campo_bloqueado(celda_tipo, A.TIPOS_CAMPO.get(estado["tipo"], estado["tipo"])).pack(fill="x")
                T.campo_bloqueado(celda_col, A.describir_campo(self.app.config, campo)).pack(fill="x")
            elif estado["fuente"] == "calculado":
                tipo = {"numeracion": "numero", "resultados": "texto_calculado", "activo": "opciones"}.get(estado["dato"])
                T.campo_bloqueado(celda_tipo, A.TIPOS_CAMPO.get(tipo, "Según lo que se calcula")).pack(fill="x")
                self.opc_calculo = T.Opciones(celda_col, list(A.DATOS_CALCULADOS.items()), estado["dato"],
                                              lambda v: (estado.update(dato=v), pintar_dependientes()))
                self.opc_calculo.pack(fill="x")
            else:
                tipos = [(k, t) for k, t in A.TIPOS_CAMPO.items() if k != "texto_calculado"]
                self.opc_tipo = T.Opciones(celda_tipo, tipos, estado["tipo"], lambda v: estado.update(tipo=v))
                self.opc_tipo.pack(fill="x")
                if estado["fuente"] == "vacio":
                    T.campo_bloqueado(celda_col, "No se llena: queda para escribir a mano").pack(fill="x")
                else:
                    self.opc_columna = T.Opciones(celda_col, [(v, t) for v, t, _ in opciones_col], estado["dato"],
                                                  lambda v: (estado.update(dato=v), pintar_nota()))
                    self.opc_columna.pack(fill="x")
            pintar_nota()

        if base:
            T.campo_bloqueado(g, "Matriz de convenios" if estado["fuente"] == "matriz" else "Calculado").grid(
                row=3, column=0, sticky="ew")
            tk.Label(g, text="Campo base: se puede renombrar, no eliminar ni cambiar de dónde sale.", font=T.F["pequena"],
                     bg=T.BLANCO, fg=T.GRIS, anchor="w").grid(row=4, column=0, sticky="w", pady=(6, 0))
        else:
            fuentes = [("matriz", "Matriz de convenios"), ("calculado", "Calculado por el programa"),
                       ("vacio", "Vacío (se llena a mano)")]

            def cambiar_fuente(v):
                estado.update(fuente=v, dato=None if v != (campo or {}).get("fuente") else campo.get("dato"))
                pintar_dependientes()
            self.opc_fuente = T.Opciones(g, fuentes, estado["fuente"], cambiar_fuente)
            self.opc_fuente.grid(row=3, column=0, sticky="ew")
            tk.Label(g, text="Movilidad e internacionalización en casa llegan al cuadro a través de «Resultados».",
                     font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=380).grid(row=4, column=0, sticky="w", pady=(6, 0))
        pintar_dependientes()
        error = tk.Label(d, font=T.F["pequena"], bg=T.BLANCO, fg=T.MAGENTA, anchor="w")
        error.pack(fill="x", pady=(6, 0))

        def guardar():
            try:
                A.guardar_campo(self.app.config, i, v_nombre.get(), estado["fuente"], estado["dato"], estado["tipo"])
            except ValueError as err:
                error.configure(text=str(err))
                return
            self.app.guardar_config()
            self.cancelar()
        self.guardar_edicion = guardar
        self.v_nombre_edicion = v_nombre
        pie = tk.Frame(d, bg=T.BLANCO)
        pie.pack(fill="x", pady=(8, 0))
        tk.Label(pie, text="Enter guarda · Esc cancela", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS).pack(side="left")
        T.Boton(pie, "Guardar", guardar, ancho=150, alto=40).pack(side="right")
        T.Boton(pie, "Cancelar", self.cancelar, tipo="secundario", ancho=140, alto=40).pack(side="right", padx=10)
        self.bind("<Return>", lambda e: guardar())
        self.bind("<Escape>", lambda e: self.cancelar())

    def _confirmar_eliminar(self, i, campo):
        d = T.Caja(self.lista, fondo=T.AVISO_BG, borde=T.NARANJA, radio=T.RADIO + 2, padx=14, pady=10)
        d.pack(fill="x", padx=8, pady=6)
        T.icono(d, "aviso", 22, bg=T.AVISO_BG).pack(side="left")
        tx = tk.Frame(d, bg=T.AVISO_BG)
        tx.pack(side="left", fill="x", expand=True, padx=10)
        tk.Label(tx, text=f"¿Eliminar el campo «{campo['nombre']}»?", font=T.F["cuerpo_b"], bg=T.AVISO_BG,
                 anchor="w").pack(fill="x")
        tk.Label(tx, text="Los próximos cuadros no tendrán esta columna. Los cuadros ya generados y tus Excel no se "
                          "tocan.", font=T.F["pequena"], bg=T.AVISO_BG, fg=T.GRIS, anchor="w").pack(fill="x")
        b = tk.Frame(d, bg=T.AVISO_BG)
        b.pack(side="right")
        T.Boton(b, "Cancelar", self.cancelar, tipo="secundario", fuente="boton_peq", ancho=110, alto=34).pack(side="left",
                                                                                                          padx=6)
        T.Boton(b, "Eliminar", lambda: self.confirmar_eliminacion(), tipo="peligro", fuente="boton_peq", ancho=110,
                alto=34).pack(side="left")
        self.confirmar_eliminacion = lambda: (A.eliminar_campo(self.app.config, i), self.app.guardar_config(),
                                              self.cancelar())
