"""Ventana principal (mockups 01, 02, 34, 35, 39, 40)."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk

from .. import __version__
from ..configuracion import AlmacenConfiguracion
from ..estado import AlmacenEstado, Estado
from ..recursos import carpeta_recursos
from . import dialogos as D
from . import flujo
from . import tema as T
from .modelo import ENCONTRADO, cuando, mensaje_faltantes, motivo_para_no_generar, resumir, vigencia
from .sistema import abrir

ANIO_MINIMO = 2015
ANCHO_APILADO = 760


class VentanaPrincipal(tk.Frame):
    def __init__(self, raiz: tk.Tk, almacen: AlmacenConfiguracion, config: dict, estados: AlmacenEstado,
                 estado: Estado):
        super().__init__(raiz, bg=T.BLANCO)
        self.raiz, self.almacen, self.config, self.estados, self.estado = raiz, almacen, config, estados, estado
        self.resumen = None
        self.uso_vista_previa = False
        self.al_abrir_revision = None            # lo pone la aplicación (cambia a la pantalla de revisión)
        self.app = None
        self._revirtiendo = False
        self.v_carpeta = tk.StringVar(value=estado.carpeta or "")
        anio = datetime.now().year
        self.anios = [str(a) for a in range(ANIO_MINIMO, anio + 2)]
        self.v_desde = tk.StringVar(value=str(estado.anio_inicio or anio - 4))
        self.v_hasta = tk.StringVar(value=str(estado.anio_fin or anio - 1))
        self.programas = {p["nombre"]: p["id"] for p in config["programas"]}
        nombre = next((n for n, i in self.programas.items() if i == estado.programa_id), "")
        self.v_programa = tk.StringVar(value=nombre)
        self._construir()
        for v in (self.v_programa, self.v_desde, self.v_hasta):
            v.trace_add("write", lambda *a: self.actualizar())
        self.raiz.bind("<FocusIn>", self._al_volver, add="+")
        self.actualizar()

    # ------------------------------------------------------------ construcción
    def _construir(self):
        self.pack(fill="both", expand=True)
        cab = tk.Frame(self, bg=T.BLANCO, padx=28, pady=16)
        cab.pack(fill="x")
        self._logo(cab).pack(side="left")
        der = tk.Frame(cab, bg=T.BLANCO)
        der.pack(side="right")
        tk.Label(der, text="Cuadro maestro internacional", font=T.F["app_titulo"], bg=T.BLANCO,
                 fg=T.GRIS_OSC).pack(anchor="e")
        tk.Label(der, text="Oficina de Relaciones Internacionales", font=T.F["app_sub"], bg=T.BLANCO,
                 fg=T.GRIS).pack(anchor="e")
        tk.Frame(self, bg=T.VERDE, height=4).pack(fill="x")

        pie = tk.Frame(self, bg=T.FONDO, padx=28, pady=10)
        pie.pack(side="bottom", fill="x")
        tk.Frame(self, bg=T.LINEA, height=1).pack(side="bottom", fill="x")
        tk.Label(pie, text="Fundación Universitaria del Área Andina", font=T.F["barra"], bg=T.FONDO,
                 fg=T.GRIS).pack(side="left")
        tk.Label(pie, text=f"Versión {__version__}", font=T.F["barra"], bg=T.FONDO, fg=T.GRIS).pack(side="right")

        # cuerpo con desplazamiento (pantallas pequeñas)
        marco = tk.Frame(self, bg=T.BLANCO)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, bg=T.BLANCO, highlightthickness=0)
        barra = tk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.cuerpo = tk.Frame(self.lienzo, bg=T.BLANCO, padx=28, pady=20)
        vid = self.lienzo.create_window(0, 0, window=self.cuerpo, anchor="nw")
        self.cuerpo.bind("<Configure>", lambda e: self._ajustar_desplazamiento(barra))
        self.lienzo.bind("<Configure>", lambda e: (self.lienzo.itemconfigure(vid, width=e.width), self._reacomodar(e.width)))
        self.lienzo.configure(yscrollcommand=barra.set)
        self.lienzo.pack(side="left", fill="both", expand=True)
        self._barra = barra
        self.lienzo.bind_all("<MouseWheel>", self._rueda, add="+")
        self.lienzo.bind_all("<Button-4>", lambda e: self.lienzo.yview_scroll(-2, "units"), add="+")
        self.lienzo.bind_all("<Button-5>", lambda e: self.lienzo.yview_scroll(2, "units"), add="+")
        c = self.cuerpo

        # 1. Carpeta
        self._titulo(c, "1. Carpeta con los Excel", "carpeta").pack(fill="x")
        fila = tk.Frame(c, bg=T.BLANCO)
        fila.pack(fill="x", pady=(8, 18))
        self.campo_carpeta = T.Campo(fila, self.v_carpeta, solo_lectura=True)
        self.campo_carpeta.pack(side="left", fill="x", expand=True)
        T.Boton(fila, "Elegir carpeta…", self.elegir_carpeta, tipo="secundario", ancho=190).pack(side="left", padx=(14, 0))

        # 2. Programa y 3. Vigencia
        self.zona_pv = tk.Frame(c, bg=T.BLANCO)
        self.zona_pv.pack(fill="x", pady=(0, 16))
        self.bloque_prog = tk.Frame(self.zona_pv, bg=T.BLANCO)
        self._titulo(self.bloque_prog, "2. Programa", None).pack(fill="x")
        self.cb_programa = ttk.Combobox(self.bloque_prog, textvariable=self.v_programa, values=list(self.programas),
                                        state="readonly", style="CM.TCombobox", font=T.F["cuerpo"], height=16)
        self.cb_programa.pack(fill="x", pady=(8, 0))
        self.bloque_vig = tk.Frame(self.zona_pv, bg=T.BLANCO)
        self._titulo(self.bloque_vig, "3. Vigencia (años completos)", "vigencia").pack(fill="x")
        fv = tk.Frame(self.bloque_vig, bg=T.BLANCO)
        fv.pack(fill="x", pady=(8, 0))
        self.cb_desde, self.cb_hasta = [], []
        for texto, var in (("Desde", self.v_desde), ("Hasta", self.v_hasta)):
            tk.Label(fv, text=texto, font=T.F["cuerpo"], bg=T.BLANCO).pack(side="left", padx=(0 if texto == "Desde" else 16, 10))
            cb = ttk.Combobox(fv, textvariable=var, values=self.anios, state="readonly", width=7,
                              style="CM.TCombobox", font=T.F["cuerpo"])
            cb.pack(side="left", fill="x", expand=True)
            (self.cb_desde if texto == "Desde" else self.cb_hasta).append(cb)
        self.lbl_vig_error = tk.Label(self.bloque_vig, text="", font=T.F["pequena"], bg=T.BLANCO, fg=T.MAGENTA, anchor="w")
        self.lbl_vig_error.pack(fill="x")
        self._acomodo = None
        self._reacomodar(1000)

        # Archivos que se usarán
        cab_arch = tk.Frame(c, bg=T.BLANCO)
        cab_arch.pack(fill="x", pady=(0, 8))
        self._titulo(cab_arch, "Archivos que se usarán", "archivos").pack(side="left")
        self.chip = tk.Label(cab_arch, text="", font=T.F["pequena_b"], padx=14, pady=5)
        self.chip.pack(side="right")
        T.Enlace(cab_arch, "Actualizar", self.actualizar).pack(side="right", padx=(0, 18))

        borde = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        borde.pack(fill="x", pady=(0, 10))
        self.fila_matriz = tk.Frame(borde, bg=T.BLANCO, padx=18, pady=10)
        self.fila_matriz.pack(fill="both")
        self.tabla_borde = tk.Frame(c, bg=T.LINEA, padx=1, pady=1)
        self.tabla_borde.pack(fill="x")
        self.tabla = tk.Frame(self.tabla_borde, bg=T.BLANCO)
        self.tabla.pack(fill="both")
        self.zona_avisos = tk.Frame(c, bg=T.BLANCO)
        self.zona_avisos.pack(fill="x", pady=(12, 0))
        self.zona_ultimo = tk.Frame(c, bg=T.BLANCO)
        self.zona_ultimo.pack(fill="x", pady=(12, 0))

        # Botones
        acciones = tk.Frame(c, bg=T.BLANCO)
        acciones.pack(fill="x", pady=(18, 0))
        self.b_generar = T.Boton(acciones, "Generar cuadro maestro", self.generar, ancho=300, alto=50)
        self.b_generar.pack(side="left")
        self.b_previa = T.Boton(acciones, "Previsualizar cuadro", None, tipo="secundario", ancho=200, alto=50)
        self.b_previa.pack(side="left", padx=(14, 8))
        self.b_previa.activar(False)
        T.Ayuda(acciones, "previsualizar").pack(side="left")
        self.lbl_motivo = tk.Label(c, text="", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w")
        self.lbl_motivo.pack(fill="x", pady=(6, 0))
        abajo = tk.Frame(c, bg=T.BLANCO)
        abajo.pack(fill="x", pady=(10, 0))
        self.b_config = T.Boton(abajo, "Configuración", None, tipo="secundario", ancho=170, alto=44)
        self.b_config.pack(side="left")
        self.b_config.activar(False)
        T.Ayuda(abajo, "config").pack(side="left", padx=8)
        T.Ayuda(abajo, "revision").pack(side="right")
        self.l_revision = T.Enlace(abajo, "Ver revisión", self.abrir_revision)
        self.l_revision.pack(side="right", padx=(0, 8))
        tk.Label(c, text="Previsualizar y Configuración llegan en la próxima versión.",
                 font=T.F["pequena"], bg=T.BLANCO, fg=T.DESACT_TXT, anchor="w").pack(fill="x", pady=(8, 0))

    def _logo(self, padre):
        ruta = carpeta_recursos() / "marca" / "logotipo_verde.png"
        if ruta.is_file():
            try:
                from PIL import Image, ImageTk
                im = Image.open(ruta)
                caja = im.getbbox()                 # el archivo oficial trae mucho margen transparente
                if caja:
                    im = im.crop(caja)
                alto = 52
                im = im.resize((int(im.width * alto / im.height), alto), Image.LANCZOS)
                self._img_logo = ImageTk.PhotoImage(im)
                return tk.Label(padre, image=self._img_logo, bg=T.BLANCO)
            except Exception:   # noqa: BLE001
                pass
        return tk.Label(padre, text="AREANDINA", font=T.F["app_titulo"], bg=T.BLANCO, fg=T.VERDE)

    def _titulo(self, padre, texto, ayuda):
        f = tk.Frame(padre, bg=T.BLANCO)
        tk.Label(f, text=texto, font=T.F["seccion"], bg=T.BLANCO, fg=T.GRIS_OSC).pack(side="left")
        if ayuda:
            T.Ayuda(f, ayuda).pack(side="left", padx=(10, 0))
        return f

    def _reacomodar(self, ancho):
        apilar = ancho < ANCHO_APILADO
        if apilar == self._acomodo:
            return
        self._acomodo = apilar
        for b in (self.bloque_prog, self.bloque_vig):
            b.grid_forget()
        if apilar:
            self.bloque_prog.grid(row=0, column=0, sticky="ew")
            self.bloque_vig.grid(row=1, column=0, sticky="ew", pady=(14, 0))
            self.zona_pv.grid_columnconfigure(0, weight=1, uniform="")
            self.zona_pv.grid_columnconfigure(1, weight=0, uniform="")
        else:
            self.bloque_prog.grid(row=0, column=0, sticky="new", padx=(0, 28))
            self.bloque_vig.grid(row=0, column=1, sticky="new")
            self.zona_pv.grid_columnconfigure(0, weight=1, uniform="pv")
            self.zona_pv.grid_columnconfigure(1, weight=1, uniform="pv")
        if hasattr(self, "tabla"):
            self.after_idle(self.actualizar)        # la tabla y la fila de la matriz cambian con el ancho

    def _ajustar_desplazamiento(self, barra):
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))
        necesita = self.cuerpo.winfo_reqheight() > self.lienzo.winfo_height()
        if necesita and not barra.winfo_ismapped():
            barra.pack(side="right", fill="y")
        elif not necesita and barra.winfo_ismapped():
            barra.pack_forget()
            self.lienzo.yview_moveto(0)

    def _rueda(self, e):
        if self._barra.winfo_ismapped():
            self.lienzo.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def _al_volver(self, evento):
        if evento.widget is self.raiz and self.v_carpeta.get():
            self.actualizar()          # se actualiza al volver a la ventana (decisión 4 de flujo)

    # ------------------------------------------------------------ datos
    def anios_elegidos(self):
        try:
            return int(self.v_desde.get()), int(self.v_hasta.get())
        except ValueError:
            return None, None

    def programa_id(self):
        return self.programas.get(self.v_programa.get())

    def elegir_carpeta(self):
        inicial = self.v_carpeta.get() if Path(self.v_carpeta.get() or ".").is_dir() else str(Path.home())
        carpeta = filedialog.askdirectory(parent=self.raiz, initialdir=inicial, title="Carpeta con los Excel")
        if carpeta:
            self.v_carpeta.set(str(Path(carpeta)))
            self.actualizar()

    def _valores(self):
        return (self.v_carpeta.get(), self.v_programa.get(), self.v_desde.get(), self.v_hasta.get())

    def actualizar(self):
        if not self._confirmar_cambio():
            return
        desde, hasta = self.anios_elegidos()
        carpeta = self.v_carpeta.get()
        invertida = desde is not None and hasta is not None and desde > hasta
        self.lbl_vig_error.configure(text="«Desde» no puede ser mayor que «Hasta»." if invertida else "")
        for cb in self.cb_desde + self.cb_hasta:
            cb.configure(style="Error.CM.TCombobox" if invertida else "CM.TCombobox")
        self.resumen = resumir(carpeta, self.config, desde, hasta) if carpeta and not invertida and desde else None
        self._pintar_matriz()
        self._pintar_tabla(desde, hasta)
        self._pintar_avisos()
        self._pintar_ultimo()
        motivo = motivo_para_no_generar(carpeta, self.programa_id(), desde, hasta, self.resumen)
        self.b_generar.activar(motivo is None)
        self.l_revision.activar(self.estado.ultima is not None)
        self.lbl_motivo.configure(text=motivo or "")
        self._guardar_estado()

    def _confirmar_cambio(self) -> bool:
        """Mockup 38: cambiar carpeta, programa o vigencia con cambios sin incluir pide generar antes."""
        nuevos = self._valores()
        anteriores = getattr(self, "_anteriores", None)
        self._anteriores = nuevos
        u = self.estado.ultima
        if anteriores is None or nuevos == anteriores or not (u and u.cambios_sin_incluir) or self._revirtiendo:
            return True
        r = D.aviso(self.raiz, "Hay cambios sin incluir en el último cuadro", "aviso",
                    f"El cuadro de {u.programa} ({vigencia(u.anio_inicio, u.anio_fin)}) tiene correcciones que todavía no "
                    "se incluyeron. Si cambias la carpeta, el programa o la vigencia ahora, esas correcciones se pierden "
                    "de vista. Genera el cuadro de nuevo primero; después se aplica tu cambio.",
                    [("Generar cuadro de nuevo", "generar", "primario"), ("Cancelar el cambio", "cancelar", "secundario")])
        if r == "generar":
            from .revision import generar_de_nuevo
            estado, g = generar_de_nuevo(self.app)
            if g:
                return True                   # se aplica el cambio y se vuelve a leer la tabla de archivos
        self._revirtiendo = True              # se deshace el cambio sin volver a preguntar
        try:
            for var, valor in zip((self.v_carpeta, self.v_programa, self.v_desde, self.v_hasta), anteriores):
                var.set(valor)
        finally:
            self._revirtiendo = False
        self._anteriores = anteriores
        return False

    def _guardar_estado(self):
        desde, hasta = self.anios_elegidos()
        self.estado.carpeta = self.v_carpeta.get() or None
        self.estado.programa_id = self.programa_id()
        self.estado.anio_inicio, self.estado.anio_fin = desde, hasta
        self.estados.guardar(self.estado)

    # ------------------------------------------------------------ pintar
    def _pintar_matriz(self):
        f = self.fila_matriz
        for w in f.winfo_children():
            w.destroy()
        tk.Label(f, text="Matriz de convenios", font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(side="left", padx=(0, 24))
        r = self.resumen
        if r is None:
            tk.Label(f, text="Elige la carpeta y la vigencia para buscarla.", font=T.F["cuerpo"], bg=T.BLANCO,
                     fg=T.GRIS).pack(side="left", padx=(12, 0))
        elif r.matriz and r.matriz.encontrado:
            T.marca(f, "ok").pack(side="left", padx=(12, 6))
            tk.Label(f, text=r.matriz.ruta.name, font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(side="left")
            if r.matriz_modificada:
                fecha = tk.Label(f, text=f"Modificada {cuando(r.matriz_modificada)}", font=T.F["pequena"],
                                 bg=T.BLANCO, fg=T.GRIS)
                if self._acomodo:      # angosta: la fecha va debajo, para no montarse sobre el nombre
                    fecha.pack(side="bottom", anchor="w", before=f.winfo_children()[0])
                else:
                    fecha.pack(side="right")
        else:
            T.marca(f, "mal").pack(side="left", padx=(12, 6))
            tk.Label(f, text="Falta la matriz de convenios", font=T.F["cuerpo_b"], bg=T.BLANCO,
                     fg=T.MAGENTA).pack(side="left")

    def _pintar_tabla(self, desde, hasta):
        t = self.tabla
        for w in t.winfo_children():
            w.destroy()
        angosta = bool(self._acomodo)
        encabezados = (("Año", "Movilidad", "IC · 1.er sem.", "IC · 2.º sem.") if angosta else
                       ("Año", "Movilidad (anual)", "Int. en casa · 1.er semestre", "Int. en casa · 2.º semestre"))
        for j, h in enumerate(encabezados):
            tk.Label(t, text=h, font=T.F["cuerpo_b"], bg=T.GRIS_OSC, fg=T.BLANCO, anchor="w", padx=18,
                     pady=10).grid(row=0, column=j, sticky="ew")
            t.grid_columnconfigure(j, weight=1 if j else 0, uniform=None if j == 0 else "col", minsize=90 if j == 0 else 0)
        r = self.resumen
        if r is None:
            tk.Label(t, text="Elige la carpeta con los Excel para ver qué archivos hay.", font=T.F["cuerpo"],
                     bg=T.BLANCO, fg=T.GRIS, pady=18).grid(row=1, column=0, columnspan=4)
            self.chip.configure(text="", bg=T.BLANCO)
            return
        for i, (anio, *celdas) in enumerate(r.filas, start=1):
            fondo = T.BLANCO if i % 2 else T.FONDO
            tk.Label(t, text=str(anio), font=T.F["cuerpo"], bg=fondo, anchor="w", padx=18, pady=9).grid(
                row=i, column=0, sticky="nsew")
            for j, celda in enumerate(celdas, start=1):
                cf = tk.Frame(t, bg=fondo, padx=18, pady=7)
                cf.grid(row=i, column=j, sticky="nsew")
                ok = celda.estado == ENCONTRADO
                T.marca(cf, "ok" if ok else "mal", bg=fondo).pack(side="left", padx=(0, 6))
                if angosta:            # identidad.md: en ventana angosta, solo las marcas y el texto de lo que falta
                    if not ok:
                        tk.Label(cf, text="Falta", font=T.F["cuerpo_b"], bg=fondo, fg=T.MAGENTA).pack(side="left")
                    elif celda.aviso:
                        tk.Label(cf, text="!", font=T.F["cuerpo_b"], bg=fondo, fg=T.AVISO_TXT).pack(side="left")
                    continue
                texto = celda.texto + (f" · {celda.aviso}" if celda.aviso else "")
                tk.Label(cf, text=texto, font=T.F["cuerpo"] if ok else T.F["cuerpo_b"], bg=fondo,
                         fg=T.GRIS if ok else T.MAGENTA, anchor="w").pack(side="left")
        completo = r.completo
        self.chip.configure(text=f"{r.encontrados} de {r.esperados} encontrados",
                            bg=T.VERDE_CTA if completo else T.NARANJA, fg=T.BLANCO if completo else T.GRIS_OSC)

    def _pintar_avisos(self):
        z = self.zona_avisos
        for w in z.winfo_children():
            w.destroy()
        r = self.resumen
        carpeta = self.v_carpeta.get()
        if not carpeta or r is None:
            return
        if not r.carpeta_existe:
            T.Franja(z, "error", f"No se encuentra la carpeta «{carpeta}». Puede que el disco o la memoria USB estén "
                     "desconectados, o que la carpeta haya cambiado de nombre.").pack(fill="x")
            return
        if r.sin_archivos:
            T.Franja(z, "error", "En esta carpeta no hay ningún Excel con un nombre que el programa reconozca. "
                     "Los nombres deben llevar «Convenios», «Movilidad» o «Casa» y el año (por ejemplo Movilidad_2021.xlsx, "
                     "IntCasa_2021-1.xlsx). Revisa que sea la carpeta correcta.").pack(fill="x")
            return
        if not (r.matriz and r.matriz.encontrado):
            T.Franja(z, "error", "Falta la Matriz de convenios: sin ella no se puede generar ni previsualizar. Copia a "
                     "esta carpeta el archivo de convenios (un nombre que contenga «Convenios»).").pack(fill="x")
            return
        mensaje = mensaje_faltantes(r.faltan)
        if mensaje:
            T.Franja(z, "aviso", mensaje).pack(fill="x")

    def _pintar_ultimo(self):
        z = self.zona_ultimo
        for w in z.winfo_children():
            w.destroy()
        u = self.estado.ultima
        if not u:
            return
        caja = tk.Frame(z, bg=T.LINEA, padx=1, pady=1)
        caja.pack(fill="x")
        f = tk.Frame(caja, bg=T.FONDO, padx=18, pady=12)
        f.pack(fill="both")
        color = T.NARANJA if u.cambios_sin_incluir else T.VERDE_CTA
        T.punto(f, color, 12).pack(side="left")
        tk.Label(f, text="Último cuadro:", font=T.F["cuerpo_b"], bg=T.FONDO).pack(side="left", padx=(8, 6))
        hora = datetime.fromisoformat(u.hora)
        n = u.total_avisos
        tk.Label(f, text=f"{u.programa} · {vigencia(u.anio_inicio, u.anio_fin)} · {cuando(hora)} · "
                         f"{n} aviso{'s' if n != 1 else ''}", font=T.F["cuerpo"], bg=T.FONDO).pack(side="left")
        T.Enlace(f, "Abrir carpeta", lambda: self._abrir_ultimo(carpeta=True)).pack(side="right")
        T.Enlace(f, "Abrir cuadro", lambda: self._abrir_ultimo(carpeta=False)).pack(side="right", padx=(0, 18))

    def _abrir_ultimo(self, carpeta: bool):
        u = self.estado.ultima
        ruta = Path(u.ruta)
        if abrir(ruta.parent if carpeta else ruta):
            return
        r = D.aviso(self.raiz, "No se encontró el cuadro", "error",
                    f"El archivo «{ruta.name}» ya no está en «{ruta.parent}». Puede que se haya movido, renombrado o "
                    "borrado. La revisión y la configuración no cambian.",
                    [("Generar cuadro de nuevo", "generar", "primario"), ("Abrir carpeta", "carpeta", "secundario"),
                     ("Cerrar", "cerrar", "enlace")])
        if r == "generar":
            self.generar()
        elif r == "carpeta":
            abrir(ruta.parent) or abrir(u.carpeta)

    # ------------------------------------------------------------ generar
    def generar(self):
        desde, hasta = self.anios_elegidos()
        pid = self.programa_id()
        if motivo_para_no_generar(self.v_carpeta.get(), pid, desde, hasta, self.resumen):
            return
        estado, g = flujo.generar(self.raiz, self.almacen, self.config, self.v_carpeta.get(), pid, desde, hasta,
                                  self.uso_vista_previa)
        if g:
            self.al_generar(g, desde_revision=False)

    def al_generar(self, g, desde_revision):
        """Guarda la última generación y muestra el cuadro generado (31/33, o 32 si vino de la revisión)."""
        self.estado.ultima = flujo.ultima_generacion(g, self.config)
        self.estados.guardar(self.estado)
        self.actualizar()
        if desde_revision:
            return D.cuadro_generado(self.raiz, g, desde_revision=True)
        if D.cuadro_generado(self.raiz, g, abrir_revision=self.abrir_revision) == "revision":
            self.abrir_revision()
        return None

    def abrir_revision(self):
        if self.al_abrir_revision:
            self.al_abrir_revision()
