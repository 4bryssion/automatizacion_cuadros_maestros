"""Exportar e importar configuración (mockup 23)."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog

from ..configuracion import intercambio as X
from . import dialogos as D
from . import tema as T
from .modelo import cuando


def carpeta_inicial() -> Path:
    for p in (Path.home() / "Documents", Path.home() / "Documentos", Path.home()):
        if p.is_dir():
            return p
    return Path.cwd()


class ModalIntercambio(D.Modal):
    def __init__(self, app, duena=None):
        super().__init__(duena or app.raiz, "Exportar e importar configuración", ancho=1060)
        self.app = app
        self.carpeta = carpeta_inicial()
        self.archivo, self.otro, self.error_archivo = None, None, None
        self.modo = tk.StringVar(value=X.COMBINAR)
        self.v_nombre = tk.StringVar(value=X.nombre_sugerido())
        self.mensaje = None                 # (tipo, texto) tras exportar o importar
        cab = tk.Frame(self.cuerpo, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Exportar e importar configuración", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(cab, "exportar").pack(side="left", padx=10)
        tk.Label(self.cuerpo, text="Lleva tu configuración a otro equipo o guarda una copia aparte. El archivo no "
                                   "contiene datos de personas ni tus Excel.", font=T.F["cuerpo"], bg=T.BLANCO,
                 anchor="w").pack(fill="x", pady=(8, 14))
        self.columnas = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.columnas.pack(fill="both", expand=True)
        pie = self.botones()
        tk.Label(pie, text="Los cambios importados se aplican al instante.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="left")
        T.Boton(pie, "Listo", lambda: self.cerrar(True), ancho=160).pack(side="right")
        self.pintar()

    def _caja(self, col):
        d = T.Caja(self.columnas, fondo=T.BLANCO, borde=T.LINEA, radio=T.RADIO_GRANDE + 4, padx=22, pady=18)
        d.grid(row=0, column=col, sticky="nsew", padx=(0, 10) if col == 0 else (10, 0))
        self.columnas.grid_columnconfigure(col, weight=1, uniform="c")
        return d

    def pintar(self):
        for w in self.columnas.winfo_children():
            w.destroy()
        self.columnas.grid_rowconfigure(0, weight=1)
        self._exportar(self._caja(0))
        self._importar(self._caja(1))

    # exportar
    def _exportar(self, d):
        cab = tk.Frame(d, bg=T.BLANCO)
        cab.pack(fill="x")
        tk.Label(cab, text="Exportar", font=T.F["seccion"], bg=T.BLANCO).pack(side="left")
        T.chip(cab, "Esta configuración", "ok").pack(side="right")
        tk.Label(d, text="Se guarda en un solo archivo:", font=T.F["cuerpo"], bg=T.BLANCO, anchor="w").pack(fill="x",
                                                                                                         pady=(10, 4))
        for nombre, n in X.contar(self.app.config):
            f = tk.Frame(d, bg=T.BLANCO)
            f.pack(fill="x", pady=2)
            T.marca(f, "ok", d=18).pack(side="left")
            tk.Label(f, text=nombre, font=T.F["cuerpo"], bg=T.BLANCO).pack(side="left", padx=10)
            tk.Label(f, text=str(n), font=T.F["cuerpo_b"], bg=T.BLANCO).pack(side="right")
        tk.Label(d, text="Nombre del archivo", font=T.F["pequena_b"], bg=T.BLANCO, anchor="w").pack(fill="x",
                                                                                                    pady=(14, 4))
        T.Campo(d, self.v_nombre).pack(fill="x")
        tk.Label(d, text=f"Carpeta: {self.carpeta}", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w",
                 justify="left", wraplength=440).pack(fill="x", pady=(6, 0))
        caja = T.Caja(d, fondo=T.FONDO, borde=T.LINEA, radio=T.RADIO + 2, padx=14, pady=10)
        caja.pack(fill="x", pady=(12, 0))
        T.icono(caja, "gris", 20, bg=T.FONDO).pack(side="left", anchor="n")
        tx = tk.Frame(caja, bg=T.FONDO)
        tx.pack(side="left", fill="x", padx=10)
        tk.Label(tx, text="No incluye", font=T.F["cuerpo_b"], bg=T.FONDO, anchor="w").pack(fill="x")
        tk.Label(tx, text="Tus archivos Excel, los datos de personas ni los cuadros ya generados.", font=T.F["pequena"],
                 bg=T.FONDO, anchor="w", justify="left", wraplength=380).pack(fill="x")
        if self.mensaje and self.mensaje[0] == "exportado":
            T.Franja(d, "info", self.mensaje[1]).pack(fill="x", pady=(12, 0))
        pie = tk.Frame(d, bg=T.BLANCO)
        pie.pack(fill="x", side="bottom", pady=(14, 0))
        T.Boton(pie, "Elegir carpeta…", lambda: self.elegir_carpeta(), tipo="secundario", ancho=190).pack(side="left")
        T.Boton(pie, "Exportar", lambda: self.exportar(), ancho=160).pack(side="right")

    def elegir_carpeta(self, ruta=None):
        ruta = ruta or filedialog.askdirectory(parent=self, initialdir=str(self.carpeta),
                                               title="Carpeta donde se guarda la configuración")
        if ruta:
            self.carpeta = Path(ruta)
            self.pintar()

    def exportar(self):
        try:
            ruta = X.exportar(self.app.almacen.actual, self.carpeta, self.v_nombre.get())
        except (OSError, ValueError) as e:
            self.mensaje = None
            D.aviso(self, "No se pudo exportar", "error", f"No se pudo guardar el archivo: {e}",
                    [("Entendido", "ok", "primario")])
            return None
        self.mensaje = ("exportado", f"Se guardó «{ruta.name}» en {ruta.parent}.")
        self.pintar()
        return ruta

    # importar
    def _importar(self, d):
        tk.Label(d, text="Importar", font=T.F["seccion"], bg=T.BLANCO, anchor="w").pack(fill="x")
        fila = tk.Frame(d, bg=T.BLANCO)
        fila.pack(fill="x", pady=(10, 6))
        T.Boton(fila, "Elegir archivo…", lambda: self.elegir_archivo(), tipo="secundario", ancho=190).pack(side="left")
        if self.otro:
            info = tk.Frame(fila, bg=T.BLANCO)
            info.pack(side="left", padx=14)
            tk.Label(info, text="Archivo elegido", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
            guardado = datetime.fromisoformat(self.otro["guardado_en"]).astimezone().replace(tzinfo=None)
            tk.Label(info, text=f"Guardado {cuando(guardado)} · versión {self.otro.get('version_programa', '—')}",
                     font=T.F["pequena_b"], bg=T.BLANCO, anchor="w").pack(fill="x")
            tk.Label(d, text=self.archivo.name, font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(fill="x")
        if self.error_archivo:
            T.Franja(d, "error", self.error_archivo).pack(fill="x", pady=(6, 0))
        if self.mensaje and self.mensaje[0] == "importado":
            T.Franja(d, "info", self.mensaje[1]).pack(fill="x", pady=(6, 0))
        if not self.otro:
            if not self.error_archivo and not self.mensaje:
                tk.Label(d, text="Elige un archivo .json exportado desde este programa (en este u otro equipo) para ver "
                                 "qué cambiaría antes de importarlo.", font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS,
                         anchor="w", justify="left", wraplength=440).pack(fill="x", pady=(10, 0))
            return
        modo = "combinarla" if self.modo.get() == X.COMBINAR else "reemplazarla"
        tk.Label(d, text=f"Qué cambiaría al {modo}", font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(
            fill="x", pady=(12, 6))
        caja = T.tabla(d)
        caja.pack(fill="x")
        anchos = (190, 60, 70, 120)
        cab = T.cabecera(caja, padx=12, pady=7)
        cab.pack(fill="x")
        for j, (t, w) in enumerate(zip(("Elemento", "Hoy", "Después", "Cambio"), anchos)):
            cab.grid_columnconfigure(j, minsize=w)
            tk.Label(cab, text=t, font=T.F["pequena_b"], bg=T.GRIS_OSC, fg=T.BLANCO).grid(row=0, column=j, sticky="w")
        despues = X.preparar(self.app.config, self.otro, self.modo.get())
        filas = X.comparar(self.app.config, despues)
        for i, (nombre, hoy, archivo, cambio) in enumerate(filas):
            fondo = T.BLANCO if i % 2 == 0 else T.FONDO
            f = T.fila(caja, fondo, 12, 6, ultima=i == len(filas) - 1)
            f.pack(fill="x")
            for j, w in enumerate(anchos):
                f.grid_columnconfigure(j, minsize=w)
            for j, v in enumerate((nombre, hoy, archivo)):
                tk.Label(f, text=str(v), font=T.F["pequena"], bg=fondo).grid(row=0, column=j, sticky="w")
            tipo = "gris" if cambio == "Igual" else "aviso" if "distint" in cambio or "−" in cambio else "ok"
            T.chip(f, cambio, tipo).grid(row=0, column=3, sticky="w")
        tk.Label(d, text="Cómo importarla", font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(fill="x", pady=(12, 4))
        for valor, titulo, texto in ((X.COMBINAR, "Combinar (recomendado)", "Conserva lo tuyo y agrega lo que falte. "
                                      "Tus fuentes y reglas no cambian."),
                                     (X.REEMPLAZAR, "Reemplazar todo", "Tu configuración queda igual a la del archivo.")):
            f = tk.Frame(d, bg=T.BLANCO)
            f.pack(fill="x", pady=2)
            T.radio(f, self.modo, valor, titulo, comando=self.pintar, fuente="cuerpo_b").pack(fill="x")
            tk.Label(f, text=texto, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x", padx=(32, 0))
        T.Franja(d, "aviso", "Antes de importar se guarda una copia de la actual (en Copias y almacenamiento).").pack(
            fill="x", pady=(10, 0))
        pie = tk.Frame(d, bg=T.BLANCO)
        pie.pack(fill="x", pady=(14, 0))
        T.Boton(pie, "Importar", lambda: self.importar(), ancho=160).pack(side="right")
        T.Boton(pie, "Cancelar", self.cancelar_importacion, tipo="secundario", ancho=140).pack(side="right", padx=10)

    def elegir_archivo(self, ruta=None):
        ruta = ruta or filedialog.askopenfilename(parent=self, initialdir=str(self.carpeta),
                                                  title="Configuración para importar",
                                                  filetypes=[("Configuración", "*.json"), ("Todos los archivos", "*.*")])
        if not ruta:
            return
        self.archivo, self.mensaje = Path(ruta), None
        try:
            self.otro, self.error_archivo = X.leer(self.archivo), None
        except X.ErrorImportar as e:
            self.otro, self.error_archivo = None, f"{self.archivo.name}: {e}"
        self.pintar()

    def cancelar_importacion(self):
        self.archivo = self.otro = self.error_archivo = None
        self.pintar()

    def importar(self):
        nueva = X.preparar(self.app.config, self.otro, self.modo.get())
        try:
            self.app.almacen.importar(nueva)
        except (OSError, ValueError) as e:
            D.aviso(self, "No se pudo importar", "error", f"Tu configuración no cambió. {e}",
                    [("Entendido", "ok", "primario")])
            return
        self.app.guardar_config(ya_guardada=True)
        modo = "combinó" if self.modo.get() == X.COMBINAR else "reemplazó"
        self.mensaje = ("importado", f"Se {modo} la configuración con «{self.archivo.name}». La anterior quedó en Copias "
                                     "y almacenamiento (Antes de importar).")
        self.archivo = self.otro = None
        self.pintar()
