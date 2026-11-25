"""Ventanas modales: confirmar (03), progreso (30), cuadro generado (31, 33), generación detenida (43-45) y avisos."""
from __future__ import annotations

import queue
import threading
import time
import tkinter as tk
from datetime import datetime

from ..cruce.modelos import EXCEL, INFORMATIVO, PROGRAMA
from ..generacion import Cancelado, GeneracionDetenida, detalle_para_sistemas, generar
from ..generacion import errores as GE
from ..generacion import proceso as GP
from . import tema as T
from .modelo import cuando, vigencia
from .sistema import abrir


class Modal(tk.Toplevel):
    """Ventana modal centrada sobre su dueña; la X equivale al botón de cerrar o cancelar."""

    def __init__(self, duena, titulo, ancho=720):
        super().__init__(duena)
        self.withdraw()
        self.title(titulo)
        self.configure(bg=T.BLANCO)
        if duena.winfo_viewable():
            self.transient(duena)        # una ventana que depende de otra oculta no se mostraría (avisos al abrir)
        self.resizable(False, False)
        self.resultado = None
        self.cuerpo = tk.Frame(self, bg=T.BLANCO, padx=32, pady=26)
        self.cuerpo.pack(fill="both", expand=True)
        tk.Frame(self.cuerpo, bg=T.BLANCO, width=ancho - 64, height=0).pack()   # fija el ancho del modal
        self.ancho = ancho
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        self.bind("<Escape>", lambda e: self.al_cerrar())

    def mostrar(self):
        self.update_idletasks()
        duena = self.master.winfo_toplevel()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        if duena.winfo_viewable():
            x = duena.winfo_rootx() + max(0, (duena.winfo_width() - w) // 2)
            y = duena.winfo_rooty() + max(0, (duena.winfo_height() - h) // 3)
        else:
            x, y = (self.winfo_screenwidth() - w) // 2, (self.winfo_screenheight() - h) // 3
        self.geometry(f"+{x}+{max(0, y)}")
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.wait_window()
        return self.resultado

    def al_cerrar(self):
        self.cerrar(None)

    def cerrar(self, valor):
        self.resultado = valor
        self.grab_release()
        duena = self.master
        self.destroy()
        # Si esta ventana se abrió encima de otra ventana modal, esa recupera el control.
        if isinstance(duena, Modal) and duena.winfo_exists() and duena.winfo_viewable():
            duena.grab_set()
            duena.focus_set()

    # piezas comunes
    def encabezado(self, tipo, titulo, subtitulo=None):
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x", pady=(0, 18))
        T.icono(fila, tipo, d=48).pack(side="left", padx=(0, 18))
        textos = tk.Frame(fila, bg=T.BLANCO)
        textos.pack(side="left", fill="x")
        tk.Label(textos, text=titulo, font=T.F["modal_titulo"], bg=T.BLANCO, fg=T.GRIS_OSC, anchor="w").pack(fill="x")
        if subtitulo:
            tk.Label(textos, text=subtitulo, font=T.F["suave"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
        return fila

    def parrafo(self, partes, color=T.NEGRO, pady=(0, 10), vineta=False):
        """Párrafo con partes en negrita: [(texto, negrita), ...]. El alto se calcula midiendo el texto."""
        t = tk.Text(self.cuerpo, wrap="word", bd=0, bg=self.cuerpo["bg"], font=T.F["cuerpo"], height=1,
                    highlightthickness=0, cursor="arrow", fg=color, spacing1=1, spacing3=1, padx=0, pady=0)
        t.tag_configure("b", font=T.F["cuerpo_b"])
        margen = 0
        if vineta:
            margen = T.F["cuerpo"].measure("•  ")
            t.tag_configure("v", lmargin1=0, lmargin2=margen)
            t.insert("end", "•  ", ("v",))
        for texto, negrita in partes:
            t.insert("end", texto, ("b", "v") if negrita else ("v",))
        ancho_px = self.ancho - 64
        t.configure(state="disabled", width=max(10, ancho_px // max(1, T.F["cuerpo"].measure("0"))),
                    height=contar_lineas(partes, ancho_px - margen))
        t.pack(fill="x", pady=pady)
        return t

    def botones(self):
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x", pady=(16, 0))
        return fila


def contar_lineas(partes, ancho_px: int) -> int:
    """Líneas que ocupa un párrafo al ajustar por palabras, midiendo cada palabra con su tipografía."""
    lineas, x = 1, 0
    espacio = T.F["cuerpo"].measure(" ")
    for texto, negrita in partes:
        fuente = T.F["cuerpo_b"] if negrita else T.F["cuerpo"]
        for i, trozo in enumerate(texto.split("\n")):
            if i:
                lineas, x = lineas + 1, 0
            for palabra in trozo.split(" "):
                if not palabra:
                    x += espacio
                    continue
                w = fuente.measure(palabra)
                if x and x + w > ancho_px:
                    lineas, x = lineas + 1, 0
                x += w + espacio
    return lineas


def _tabla_resumen(padre, filas):
    interior = T.Caja(padre, fondo=T.FONDO, borde=T.LINEA, radio=T.RADIO + 2, padx=22, pady=14)
    interior.pack(fill="x", pady=(0, 14))
    for i, (k, v, punto) in enumerate(filas):
        tk.Label(interior, text=k, font=T.F["cuerpo_b"], bg=T.FONDO, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
        celda = tk.Frame(interior, bg=T.FONDO)
        celda.grid(row=i, column=1, sticky="w", padx=(60, 0))
        if punto:
            T.punto(celda, punto).pack(side="left", padx=(0, 8))
        tk.Label(celda, text=v, font=T.F["cuerpo"], bg=T.FONDO, anchor="w").pack(side="left")


# ---------------------------------------------------------------- 03 confirmar
def confirmar_generacion(duena, programa, desde, hasta, encontrados, esperados, faltan, config_modificada,
                         uso_vista_previa: bool) -> bool:
    m = Modal(duena, "Confirmar generación", ancho=700)
    m.encabezado("aviso", "¿Generar el cuadro maestro?")
    _tabla_resumen(m.cuerpo, [("Programa", programa, None), ("Vigencia", f"{desde} a {hasta}", None),
                              ("Archivos", f"{encontrados} de {esperados} encontrados",
                               T.VERDE_CTA if encontrados == esperados else T.NARANJA),
                              ("Configuración", f"modificada {config_modificada}", None)])
    if faltan:
        texto = (f"{'Falta' if len(faltan) == 1 else 'Faltan'} {len(faltan)} de {esperados} archivos ({', '.join(faltan[:3])}{'…' if len(faltan) > 3 else ''}). "
                 + ("Ese año quedará incompleto en el conteo." if len(faltan) == 1 else "Esos periodos quedarán incompletos en el conteo."))
        T.Franja(m.cuerpo, "aviso", texto).pack(fill="x", pady=(0, 14))
    m.parrafo([("Se usará la ", False), ("configuración de cruce de datos actual", True),
               (" de los Excel: las columnas, filtros y reglas guardadas en Configuración.", False)])
    tk.Label(m.cuerpo, text="Antes de continuar, ten en cuenta", font=T.F["cuerpo_b"], bg=T.BLANCO, fg=T.VERDE_CTA,
             anchor="w").pack(fill="x", pady=(4, 4))
    m.parrafo([("El resultado depende de esa configuración. Si los Excel cambiaron de columnas, nombres o filtros y la "
                "configuración no se actualizó, el cuadro puede quedar ", False), ("incompleto o con datos incorrectos", True),
               (".", False)], vineta=True, pady=(0, 4))
    m.parrafo([("El programa ", False), ("no modifica tus Excel originales", True), (": solo los lee y crea un archivo "
               "nuevo en la subcarpeta ", False), ("Cuadros generados", True), (".", False)], vineta=True, pady=(0, 4))
    if not uso_vista_previa:
        m.parrafo([("¿Dudas del resultado? Cancela y usa ", False), ("Previsualizar cuadro", True),
                   (": muestra cómo quedaría sin crear ningún archivo.", False)], vineta=True, pady=(0, 4))
    m.parrafo([("Después de generarlo, abre ", False), ("Ver revisión", True),
               (" y confirma lo que no se pudo cruzar antes de entregar el cuadro.", False)], vineta=True)
    tk.Label(m.cuerpo, text="¿Quieres continuar?", font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(fill="x", pady=(6, 0))
    fila = m.botones()
    si = T.Boton(fila, "Sí, generar cuadro maestro", lambda: m.cerrar(True), ancho=300)
    si.pack(side="right")
    cancelar = T.Boton(fila, "Cancelar", lambda: m.cerrar(False), tipo="secundario", ancho=170)
    cancelar.pack(side="right", padx=(0, 14))
    m.bind("<Return>", lambda e: m.cerrar(False))          # Enter cancela: el foco inicial está en Cancelar
    return bool(m.mostrar())


# ---------------------------------------------------------------- 30 progreso
NOMBRES_PASO = dict(GE.PASOS)
ESTADO_TEXTO = {GP.PENDIENTE: "Pendiente", GP.NO_SE_LLEGO: "No se llegó"}


class Progreso(Modal):
    """Corre la generación en otro hilo. Cancelar y la X son inmediatos: no se crea ningún archivo."""

    def __init__(self, duena, parametros: dict, chips: list[str]):
        super().__init__(duena, "Generando cuadro maestro", ancho=760)
        self.parametros, self.cola, self.cancelar_evt = parametros, queue.Queue(), threading.Event()
        self.inicio = time.monotonic()
        self.encabezado("curso", "Generando el cuadro maestro…", "Esto puede tardar un momento")
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x", pady=(0, 14))
        for c in chips:
            T.chip_contexto(fila, c).pack(side="left", padx=(0, 8))
        linea = tk.Frame(self.cuerpo, bg=T.BLANCO)
        linea.pack(fill="x")
        self.lbl_paso = tk.Label(linea, text="Paso 1 de 5", font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w")
        self.lbl_paso.pack(side="left")
        self.lbl_tiempo = tk.Label(linea, text="Tiempo: 0:00", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS)
        self.lbl_tiempo.pack(side="right")
        from tkinter import ttk
        self.barra = ttk.Progressbar(self.cuerpo, style="CM.Horizontal.TProgressbar", maximum=5)
        self.barra.pack(fill="x", pady=(8, 14))
        lista = T.tabla(self.cuerpo)
        lista.pack(fill="x")
        self.filas = {}
        for i, (paso, nombre) in enumerate(GE.PASOS):
            f = T.fila(lista, T.BLANCO, 16, 10, ultima=i == len(GE.PASOS) - 1)
            f.pack(fill="x")
            ic = T.icono(f, "pendiente", 26, bg=T.BLANCO)
            ic.pack(side="left")
            n = tk.Label(f, text=nombre, font=T.F["cuerpo_b"], bg=T.BLANCO, fg=T.DESACT_TXT, anchor="w")
            n.pack(side="left", padx=(8, 0))
            d = tk.Label(f, text="Pendiente", font=T.F["pequena"], bg=T.BLANCO, fg=T.DESACT_TXT)
            d.pack(side="right")
            self.filas[paso] = (f, ic, n, d)
            if i < len(GE.PASOS) - 1:
                tk.Frame(lista, bg=T.LINEA, height=1).pack(fill="x", padx=16)
        T.Franja(self.cuerpo, "info", "No abras ni edites los Excel de esta carpeta hasta que termine. Tus Excel "
                 "originales no se modifican: el cuadro se crea como un archivo nuevo.").pack(fill="x", pady=(14, 0))
        pie = self.botones()
        tk.Label(pie, text="Si cancelas, no se crea ningún archivo.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="left")
        T.Boton(pie, "Cancelar generación", self.al_cerrar, tipo="secundario", ancho=230).pack(side="right")
        pausar_recolector()
        self.hilo = threading.Thread(target=self._trabajar, daemon=True)
        self.hilo.start()
        reanudar_recolector_al_terminar(duena.winfo_toplevel(), self.hilo)
        self.after(100, self._revisar)

    def _trabajar(self):
        try:
            g = generar(**self.parametros, al_avanzar=lambda p, e, t: self.cola.put(("paso", p, e, t)),
                        cancelado=self.cancelar_evt.is_set)
            self.cola.put(("fin", g))
        except Cancelado:
            self.cola.put(("cancelado",))
        except GeneracionDetenida as e:
            self.cola.put(("detenida", e))
        except Exception as e:   # noqa: BLE001 — nunca dejar la ventana colgada
            self.cola.put(("fallo", e))

    def _revisar(self):
        if not self.winfo_exists():
            return
        s = int(time.monotonic() - self.inicio)
        self.lbl_tiempo.configure(text=f"Tiempo: {s // 60}:{s % 60:02d}")
        try:
            while True:
                m = self.cola.get_nowait()
                if m[0] == "paso":
                    self._pintar(*m[1:])
                else:
                    self.cerrar(m)
                    return
        except queue.Empty:
            pass
        self.after(100, self._revisar)

    def _pintar(self, paso, estado, texto):
        f, ic, n, d = self.filas[paso]
        orden = [p for p, _ in GE.PASOS]
        if estado == GP.EN_CURSO:
            i = orden.index(paso)
            self.lbl_paso.configure(text=f"Paso {i + 1} de 5  ·  {NOMBRES_PASO[paso]}")
            self.barra.configure(value=i + 0.5)
            for w in (ic, n, d):
                w.configure(bg=T.TINTE_VERDE)
            _fondo_fila(f, T.TINTE_VERDE)
            T.poner_simbolo(ic, "curso", 26)
            n.configure(fg=T.NEGRO)
            d.configure(text=texto or "En curso", fg=T.GRIS)
        else:
            for w in (ic, n, d):
                w.configure(bg=T.BLANCO)
            _fondo_fila(f, T.BLANCO)
            aviso = estado == GP.CON_AVISO
            T.poner_simbolo(ic, "aviso" if aviso else "ok", 26)
            n.configure(fg=T.NEGRO)
            d.configure(text=texto or "Listo", fg=T.AVISO_TXT if aviso else T.GRIS)
            self.barra.configure(value=orden.index(paso) + 1)

    def al_cerrar(self):
        self.cancelar_evt.set()                # el hilo se detiene en el siguiente punto de control
        self.cerrar(("cancelado",))


# ---------------------------------------------------------------- 31 / 33 cuadro generado
def cuadro_generado(duena, g, abrir_revision=None, desde_revision=False) -> str | None:
    """31 (primera vez, con avisos), 32 (de nuevo, desde la revisión) o 33 (sin avisos)."""
    r = g.resultado
    grupos = r.por_grupo()
    total = len(r.avisos)
    m = Modal(duena, "Cuadro maestro generado", ancho=800)
    m.encabezado("ok", "Cuadro maestro generado",
                 f"{r.programa['nombre']}  ·  vigencia {vigencia(r.anio_inicio, r.anio_fin)}  ·  {cuando(g.ahora)}")
    arch = T.Caja(m.cuerpo, fondo=T.BLANCO, borde=T.LINEA, radio=T.RADIO + 2, padx=20, pady=14)
    arch.pack(fill="x", pady=(0, 14))
    _icono_excel(arch).pack(side="left", padx=(0, 16))
    txt = tk.Frame(arch, bg=T.BLANCO)
    txt.pack(side="left", fill="x", expand=True)
    tk.Label(txt, text=g.ruta.name, font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w", wraplength=520,
             justify="left").pack(fill="x")
    tk.Label(txt, text=f"Guardado en  {g.ruta.parent}", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w",
             wraplength=520, justify="left").pack(fill="x")
    T.Boton(arch, "Abrir carpeta", lambda: abrir(g.ruta.parent), tipo="secundario", fuente="boton_peq",
            ancho=150, alto=38).pack(side="right")
    esperados = [e for e in g.lectura.esperados if e.fuente != "matriz"]
    leidos = sum(e.encontrado for e in esperados)
    cifras = tk.Frame(m.cuerpo, bg=T.BLANCO)
    cifras.pack(fill="x", pady=(0, 14))
    datos = [(f"{leidos} de {len(esperados)}", "archivos por año leídos",
              T.NARANJA if leidos < len(esperados) else T.VERDE_CTA,
              f"Falta {len(esperados) - leidos}" if leidos < len(esperados) else ""),
             (str(r.convenios_en_cuadro), "convenios en el cuadro", T.VERDE_CTA, ""),
             (str(r.movilidades_contadas + r.actividades_contadas), "movilidades y actividades", T.VERDE_CTA, ""),
             (str(total), "avisos para revisar", T.MAGENTA if total else T.VERDE_CTA, "Hay que revisar" if total else "")]
    for i, (num, etiqueta, color, nota) in enumerate(datos):
        cont = T.tarjeta(cifras, color, padx=14, pady=10)
        cont.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 10, 0))
        cifras.grid_columnconfigure(i, weight=1, uniform="c")
        tk.Label(cont, text=nota, font=T.F["pequena_b"], bg=T.BLANCO, fg=color if nota else T.BLANCO,
                 anchor="e").pack(fill="x")
        tk.Label(cont, text=num, font=T.F["cifra"], bg=T.BLANCO, anchor="w").pack(fill="x")
        tk.Label(cont, text=etiqueta, font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
    if total:
        bloque = T.Caja(m.cuerpo, fondo=T.FONDO, borde=None, grosor=0, radio=T.RADIO + 2, padx=18, pady=12)
        bloque.pack(fill="x")
        tk.Label(bloque, text=f"{total} avisos para revisar antes de entregar el cuadro", font=T.F["cuerpo_b"],
                 bg=T.FONDO, anchor="w").pack(fill="x")
        chips = tk.Frame(bloque, bg=T.FONDO)
        chips.pack(fill="x", pady=(8, 0))
        for n, texto, tipo in ((len(grupos[EXCEL]), "corrige el Excel", "error"),
                               (len(grupos[PROGRAMA]), "resuélvelo aquí", "aviso"),
                               (len(grupos[INFORMATIVO]), "informativos", "blanco")):
            if n:
                T.chip(chips, f"{n} {texto}", tipo).pack(side="left", padx=(0, 8))
        m.parrafo([("Lo que no se pudo cruzar queda fuera del cuadro o como dudoso. Ábrelo en Ver revisión, corrígelo y "
                    "genera de nuevo si hace falta.", False)], color=T.GRIS, pady=(12, 0))
    else:
        T.Franja(m.cuerpo, "info", "No quedó nada por revisar: todos los registros se cruzaron.").pack(fill="x")
    pie = m.botones()
    if desde_revision:
        T.Boton(pie, "Abrir cuadro", lambda: (abrir(g.ruta), m.cerrar("abrir")), ancho=200).pack(side="right")
        T.Boton(pie, "Volver a la revisión", lambda: m.cerrar("revision"), tipo="secundario",
                ancho=230).pack(side="right", padx=(0, 14))
    elif total:
        T.Enlace(pie, "Cerrar", lambda: m.cerrar("cerrar")).pack(side="left")
        ver = T.Boton(pie, f"Ver revisión ({total})", lambda: m.cerrar("revision"), ancho=240)
        ver.pack(side="right")
        ver.activar(abrir_revision is not None)
        T.Boton(pie, "Abrir cuadro", lambda: abrir(g.ruta), tipo="secundario", ancho=200).pack(side="right", padx=(0, 14))
    else:
        T.Boton(pie, "Abrir cuadro", lambda: (abrir(g.ruta), m.cerrar("abrir")), ancho=220).pack(side="right")
        T.Boton(pie, "Cerrar", lambda: m.cerrar("cerrar"), tipo="secundario", ancho=140).pack(side="right", padx=(0, 14))
    return m.mostrar()


def _icono_excel(padre, w=40, h=48):
    """Hoja de cálculo dibujada (mockup 31)."""
    from . import graficos as G
    bg = T.fondo_de(padre)

    def dibujar(d, W, H):
        s = W / w
        verde = G.rgb(T.VERDE_CTA)
        d.rounded_rectangle((2 * s, 2 * s, W - 2 * s, H - 2 * s), 4 * s, fill=G.rgb(T.OK_BG), outline=verde,
                            width=round(2 * s))
        for y in (.38, .56, .74):
            d.line((9 * s, H * y, W - 9 * s, H * y), fill=verde, width=round(2 * s))
        d.line((W * .45, H * .22, W * .45, H * .82), fill=verde, width=round(2 * s))
    return tk.Label(padre, image=G.imagen(padre, ("excel",), w, h, dibujar, bg), bg=bg, bd=0)


def _fondo_fila(f, color):
    """Cambia el fondo de una fila de tabla (tk.Frame o la última, redondeada)."""
    if isinstance(f, tk.Frame):
        f.configure(bg=color)


# ---------------------------------------------------------------- 43-45 generación detenida
def generacion_detenida(duena, det: GeneracionDetenida, contexto: dict, abrir_programas=None) -> str | None:
    m = Modal(duena, "La generación se detuvo", ancho=820)
    m.encabezado("error", "La generación se detuvo",
                 "No se creó ningún archivo. Los cambios pendientes siguen pendientes y tus Excel no se tocaron.")
    lista = T.Caja(m.cuerpo, fondo=T.BLANCO, borde=T.LINEA, radio=T.RADIO + 2, padx=16, pady=8)
    lista.pack(fill="x", pady=(0, 14))
    simbolo = {GP.HECHO: ("ok", T.VERDE_CTA), GP.CON_AVISO: ("aviso", T.NARANJA), GP.ERROR: ("error", T.MAGENTA),
               GP.NO_SE_LLEGO: ("pendiente", T.DESACT_TXT), GP.PENDIENTE: ("pendiente", T.DESACT_TXT),
               GP.EN_CURSO: ("pendiente", T.DESACT_TXT)}
    for p in det.pasos:
        f = tk.Frame(lista, bg=T.BLANCO)
        f.pack(fill="x", pady=3)
        s, color = simbolo[p.estado]
        T.icono(f, s, d=20, bg=T.BLANCO).pack(side="left")
        tk.Label(f, text=NOMBRES_PASO[p.paso], font=T.F["cuerpo"], bg=T.BLANCO,
                 fg=T.DESACT_TXT if p.estado == GP.NO_SE_LLEGO else T.NEGRO).pack(side="left", padx=(6, 0))
        texto = p.texto or ("Se detuvo aquí" if p.estado == GP.ERROR else "")
        tk.Label(f, text=texto, font=T.F["pequena"], bg=T.BLANCO, fg=color).pack(side="right")
    n = len(det.errores)
    tk.Label(m.cuerpo, text=f"Hoja de errores  ·  {n} {'error' if n == 1 else 'errores'} que impiden generar",
             font=T.F["seccion"], bg=T.BLANCO, anchor="w").pack(fill="x", pady=(0, 8))
    contenedor = _desplazable(m.cuerpo, alto=min(380, 150 * n))
    for e in det.errores:
        _tarjeta_error(contenedor, e, abrir_programas, m.ancho)
    tk.Label(m.cuerpo, text="Un archivo que existe pero no se puede leer detiene la generación: no se omite en silencio.",
             font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x", pady=(10, 0))
    pie = m.botones()

    def copiar():
        m.clipboard_clear()
        m.clipboard_append(detalle_para_sistemas(det.errores, contexto))
        copiar_lbl.configure(text="Detalle copiado ✓")

    copiar_lbl = T.Enlace(pie, "Copiar detalle del error", copiar, fuente="pequena_b")
    copiar_lbl.pack(side="left")
    T.Boton(pie, "Reintentar", lambda: m.cerrar("reintentar"), ancho=170).pack(side="right")
    T.Boton(pie, "Cerrar", lambda: m.cerrar("cerrar"), tipo="secundario", ancho=130).pack(side="right", padx=(0, 14))
    return m.mostrar()


def _desplazable(padre, alto):
    marco = T.desplazable(padre, alto)
    marco.pack(fill="x")
    return marco.interior


def _tarjeta_error(padre, e: GE.ErrorGeneracion, abrir_programas, ancho=820):
    c = T.tarjeta(padre, T.MAGENTA, borde=T.MAGENTA, padx=16, pady=10)
    c.pack(fill="x", pady=(0, 10))
    arriba = tk.Frame(c, bg=T.BLANCO)
    arriba.pack(fill="x")
    tk.Label(arriba, text=e.titulo, font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w", wraplength=ancho - 330,
             justify="left").pack(side="left")
    T.chip(arriba, e.etiqueta, "error").pack(side="right")
    for etiqueta, valor, color in (("Dónde", e.donde, T.GRIS), ("Qué pasó", e.que_paso, T.NEGRO),
                                   ("Qué hacer", e.que_hacer, T.NEGRO)):
        f = tk.Frame(c, bg=T.BLANCO)
        f.pack(fill="x", pady=(4, 0))
        etiqueta_ancho = T.F["pequena_b"].measure("Qué hacer  ")
        col = tk.Frame(f, bg=T.BLANCO, width=etiqueta_ancho, height=1)
        col.pack(side="left", anchor="n")
        col.pack_propagate(False)
        tk.Label(f, text=etiqueta, font=T.F["pequena_b"], bg=T.BLANCO, anchor="nw",
                 fg=T.VERDE_CTA if etiqueta == "Qué hacer" else T.GRIS_OSC).place(in_=col, x=0, y=0)
        col.configure(height=T.F["pequena_b"].metrics("linespace"))
        tk.Label(f, text=valor, font=T.F["pequena"], bg=T.BLANCO, fg=color, anchor="w", justify="left",
                 wraplength=ancho - 64 - 20 - 40 - etiqueta_ancho - 30).pack(side="left", fill="x")
    acciones = tk.Frame(c, bg=T.BLANCO)
    acciones.pack(fill="x", pady=(8, 0))
    destino = e.ruta.parent if e.ruta and e.ruta.suffix else e.ruta
    for a in e.acciones:
        if a == "abrir_carpeta" and destino:
            T.Boton(acciones, "Abrir carpeta", lambda d=destino: abrir(d), tipo="secundario", fuente="boton_peq",
                    ancho=150, alto=34).pack(side="left", padx=(0, 8))
        elif a == "abrir_archivo" and e.ruta:
            T.Boton(acciones, T.texto_abrir(e.ruta), lambda r=e.ruta: abrir(r), tipo="secundario",
                    fuente="boton_peq", ancho=T.F["boton_peq"].measure(T.texto_abrir(e.ruta)) + 44,
                    alto=34).pack(side="left", padx=(0, 8))
        elif a == "abrir_programas" and abrir_programas:
            T.Boton(acciones, "Abrir Programas", abrir_programas, tipo="secundario", fuente="boton_peq",
                    ancho=170, alto=34).pack(side="left", padx=(0, 8))


# ---------------------------------------------------------------- avisos simples (46-49 y otros)
def aviso(duena, titulo, tipo, mensaje, botones: list[tuple[str, str, str]], detalle: list[str] | None = None):
    """botones: [(texto, valor, "primario"|"secundario"|"enlace")] de derecha a izquierda."""
    m = Modal(duena, titulo, ancho=640)
    m.encabezado(tipo, titulo)
    m.parrafo([(mensaje, False)])
    for d in detalle or []:
        m.parrafo([(d, False)], color=T.GRIS, vineta=True, pady=(0, 2))
    pie = m.botones()
    for texto, valor, estilo in botones:
        if estilo == "enlace":
            T.Enlace(pie, texto, lambda v=valor: m.cerrar(v)).pack(side="left")
        else:
            T.Boton(pie, texto, lambda v=valor: m.cerrar(v), tipo=estilo,
                    ancho=max(130, 11 * len(texto) + 40)).pack(side="right", padx=(14, 0))
    return m.mostrar()


def pausar_recolector():
    """Si el recolector de basura de Python corriera en un hilo de trabajo podría borrar variables de Tk (StringVar
    de pantallas ya cerradas) desde ese hilo, y Tcl se cae («Segmentation fault»). Se recoge aquí, en el hilo de la
    ventana, y se pausa mientras el otro hilo trabaja."""
    import gc
    gc.collect()
    gc.disable()


def reanudar_recolector_al_terminar(ventana, hilo):
    import gc

    def revisar():
        if hilo.is_alive():
            ventana.after(150, revisar)
        else:
            gc.enable()
    ventana.after(150, revisar)


def en_espera(duena, trabajo, titulo="Leyendo los archivos…", subtitulo="Solo se leen: no se crea ni se cambia nada."):
    """Hace `trabajo()` en otro hilo con una ventana de espera encima de `duena`; devuelve su resultado o
    vuelve a lanzar su error. Sirve para todo lo que lee Excel desde la interfaz (vista previa, Fuentes, Campos)."""
    import threading
    salida = {}
    pausar_recolector()

    def trabajar():
        try:
            salida["r"] = trabajo()
        except Exception as e:   # noqa: BLE001
            salida["e"] = e

    espera = Modal(duena, "Leyendo los archivos", ancho=460)
    espera.encabezado("curso", titulo, subtitulo)
    hilo = threading.Thread(target=trabajar, daemon=True)
    hilo.start()

    def revisar():
        if hilo.is_alive():
            espera.after(100, revisar)
        else:
            espera.cerrar(True)
    espera.after(100, revisar)
    espera.protocol("WM_DELETE_WINDOW", lambda: None)
    espera.unbind("<Escape>")
    reanudar_recolector_al_terminar(espera.master.winfo_toplevel(), hilo)
    espera.mostrar()
    if "e" in salida:
        raise salida["e"]
    return salida["r"]


def ahora_texto() -> str:
    return cuando(datetime.now())
