"""Pantalla «Ver revisión» (mockups 10, 11, 12, 41), Elegir institución (28) y salir con cambios sin incluir (13)."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path

from .. import revision as RV
from ..cruce.modelos import EXCEL, INFORMATIVO, ORDEN_GRUPOS, PROGRAMA
from ..texto import normalizar
from . import dialogos as D
from . import flujo
from . import tema as T
from .modelo import cuando, vigencia
from .sistema import abrir

GRUPOS = {
    EXCEL: ("Corrige el Excel y recarga", "Estos avisos se arreglan fuera del programa: edita el archivo, guárdalo, "
            "ciérralo y pulsa Recargar archivos.", T.MAGENTA, T.ROSA_SUAVE, ("se corrige en el Excel", "se corrigen en el Excel")),
    PROGRAMA: ("Resuélvelo aquí en el programa", "No tienes que tocar el Excel. Elige o indica la opción correcta y el "
               "programa la recuerda.", T.NARANJA, T.AVISO_BG, ("se resuelve aquí", "se resuelven aquí")),
    INFORMATIVO: ("Solo informativo", "No necesitan acción; se muestran para que sepas qué quedó fuera del cuadro.",
                  "#9A9A9A", "#EDEDED", ("solo informativo", "solo informativos")),
}
MARCAS = {"nuevo": ("Nuevo", T.ROSA_SUAVE, T.MAGENTA), "sigue": ("Sigue pendiente", T.AVISO_BG, T.AVISO_TXT),
          "igual": ("Sin cambios", "#EDEDED", T.GRIS)}
ACCIONES_SIN_PANTALLA = {"abrir_fuentes": "Abrir Fuentes de datos", "preguntar_a_gemini": "Preguntar a Gemini"}
ACCIONES_MODAL = {"abrir_programas": ("Abrir Programas", "programas"), "abrir_tipos": ("Abrir Tipos de persona", "tipos"),
                  "abrir_equivalencias_programas": ("Abrir Equivalencias de programas", "eq_prog")}


class PantallaRevision(tk.Frame):
    def __init__(self, app, al_volver):
        super().__init__(app.raiz, bg=T.BLANCO)
        self.app, self.al_volver = app, al_volver
        self.u = app.estado.ultima
        self.recarga = None
        self.instituciones = None
        self._construir()
        self._pintar()

    # ------------------------------------------------------------ armado
    def _construir(self):
        cab = tk.Frame(self, bg=T.BLANCO, padx=28, pady=16)
        cab.pack(fill="x")
        self.app.ventana._logo(cab).pack(side="left")
        der = tk.Frame(cab, bg=T.BLANCO)
        der.pack(side="right")
        tk.Label(der, text="Revisión", font=T.F["app_titulo"], bg=T.BLANCO, fg=T.GRIS_OSC).pack(anchor="e")
        tk.Label(der, text="Oficina de Relaciones Internacionales", font=T.F["app_sub"], bg=T.BLANCO,
                 fg=T.GRIS).pack(anchor="e")
        tk.Frame(self, bg=T.VERDE, height=4).pack(fill="x")
        self.arriba = tk.Frame(self, bg=T.BLANCO, padx=28, pady=14)
        self.arriba.pack(fill="x")
        tk.Frame(self, bg=T.LINEA, height=1).pack(fill="x")
        self.pie = tk.Frame(self, bg=T.BLANCO, padx=28, pady=12)
        self.pie.pack(side="bottom", fill="x")
        tk.Frame(self, bg=T.LINEA, height=1).pack(side="bottom", fill="x")
        marco = tk.Frame(self, bg=T.FONDO)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, bg=T.FONDO, highlightthickness=0)
        barra = tk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
        self.lista = tk.Frame(self.lienzo, bg=T.FONDO, padx=28, pady=16)
        vid = self.lienzo.create_window(0, 0, window=self.lista, anchor="nw")
        self.lista.bind("<Configure>", lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda e: (self.lienzo.itemconfigure(vid, width=e.width), self._ancho(e.width)))
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.ancho = 900

    def _ancho(self, w):
        if abs(w - self.ancho) > 40:
            self.ancho = w
            self.after_idle(self._pintar_lista)

    def avisos(self):
        if self.recarga:
            return self.recarga.resultado.avisos
        lista = self.u.avisos_actuales if self.u.avisos_actuales is not None else self.u.avisos_lista
        return [RV.aviso_de_dict(d) for d in lista]

    def _pintar(self):
        self._pintar_arriba()
        self._pintar_lista()
        self._pintar_pie()

    def _pintar_arriba(self):
        a = self.arriba
        for w in a.winfo_children():
            w.destroy()
        fila = tk.Frame(a, bg=T.BLANCO)
        fila.pack(fill="x")
        T.Enlace(fila, "‹ Volver al cuadro maestro", self.volver).pack(side="left")
        hora = datetime.fromisoformat(self.u.hora)
        tk.Label(fila, text=f"{self.u.programa}  ·  vigencia {vigencia(self.u.anio_inicio, self.u.anio_fin)}  ·  "
                            f"generado {cuando(hora)}", font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS).pack(side="right")
        pasos = tk.Frame(a, bg=T.BLANCO)
        pasos.pack(fill="x", pady=(12, 10))
        for i, (titulo, texto) in enumerate((("Lee el aviso", "Cada tarjeta dice qué pasó y qué hacer."),
                                             ("Corrígelo", "En tu Excel o aquí en el programa; la tarjeta te lo indica."),
                                             ("Recarga", "Guarda y cierra el Excel, pulsa Recargar archivos y mira qué cambió."))):
            ultimo = i == 2
            borde = tk.Frame(pasos, bg=T.VERDE if ultimo else T.LINEA, padx=1, pady=1)
            borde.grid(row=0, column=i * 2, sticky="nsew")
            pasos.grid_columnconfigure(i * 2, weight=1, uniform="p")
            fondo = T.TINTE_VERDE if ultimo else T.BLANCO
            c = tk.Frame(borde, bg=fondo, padx=12, pady=8)
            c.pack(fill="both", expand=True)
            n = tk.Canvas(c, width=28, height=28, bg=fondo, highlightthickness=0)
            n.create_oval(1, 1, 27, 27, fill=T.VERDE_CTA, outline=T.VERDE_CTA)
            n.create_text(14, 15, text=str(i + 1), fill=T.BLANCO, font=T.F["pequena_b"])
            n.pack(side="left", anchor="n", padx=(0, 10))
            tx = tk.Frame(c, bg=fondo)
            tx.pack(side="left", fill="x", expand=True)
            tk.Label(tx, text=titulo, font=T.F["cuerpo_b"], bg=fondo, anchor="w").pack(fill="x")
            tk.Label(tx, text=texto, font=T.F["pequena"], bg=fondo, anchor="w", justify="left",
                     wraplength=230).pack(fill="x")
            if not ultimo:
                T.flecha(pasos, T.BLANCO).grid(row=0, column=i * 2 + 1, padx=6)
        resumen = tk.Frame(a, bg=T.BLANCO)
        resumen.pack(fill="x")
        avisos = self.avisos()
        if self.recarga:
            c = self.recarga.comparacion
            caja = tk.Frame(resumen, bg=T.VERDE, padx=1, pady=1)
            caja.pack(fill="x")
            dentro = tk.Frame(caja, bg=T.OK_BG, padx=14, pady=8)
            dentro.pack(fill="both")
            T.icono(dentro, "ok", 22, bg=T.OK_BG).pack(side="left")
            tk.Label(dentro, text=f"Archivos recargados {cuando(datetime.now())}.  Antes {c.antes} avisos, ahora {c.ahora}.",
                     font=T.F["cuerpo_b"], bg=T.OK_BG, fg=T.OK_TXT).pack(side="left", padx=(10, 0))
            for n, texto, fondo, color in ((len(c.nuevos), "nuevo" if len(c.nuevos) == 1 else "nuevos", T.ROSA_SUAVE, T.MAGENTA),
                                           (len(c.siguen), "siguen", T.AVISO_BG, T.AVISO_TXT),
                                           (len(c.resueltos), "resueltos", "#E3EED2", T.OK_TXT)):
                tk.Label(dentro, text=f"{n} {texto}", font=T.F["pequena_b"], bg=fondo, fg=color, padx=10,
                         pady=3).pack(side="right", padx=(6, 0))
        else:
            tk.Label(resumen, text=f"{len(avisos)} aviso{'s' if len(avisos) != 1 else ''}", font=T.F["seccion"],
                     bg=T.BLANCO).pack(side="left", padx=(0, 12))
            cuenta = RV.contar_por_grupo(avisos)
            for g in ORDEN_GRUPOS:
                if cuenta[g]:
                    _, _, color, fondo, (uno, varios) = GRUPOS[g]
                    tk.Label(resumen, text=f"{cuenta[g]} {uno if cuenta[g] == 1 else varios}", font=T.F["pequena_b"], bg=fondo,
                             fg=color if g != INFORMATIVO else T.GRIS_OSC, padx=12, pady=4).pack(side="left", padx=(0, 8))

    def _pintar_lista(self):
        lista = self.lista
        for w in lista.winfo_children():
            w.destroy()
        avisos = self.avisos()
        envoltura = max(300, self.ancho - 56 - 300)
        if self.recarga and self.recarga.comparacion.resueltos:
            caja = tk.Frame(lista, bg=T.VERDE, padx=1, pady=1)
            caja.pack(fill="x", pady=(0, 16))
            d = tk.Frame(caja, bg=T.OK_BG, padx=18, pady=12)
            d.pack(fill="both")
            res = self.recarga.comparacion.resueltos
            tk.Label(d, text=f"Resueltos desde la última lectura ({len(res)})", font=T.F["seccion"], bg=T.OK_BG,
                     fg=T.OK_TXT, anchor="w").pack(fill="x", pady=(0, 6))
            for a in res:
                f = tk.Frame(d, bg=T.OK_BG)
                f.pack(fill="x", pady=2)
                T.icono(f, "ok", 20, bg=T.OK_BG).pack(side="left")
                tk.Label(f, text=a.titulo, font=T.F["cuerpo_b"], bg=T.OK_BG).pack(side="left", padx=(10, 6))
                tk.Label(f, text="—  " + RV.que_se_logro(a), font=T.F["cuerpo"], bg=T.OK_BG, fg=T.OK_TXT).pack(side="left")
        if not avisos:
            self._vacio(lista)
            return
        marcas = self._marcas()
        for g in ORDEN_GRUPOS:
            del_grupo = [a for a in avisos if a.grupo == g]
            if not del_grupo:
                continue
            titulo, explicacion, color, _, _ = GRUPOS[g]
            cab = tk.Frame(lista, bg=T.FONDO)
            cab.pack(fill="x", pady=(8, 10))
            n = tk.Canvas(cab, width=40, height=40, bg=T.FONDO, highlightthickness=0)
            n.create_oval(1, 1, 39, 39, fill=color, outline=color)
            n.create_text(20, 21, text=str(len(del_grupo)), fill=T.BLANCO, font=T.F["cuerpo_b"])
            n.pack(side="left", anchor="n", padx=(0, 14))
            tx = tk.Frame(cab, bg=T.FONDO)
            tx.pack(side="left", fill="x", expand=True)
            tk.Label(tx, text=titulo, font=T.F["seccion"], bg=T.FONDO,
                     anchor="w").pack(fill="x")
            tk.Label(tx, text=explicacion, font=T.F["pequena"], bg=T.FONDO, fg=T.GRIS, anchor="w", justify="left",
                     wraplength=envoltura + 200).pack(fill="x")
            for a in del_grupo:
                self._tarjeta(lista, a, color, marcas.get(a.clave), envoltura)

    def _marcas(self):
        if not self.recarga:
            return {}
        c = self.recarga.comparacion
        m = {a.clave: "nuevo" for a in c.nuevos}
        m.update({a.clave: ("igual" if a.grupo == INFORMATIVO else "sigue") for a in c.siguen})
        return m

    def _tarjeta(self, padre, a, color, marca, envoltura):
        borde = tk.Frame(padre, bg=T.LINEA, padx=1, pady=1)
        borde.pack(fill="x", pady=(0, 12))
        t = tk.Frame(borde, bg=T.BLANCO)
        t.pack(fill="both")
        tk.Frame(t, bg=color, width=5).pack(side="left", fill="y")
        c = tk.Frame(t, bg=T.BLANCO, padx=20, pady=12)
        c.pack(side="left", fill="both", expand=True)
        arriba = tk.Frame(c, bg=T.BLANCO)
        arriba.pack(fill="x")
        tk.Label(arriba, text=a.titulo, font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w", justify="left",
                 wraplength=envoltura).pack(side="left")
        if marca:
            texto, fondo, fg = MARCAS[marca]
            tk.Label(arriba, text=texto, font=T.F["pequena_b"], bg=fondo, fg=fg, padx=10, pady=3).pack(side="right")
        ancho_et = T.F["pequena_b"].measure("Qué hacer  ")
        for etiqueta, valor, fg in (("Dónde", a.donde, T.GRIS), ("Qué pasó", a.que_paso, T.NEGRO),
                                    ("Qué hacer", a.que_hacer, T.NEGRO)):
            f = tk.Frame(c, bg=T.BLANCO)
            f.pack(fill="x", pady=(5, 0))
            col = tk.Frame(f, bg=T.BLANCO, width=ancho_et + 14, height=T.F["pequena_b"].metrics("linespace"))
            col.pack(side="left", anchor="n")
            col.pack_propagate(False)
            tk.Label(col, text=etiqueta, font=T.F["pequena_b"], bg=T.BLANCO,
                     fg=T.VERDE_CTA if etiqueta == "Qué hacer" else T.GRIS_OSC).pack(anchor="w")
            tk.Label(f, text=valor, font=T.F["pequena"], bg=T.BLANCO, fg=fg, anchor="w", justify="left",
                     wraplength=envoltura + 120).pack(side="left", fill="x")
        acciones = tk.Frame(c, bg=T.BLANCO)
        acciones.pack(fill="x", pady=(10, 0))
        tk.Frame(acciones, bg=T.BLANCO, width=ancho_et + 14).pack(side="left")
        for accion in a.acciones:
            b = self._boton_accion(acciones, accion, a)
            if b:
                b.pack(side="left", padx=(0, 8))

    def _boton_accion(self, padre, accion, a):
        crear = lambda texto, fn, ancho=None: T.Boton(padre, texto, fn, tipo="secundario", fuente="boton_peq",  # noqa: E731
                                                      ancho=ancho or (T.F["boton_peq"].measure(texto) + 44), alto=36)
        if accion == "abrir_archivo" and a.ruta:
            return crear(T.texto_abrir(a.ruta), lambda: self._abrir(a.ruta))
        if accion == "abrir_carpeta":
            return crear("Abrir carpeta", lambda: self._abrir(a.ruta.parent if a.ruta else Path(self.u.carpeta)))
        if accion == "elegir_institucion":
            return crear("Elegir institución…", lambda: self.elegir_institucion(a))
        if accion == "confirmar_sugerencia":
            return crear("Confirmar sugerencia", lambda: self.confirmar(a))
        if accion in ACCIONES_MODAL:
            texto, clave = ACCIONES_MODAL[accion]
            return crear(texto, lambda: self.app.abrir_modal(clave, self.app.raiz))
        if accion in ACCIONES_SIN_PANTALLA:
            b = crear(ACCIONES_SIN_PANTALLA[accion], None)
            b.activar(False)            # Configuración llega en la próxima versión
            return b
        return None

    def _vacio(self, padre):
        """Mockup 41: no quedó nada por revisar."""
        caja = tk.Frame(padre, bg=T.LINEA, padx=1, pady=1)
        caja.pack(fill="x", pady=30)
        d = tk.Frame(caja, bg=T.BLANCO, padx=30, pady=30)
        d.pack(fill="both")
        T.icono(d, "ok", 56).pack()
        tk.Label(d, text="No hay nada que revisar", font=T.F["modal_titulo"], bg=T.BLANCO).pack(pady=(14, 6))
        tk.Label(d, text="Todos los registros se cruzaron con su convenio y no quedó ningún aviso. Si cambias algún "
                         "Excel, guárdalo, ciérralo y pulsa Recargar archivos para comprobarlo.",
                 font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS, wraplength=560, justify="center").pack()
        T.Boton(d, "Abrir cuadro", lambda: self._abrir(Path(self.u.ruta)), tipo="secundario",
                ancho=190).pack(pady=(18, 0))

    def _pintar_pie(self):
        p = self.pie
        for w in p.winfo_children():
            w.destroy()
        pendiente = self.u.cambios_sin_incluir
        if pendiente:
            T.Franja(p, "info", "Los cambios ya se ven aquí, pero el cuadro anterior no cambió. Genera de nuevo para "
                     "incluirlos.").pack(fill="x", pady=(0, 10))
        else:
            T.Franja(p, "aviso", "Antes de recargar: guarda y cierra los Excel que hayas editado. Si siguen abiertos, "
                     "el programa no ve tus cambios.").pack(fill="x", pady=(0, 10))
        fila = tk.Frame(p, bg=T.BLANCO)
        fila.pack(fill="x")
        info = tk.Frame(fila, bg=T.BLANCO)
        info.pack(side="left", fill="x", expand=True)
        lectura = datetime.fromisoformat(self.u.ultima_lectura or self.u.hora)
        tk.Label(info, text=f"Última lectura: {cuando(lectura)}  ·  {self.u.leidos} de {self.u.esperados} archivos",
                 font=T.F["cuerpo_b"], bg=T.BLANCO, anchor="w").pack(fill="x")
        tk.Label(info, text="Recargar vuelve a leer tus archivos y actualiza esta lista. No cambia tus Excel.",
                 font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w", justify="left", wraplength=360).pack(fill="x")
        botones = [("Recargar archivos", self.recargar), ("Generar cuadro de nuevo", self.generar_de_nuevo)]
        if pendiente:
            botones.reverse()           # después de recargar con cambios, lo principal es generar
        T.Boton(fila, botones[0][0], botones[0][1], ancho=260, alto=50).pack(side="right")
        T.Boton(fila, botones[1][0], botones[1][1], tipo="secundario", ancho=260, alto=50).pack(side="right", padx=(0, 14))

    # ------------------------------------------------------------ acciones
    def _abrir(self, ruta):
        if not abrir(ruta):
            D.aviso(self.app.raiz, "No se encontró", "error", f"«{ruta}» ya no existe o no se puede abrir.",
                    [("Cerrar", "cerrar", "primario")])

    def recargar(self):
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            antes = self.avisos()
            r = RV.recargar(self.u.carpeta, self.app.config, self.u.programa_id, self.u.anio_inicio, self.u.anio_fin,
                            antes, self.u.firmas, self.u.config_firmas)
        finally:
            self.config(cursor="")
        if r.errores:
            from ..generacion import errores as GE
            from ..generacion.proceso import EstadoPaso, GeneracionDetenida
            det = GeneracionDetenida([GE.de_lectura(e) for e in r.errores],
                                     [EstadoPaso(p, "hecho") for p, _ in GE.PASOS[:3]])
            D.generacion_detenida(self.app.raiz, det, {"Programa": self.u.programa})
            return
        self.recarga = r
        self.u.avisos_actuales = [RV.aviso_a_dict(a) for a in r.resultado.avisos]
        self.u.filas_cambian = r.filas_cambian
        self.u.cambios_sin_incluir = r.hay_cambios
        self.u.leidos, self.u.esperados = r.leidos, r.esperados
        self.u.ultima_lectura = datetime.now().isoformat()
        self.app.guardar_estado()
        self._pintar()

    def _config_cambiada(self, que):
        self.app.guardar_config()
        self._pintar_pie()
        D.aviso(self.app.raiz, "Guardado", "ok", f"Se guardó: {que}. Pulsa Recargar archivos para ver el efecto.",
                [("Entendido", "ok", "primario")])

    def confirmar(self, a):
        que = RV.confirmar_sugerencia(self.app.config, a)
        self._config_cambiada(que)

    def elegir_institucion(self, a):
        if self.instituciones is None:
            self.config(cursor="watch")
            self.update_idletasks()
            self.instituciones = RV.instituciones_de_la_matriz(self.u.carpeta, self.app.config)
            self.config(cursor="")
        eleccion = ElegirInstitucion(self.app.raiz, a, self.instituciones).mostrar()
        if eleccion:
            RV.guardar_equivalencia_institucion(self.app.config, a.detalle["como_aparece"], eleccion)
            self._config_cambiada(f"«{a.detalle['como_aparece']}» es {eleccion} (Equivalencias de instituciones)")

    def generar_de_nuevo(self):
        estado, g = generar_de_nuevo(self.app)
        if g:
            self.recarga = None
            self.u = self.app.estado.ultima
            self._pintar()
        return estado

    def volver(self):
        if self.u.cambios_sin_incluir and not salir_con_cambios(self.app, self.recarga, self):
            return
        self.al_volver()


def generar_de_nuevo(app):
    """Genera con los mismos datos del último cuadro (programa, vigencia, carpeta) y lo muestra (mockup 32)."""
    u = app.estado.ultima
    estado, g = flujo.generar(app.raiz, app.almacen, app.config, u.carpeta, u.programa_id, u.anio_inicio, u.anio_fin)
    if g:
        app.ventana.al_generar(g, desde_revision=True)
    return estado, g


def salir_con_cambios(app, recarga=None, pantalla=None) -> bool:
    """Mockup 13: con cambios sin incluir no se sale sin generar. Devuelve True si ya se puede salir.

    Si la generación falla (no si se cancela), se deja salir y el estado pendiente queda guardado.
    """
    u = app.estado.ultima
    m = D.Modal(app.raiz, "Cambios sin incluir en el cuadro", ancho=720)
    m.encabezado("aviso", "Hay correcciones que aún no están en tu cuadro")
    m.parrafo([("Recargaste los archivos o cambiaste la configuración, y el resultado cambió. El cuadro que generaste "
                "antes quedó desactualizado, así que para salir hay que generarlo de nuevo.", False)])
    caja = tk.Frame(m.cuerpo, bg=T.FONDO, padx=20, pady=14)
    caja.pack(fill="x", pady=(0, 10))
    if recarga:
        c = recarga.comparacion
        chips = tk.Frame(caja, bg=T.FONDO)
        chips.pack(fill="x", pady=(0, 8))
        for n, texto, fondo, fg in ((len(c.resueltos), "aviso resuelto", "#E3EED2", T.OK_TXT),
                                    (len(c.nuevos), "aviso nuevo", T.ROSA_SUAVE, T.MAGENTA)):
            if n:
                plural = texto if n == 1 else texto.replace("aviso ", "avisos ").replace("resuelto", "resueltos").replace("nuevo", "nuevos")
                tk.Label(chips, text=f"{n} {plural}", font=T.F["pequena_b"], bg=fondo, fg=fg, padx=10,
                         pady=4).pack(side="left", padx=(0, 8))
    cambiada = RV.elementos_cambiados(u.config_firmas, app.config)
    if cambiada:
        f = tk.Frame(caja, bg=T.FONDO)
        f.pack(fill="x", pady=(0, 8))
        tk.Label(f, text="Configuración cambiada desde que generaste:", font=T.F["cuerpo"], bg=T.FONDO).pack(side="left")
        for nombre, n in cambiada.items():
            tk.Label(f, text=f"{nombre} ({n})", font=T.F["pequena_b"], bg=T.AVISO_BG, fg=T.AVISO_TXT, padx=10,
                     pady=3).pack(side="left", padx=(8, 0))
    if u.filas_cambian:
        tk.Label(caja, text=f"El cuadro nuevo cambia en {u.filas_cambian} fila{'s' if u.filas_cambian != 1 else ''}.",
                 font=T.F["cuerpo_b"], bg=T.FONDO, anchor="w").pack(fill="x")
    tk.Label(m.cuerpo, text="Se crea un archivo nuevo. El anterior no se borra ni se modifica.", font=T.F["pequena"],
             bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x")
    pie = m.botones()
    T.Boton(pie, "Generar cuadro de nuevo", lambda: m.cerrar("generar"), ancho=300).pack(side="right")
    T.Boton(pie, "Volver a la revisión", lambda: m.cerrar("volver"), tipo="secundario", ancho=230).pack(side="right", padx=(0, 14))
    tk.Label(m.cuerpo, text="Si el programa se cierra de otra forma, esto se pedirá al abrirlo la próxima vez.",
             font=T.F["pequena"], bg=T.BLANCO, fg=T.GRIS, anchor="w").pack(fill="x", pady=(12, 0))
    if m.mostrar() != "generar":
        return False
    estado = pantalla.generar_de_nuevo() if pantalla else generar_de_nuevo(app)[0]
    return estado != flujo.CANCELADO


class ElegirInstitucion(D.Modal):
    """Mockup 28: el nombre como viene en el Excel, buscador y sugerencias con su parecido. Ninguna viene elegida."""

    def __init__(self, duena, aviso, instituciones):
        super().__init__(duena, "Elegir institución", ancho=860)
        self.instituciones = instituciones
        self.cuenta = {normalizar(n): c for n, c in instituciones}
        self.elegida = tk.StringVar()
        fila = tk.Frame(self.cuerpo, bg=T.BLANCO)
        fila.pack(fill="x")
        tk.Label(fila, text="Elegir institución", font=T.F["modal_titulo"], bg=T.BLANCO).pack(side="left")
        T.Ayuda(fila, "elegir_inst").pack(side="left", padx=10)
        tk.Label(fila, text="Se guarda como equivalencia", font=T.F["pequena_b"], bg=T.FONDO, padx=12,
                 pady=4).pack(side="right")
        chips = tk.Frame(self.cuerpo, bg=T.BLANCO)
        chips.pack(fill="x", pady=(10, 12))
        for c in (f"Archivo: {aviso.ruta.name if aviso.ruta else ''} · fila {aviso.filas[0] if aviso.filas else '—'}",
                  f"{aviso.cantidad} sin contar"):
            tk.Label(chips, text=c, font=T.F["pequena_b"], bg=T.FONDO, padx=12, pady=4).pack(side="left", padx=(0, 8))
        caja = tk.Frame(self.cuerpo, bg=T.FONDO, padx=18, pady=10)
        caja.pack(fill="x")
        tk.Label(caja, text="Así aparece en el Excel", font=T.F["pequena"], bg=T.FONDO, fg=T.GRIS, anchor="w").pack(fill="x")
        tk.Label(caja, text=f"«{aviso.detalle['como_aparece']}»", font=T.F["seccion"], bg=T.FONDO, anchor="w").pack(fill="x")
        self.buscar = tk.StringVar()
        campo = T.Campo(self.cuerpo, self.buscar,
                        guia=f"Buscar entre las {len(instituciones)} instituciones de la matriz de convenios…")
        campo.pack(fill="x", pady=(14, 10))
        self.buscar.trace_add("write", lambda *a: self._listar())
        cab = tk.Frame(self.cuerpo, bg=T.BLANCO)
        cab.pack(fill="x")
        self.lbl_lista = tk.Label(cab, text="Sugeridas por el programa", font=T.F["cuerpo_b"], bg=T.BLANCO)
        self.lbl_lista.pack(side="left")
        tk.Label(cab, text="Ninguna viene elegida de antemano: tú decides.", font=T.F["pequena"], bg=T.BLANCO,
                 fg=T.GRIS).pack(side="right")
        self.opciones = tk.Frame(self.cuerpo, bg=T.BLANCO)
        self.opciones.pack(fill="x", pady=(8, 0))
        self.sugerencias = aviso.detalle.get("sugerencias", [])
        T.Franja(self.cuerpo, "aviso", "Revisa que sea la misma universidad: el parecido de nombres puede engañar "
                 "(por ejemplo, Montreal y Continental se parecen y no son la misma).").pack(fill="x", pady=(12, 8))
        T.Franja(self.cuerpo, "info", "Al guardar, el programa recuerda esta equivalencia (origen: Revisión) y la usa en "
                 "todos los archivos. Luego pulsa Recargar archivos para ver el efecto.").pack(fill="x")
        pie = self.botones()
        tk.Label(pie, text="¿No está en la lista? Agrégala a la matriz de convenios y recarga.", font=T.F["pequena"],
                 bg=T.BLANCO, fg=T.GRIS).pack(side="left")
        self.b_guardar = T.Boton(pie, "Guardar equivalencia", lambda: self.cerrar(self.elegida.get()), ancho=240)
        self.b_guardar.pack(side="right")
        T.Boton(pie, "Cancelar", lambda: self.cerrar(None), tipo="secundario", ancho=140).pack(side="right", padx=(0, 14))
        self.elegida.trace_add("write", lambda *a: self.b_guardar.activar(bool(self.elegida.get())))
        self.b_guardar.activar(False)
        self._listar()

    def _listar(self):
        for w in self.opciones.winfo_children():
            w.destroy()
        texto = normalizar(self.buscar.get())
        if texto:
            self.lbl_lista.configure(text="Resultados de la búsqueda")
            filas = [(n, None, False) for n, _ in self.instituciones if texto in normalizar(n)][:6]
            if not filas:
                tk.Label(self.opciones, text="Ninguna institución de la matriz contiene ese texto.", font=T.F["cuerpo"],
                         bg=T.BLANCO, fg=T.GRIS).pack(anchor="w", pady=8)
        else:
            self.lbl_lista.configure(text="Sugeridas por el programa")
            filas = [(s["institucion"], s["parecido"], s["muy_parecida"]) for s in self.sugerencias]
            if not filas:
                tk.Label(self.opciones, text="El programa no encontró ninguna parecida. Escribe arriba para buscar.",
                         font=T.F["cuerpo"], bg=T.BLANCO, fg=T.GRIS).pack(anchor="w", pady=8)
        for nombre, pct, muy in filas:
            self._opcion(nombre, pct, muy)

    def _opcion(self, nombre, pct, muy):
        elegida = self.elegida.get() == nombre
        borde = tk.Frame(self.opciones, bg=T.VERDE_CTA if elegida else T.LINEA, padx=2 if elegida else 1,
                         pady=2 if elegida else 1)
        borde.pack(fill="x", pady=(0, 8))
        fondo = T.TINTE_VERDE if elegida else T.BLANCO
        f = tk.Frame(borde, bg=fondo, padx=14, pady=8, cursor="hand2")
        f.pack(fill="both")
        rb = tk.Radiobutton(f, variable=self.elegida, value=nombre, bg=fondo, activebackground=fondo,
                            selectcolor=T.BLANCO, command=self._listar, tristatevalue="\x00")
        rb.pack(side="left")
        tx = tk.Frame(f, bg=fondo)
        tx.pack(side="left", fill="x", expand=True, padx=(8, 0))
        tk.Label(tx, text=nombre, font=T.F["cuerpo_b"], bg=fondo, anchor="w").pack(fill="x")
        n = self.cuenta.get(normalizar(nombre), 0)
        tk.Label(tx, text=f"{n} convenio{'s' if n != 1 else ''} en la matriz", font=T.F["pequena"], bg=fondo,
                 fg=T.GRIS, anchor="w").pack(fill="x")
        if pct is not None:
            tk.Label(f, text=f"{pct} %  ·  {'Muy parecida' if muy else 'Poco parecida'}", font=T.F["pequena_b"],
                     bg=fondo if muy else T.FONDO, fg=T.OK_TXT if muy else T.GRIS_OSC, padx=10, pady=3).pack(side="right")
        for w in (f, tx, *tx.winfo_children()):
            w.bind("<Button-1>", lambda e, v=nombre: (self.elegida.set(v), self._listar()))
