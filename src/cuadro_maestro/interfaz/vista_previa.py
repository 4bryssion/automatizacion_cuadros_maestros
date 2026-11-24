"""Previsualizar cuadro (mockups 20 y 42): lee y cruza sin crear ningún archivo ni cambiar la configuración."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from ..cruce import cruzar, texto_resultados
from ..cruce.modelos import EXCEL, INFORMATIVO, PROGRAMA
from ..lectura import leer_carpeta
from ..lectura.modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR
from ..revision import guardar_equivalencia_institucion, instituciones_de_la_matriz
from . import dialogos as D
from . import tema as T
from .modelo import vigencia
from .sistema import abrir

AVISOS_VISIBLES, FILAS_VISIBLES = 3, 4
COLOR_GRUPO = {EXCEL: T.MAGENTA, PROGRAMA: T.NARANJA, INFORMATIVO: "#9A9A9A"}


def leer_y_cruzar(raiz, carpeta, config, programa_id, desde, hasta):
    """Lee y cruza en otro hilo mostrando una ventana de espera (la matriz real tarda uno o dos segundos)."""
    def trabajo():
        lectura = leer_carpeta(Path(carpeta), config, desde, hasta)
        return lectura, cruzar(lectura, config, programa_id)
    return D.en_espera(raiz, trabajo)


class VistaPrevia(D.Modal):
    def __init__(self, app, carpeta, programa_id, desde, hasta):
        super().__init__(app.raiz, "Previsualizar cuadro", ancho=980)
        self.app, self.carpeta, self.programa_id, self.desde, self.hasta = app, carpeta, programa_id, desde, hasta
        self.contenido = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.contenido.pack(fill="both", expand=True)
        self.leer(primera=True)

    def leer(self, primera=False):
        lectura, resultado = leer_y_cruzar(self.app.raiz, self.carpeta, self.app.config, self.programa_id,
                                           self.desde, self.hasta)
        self.lectura, self.r = lectura, resultado
        self._pintar()
        if not primera:
            self.update_idletasks()

    def _pintar(self):
        c = self.contenido
        for w in c.winfo_children():
            w.destroy()
        r, lectura = self.r, self.lectura
        fila = tk.Frame(c, bg=T.BLANCO)
        fila.pack(fill="x")
        tk.Label(fila, text="Previsualizar cuadro", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(fila, "vista_previa").pack(side="left", padx=10)
        tk.Label(fila, text="Solo vista previa", font=T.F["pequena_b"], bg=T.FONDO, padx=12, pady=4).pack(side="right")
        chips = tk.Frame(c, bg=T.BLANCO)
        chips.pack(fill="x", pady=(10, 10))
        for texto in (f"Programa: {r.programa['nombre']}", f"Vigencia: {vigencia(self.desde, self.hasta)}",
                      f"Carpeta: {self.carpeta}"):
            tk.Label(chips, text=texto, font=T.F["pequena_b"], bg=T.FONDO, padx=12, pady=4).pack(side="left", padx=(0, 8))
        T.Franja(c, "info", "Es solo una prueba: lee tus archivos y muestra cómo quedaría el cuadro. No crea ningún "
                 "archivo ni cambia tu configuración.").pack(fill="x", pady=(0, 12))
        if lectura.errores:
            T.Franja(c, "error", f"{len(lectura.errores)} archivo(s) existen pero no se pueden leer (en uso, con "
                     "contraseña o dañados). Al generar, la generación se detendría.").pack(fill="x", pady=(0, 12))
        if r.sin_convenios:
            self._sin_convenios(c)
        else:
            self._cifras(c)
            self._lectura(c)
            self._avisos(c)
            self._tabla(c)
        pie = tk.Frame(c, bg=T.BLANCO)
        pie.pack(fill="x", pady=(16, 0))
        T.Boton(pie, "Cerrar", lambda: self.cerrar(None), tipo="secundario", ancho=130).pack(side="left")
        T.Boton(pie, "Volver a leer los archivos", lambda: self.leer(), tipo="secundario", ancho=260).pack(side="left", padx=14)
        tk.Label(pie, text="Después de corregir algo, vuelve a leer.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="left")
        generar = T.Boton(pie, "Generar cuadro maestro", lambda: self.cerrar("generar"), ancho=270)
        generar.pack(side="right")
        generar.activar(not r.sin_convenios)

    def _cifras(self, c):
        r = self.r
        por_anio = [e for e in self.lectura.esperados if e.fuente != "matriz"]
        leidos = sum(e.encontrado for e in por_anio)
        total = len(r.avisos)
        fila = tk.Frame(c, bg=T.BLANCO)
        fila.pack(fill="x", pady=(0, 12))
        datos = [(f"{leidos} de {len(por_anio)}", "archivos por año leídos", T.NARANJA if leidos < len(por_anio) else T.VERDE_CTA,
                  f"Falta {len(por_anio) - leidos}" if leidos < len(por_anio) else ""),
                 (str(r.convenios_en_cuadro), "convenios en el cuadro", T.VERDE_CTA, ""),
                 (str(r.movilidades_contadas + r.actividades_contadas), "movilidades y actividades", T.VERDE_CTA, ""),
                 (str(total), "avisos para revisar", T.MAGENTA if total else T.VERDE_CTA, "Ver abajo" if total else "")]
        for i, (num, etiqueta, color, nota) in enumerate(datos):
            borde = tk.Frame(fila, bg=T.LINEA, padx=1, pady=1)
            borde.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
            fila.grid_columnconfigure(i, weight=1, uniform="c")
            d = tk.Frame(borde, bg=T.BLANCO)
            d.pack(fill="both", expand=True)
            tk.Frame(d, bg=color, width=4).pack(side="left", fill="y")
            x = tk.Frame(d, bg=T.BLANCO, padx=14, pady=8)
            x.pack(side="left", fill="both", expand=True)
            tk.Label(x, text=nota or " ", font=T.F["pequena_b"], bg=T.BLANCO, fg=color, anchor="e").pack(fill="x")
            tk.Label(x, text=num, font=T.F["cifra"], bg=T.BLANCO, anchor="w").pack(fill="x")
            tk.Label(x, text=etiqueta, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")

    def _lectura(self, c):
        estados = [a.estado for a in self.lectura.archivos]
        faltan = sum(1 for e in self.lectura.esperados if not e.encontrado)
        caja = tk.Frame(c, bg=T.FONDO, padx=16, pady=10)
        caja.pack(fill="x", pady=(0, 12))
        tk.Label(caja, text="Lectura de archivos", font=T.F["cuerpo_b"], bg=T.FONDO).pack(side="left", padx=(0, 12))
        for n, texto, fondo, fg in ((estados.count(EXACTA), "listos", "#E3EED2", T.OK_TXT),
                                    (estados.count(POR_CONFIRMAR), "por confirmar", T.AVISO_BG, T.AVISO_TXT),
                                    (estados.count(SIN_IDENTIFICAR), "sin identificar", T.ROSA_SUAVE, T.MAGENTA),
                                    (faltan, "no se encontró" if faltan == 1 else "no se encontraron", T.ROSA_SUAVE, T.MAGENTA)):
            if n:
                tk.Label(caja, text=f"{n} {texto}", font=T.F["pequena_b"], bg=fondo, fg=fg, padx=10,
                         pady=3).pack(side="left", padx=(0, 6))
        T.Enlace(caja, "Ver cómo se leyó cada archivo ›", self.ver_lectura, fuente="pequena_b").pack(side="right")

    def ver_lectura(self):
        """Mockup 27: la prueba de lectura encima de la vista previa, con lo que ya se leyó."""
        from .fuentes import ProbarLectura
        arreglar = ProbarLectura(self, self.app, self.lectura, desde_vista_previa=True).mostrar()
        if arreglar:
            self.abrir_fuentes(arreglar)

    def abrir_fuentes(self, fuente_id=None, dato=None):
        import json
        antes = json.dumps(self.app.config, sort_keys=True, default=str)
        self.app.abrir_modal("fuentes", self, fuente_id=fuente_id, dato=dato)
        if json.dumps(self.app.config, sort_keys=True, default=str) != antes:
            self.leer()                       # se cambió cómo se leen los archivos: la vista previa se actualiza

    def _avisos(self, c):
        avisos = self.r.avisos
        if not avisos:
            T.Franja(c, "info", "No hay avisos: todos los registros se cruzaron con su convenio.").pack(fill="x", pady=(0, 12))
            return
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Avisos de la vista previa", font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
        tk.Label(cab, text=f"Mostrando {min(AVISOS_VISIBLES, len(avisos))} de {len(avisos)}", font=T.F["pequena"],
                 bg=T.BLANCO, fg=T.GRIS).pack(side="right")
        caja = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        caja.pack(fill="x", pady=(8, 4))
        for i, a in enumerate(avisos[:AVISOS_VISIBLES]):
            fondo = T.BLANCO if i % 2 == 0 else T.FONDO
            f = tk.Frame(caja, bg=fondo, padx=14, pady=8)
            f.pack(fill="x")
            T.punto(f, COLOR_GRUPO[a.grupo], 12).pack(side="left", padx=(0, 12))
            tk.Label(f, text=f"{a.titulo}  ·  {a.donde}", font=T.F["pequena"], bg=fondo, anchor="w", justify="left",
                     wraplength=self.ancho - 380).pack(side="left", fill="x", expand=True)
            b = self._accion(f, a)
            if b:
                b.pack(side="right")
        if len(avisos) > AVISOS_VISIBLES:
            tk.Label(c, text=f"y {len(avisos) - AVISOS_VISIBLES} avisos más. Resuelve estos aquí o ve todos en Ver "
                             "revisión, después de generar.", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS,
                     anchor="w").pack(fill="x", pady=(0, 10))

    def _accion(self, padre, a):
        """El mismo botón de acción que el aviso tiene en Ver revisión (decisión 2 de flujo)."""
        crear = lambda texto, fn: T.Boton(padre, texto, fn, tipo="secundario", fuente="boton_peq",  # noqa: E731
                                          ancho=T.F["boton_peq"].measure(texto) + 44, alto=34)
        if "abrir_archivo" in a.acciones and a.ruta:
            return crear(T.texto_abrir(a.ruta), lambda: abrir(a.ruta))
        if "elegir_institucion" in a.acciones:
            return crear("Elegir institución…", lambda: self._elegir(a))
        if "abrir_carpeta" in a.acciones:
            return crear("Abrir carpeta", lambda: abrir(a.ruta.parent if a.ruta else Path(self.carpeta)))
        if "abrir_fuentes" in a.acciones and "confirmar_sugerencia" not in a.acciones:
            return crear("Abrir Fuentes de datos", lambda: self.abrir_fuentes(a.detalle.get("fuente"),
                                                                              a.detalle.get("dato")))
        if "confirmar_sugerencia" in a.acciones:
            from ..revision import confirmar_sugerencia
            return crear("Confirmar sugerencia", lambda: (confirmar_sugerencia(self.app.config, a),
                                                         self.app.guardar_config(), self.leer()))
        return None

    def _elegir(self, a):
        from .revision import ElegirInstitucion
        instituciones = instituciones_de_la_matriz(self.carpeta, self.app.config)
        eleccion = ElegirInstitucion(self, a, instituciones).mostrar()
        if eleccion:
            guardar_equivalencia_institucion(self.app.config, a.detalle["como_aparece"], eleccion)
            self.app.guardar_config()
            self.leer()

    def _tabla(self, c):
        filas = self.r.filas
        cab = tk.Frame(c, bg=T.BLANCO)
        cab.pack(fill="x", pady=(6, 8))
        tk.Label(cab, text="Así quedaría el cuadro", font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
        tk.Label(cab, text=f"Mostrando {min(FILAS_VISIBLES, len(filas))} de {len(filas)}", font=T.F["pequena"],
                 bg=T.BLANCO, fg=T.GRIS).pack(side="right")
        t = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        t.pack(fill="x")
        dentro = tk.Frame(t, bg=T.BLANCO)
        dentro.pack(fill="both")
        r5 = self.app.config["reglas"]["r5_activo"]
        for j, (h, peso) in enumerate((("No.", 0), ("Institución", 3), ("Resultados concretos", 3), ("Vigencia", 1),
                                       ("Activo", 1))):
            tk.Label(dentro, text=h, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO, anchor="w", padx=12,
                     pady=8).grid(row=0, column=j, sticky="ew")
            dentro.grid_columnconfigure(j, weight=peso, uniform=None if j == 0 else f"u{peso}")
        envoltura = (self.ancho - 120) * 3 // 11
        for i, f in enumerate(filas[:FILAS_VISIBLES], start=1):
            fondo = T.BLANCO if i % 2 else T.FONDO
            activo = f.convenio.activo
            valores = (str(f.numero), f.convenio.institucion, texto_resultados(f, self.app.config["tipos_persona"]),
                       str(f.convenio.vigencia_anios or ""))
            for j, v in enumerate(valores):
                tk.Label(dentro, text=v, font=T.F["pequena_b"] if j == 1 else T.F["pequena"], bg=fondo,
                         fg=T.GRIS if v == "Sin evidencia" else T.NEGRO, anchor="w", justify="left", padx=12, pady=8,
                         wraplength=envoltura if j in (1, 2) else 0).grid(row=i, column=j, sticky="nsew")
            celda = tk.Frame(dentro, bg=fondo, padx=12)
            celda.grid(row=i, column=4, sticky="nsew")
            tk.Label(celda, text=r5["etiqueta_activo"] if activo else r5["etiqueta_no_activo"], font=T.F["pequena_b"],
                     bg=T.OK_BG if activo else "#EDEDED", fg=T.OK_TXT if activo else T.GRIS_OSC, padx=10,
                     pady=3).pack(anchor="w", pady=8)

    def _sin_convenios(self, c):
        """Mockup 42: el programa no tiene convenios; Generar queda bloqueado."""
        r = self.r
        borde = tk.Frame(c, bg=T.MAGENTA, padx=1, pady=1)
        borde.pack(fill="x", pady=(4, 0))
        d = tk.Frame(borde, bg=T.BLANCO, padx=24, pady=20)
        d.pack(fill="both")
        T.icono(d, "error", 44).pack(anchor="w")
        if r.convenios_del_programa:
            titulo = f"Ningún convenio de {r.programa['nombre']} entra al cuadro"
            texto = (f"{r.convenios_del_programa} convenios dicen APLICA, pero ninguno queda en el cuadro: los vencidos "
                     "sin resultados no entran y los que no tienen fechas válidas aparecen como avisos.")
        else:
            matriz = self.lectura.matriz
            titulo = f"Ningún convenio aplica a {r.programa['nombre']}"
            texto = (f"La matriz se leyó bien ({len(matriz.registros) if matriz else 0} filas), pero ninguna dice APLICA "
                     f"en la columna «{r.programa['columna_matriz']}».")
        tk.Label(d, text=titulo, font=T.F["seccion"], bg=T.BLANCO, anchor="w").pack(fill="x", pady=(10, 4))
        tk.Label(d, text=texto, font=T.F["cuerpo"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=self.ancho - 120).pack(fill="x")
        tk.Label(d, text="Revisa que la columna diga APLICA para este programa, o que su nombre en la matriz esté bien "
                         "escrito en Programas. Mientras tanto no se puede generar el cuadro.", font=T.F["cuerpo"],
                 bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left", wraplength=self.ancho - 120).pack(fill="x", pady=(8, 0))
        acciones = tk.Frame(d, bg=T.BLANCO)
        acciones.pack(fill="x", pady=(14, 0))
        if self.lectura.matriz:
            T.Boton(acciones, T.texto_abrir(self.lectura.matriz.ruta), lambda: abrir(self.lectura.matriz.ruta),
                    tipo="secundario", fuente="boton_peq",
                    ancho=T.F["boton_peq"].measure(T.texto_abrir(self.lectura.matriz.ruta)) + 44,
                    alto=38).pack(side="left", padx=(0, 10))
        T.Boton(acciones, "Abrir Programas", lambda: self.app.abrir_modal("programas", self), tipo="secundario",
                fuente="boton_peq", ancho=180, alto=38).pack(side="left")
