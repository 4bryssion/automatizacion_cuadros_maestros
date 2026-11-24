"""Arranque del programa: fuentes, configuración (avisos 46 y 47), estado (aviso 48) y ventana principal."""
from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path

from ..configuracion import AlmacenConfiguracion
from ..configuracion import almacen as AC
from ..configuracion.rutas import carpeta_programa, carpeta_usuario
from ..estado import AlmacenEstado
from . import dialogos as D
from . import tema as T
from .modelo import cuando
from .ventana import VentanaPrincipal


def _fecha(iso: str | None) -> str:
    try:
        return cuando(datetime.fromisoformat(iso).astimezone().replace(tzinfo=None))
    except (TypeError, ValueError):
        return "fecha desconocida"


def cargar_configuracion(raiz, almacen: AlmacenConfiguracion) -> dict:
    r = almacen.cargar()
    if r.situacion == AC.RESTAURADA:
        detalle = [f"{'Carpeta del usuario' if e.lugar == AC.USUARIO else 'Junto al programa'}: "
                   f"{'se restauró' if e.restaurada else 'en uso'}" + (f" ({e.detalle})" if e.detalle else "")
                   for e in r.lugares]
        D.aviso(raiz, "Configuración restaurada", "info",
                "Una de las dos copias de la configuración faltaba o estaba dañada y se restauró desde la otra. "
                f"Se usó la guardada {_fecha(r.configuracion.get('guardado_en'))}. La copia dañada se guardó aparte.",
                [("Entendido", "ok", "primario")], detalle)
    elif r.situacion == AC.DISTINTAS:
        D.aviso(raiz, "Se usó la configuración más reciente", "info",
                "Las dos copias de la configuración eran distintas (por ejemplo, el programa se copió a otro equipo). "
                f"Se usó la más reciente, guardada {_fecha(r.configuracion.get('guardado_en'))}. La otra quedó como "
                "copia de seguridad.", [("Entendido", "ok", "primario")])
    elif r.situacion == AC.NO_ENCONTRADA:
        restaurables = [c for c in r.copias if c.restaurable]
        if restaurables:
            mas_reciente = restaurables[0]
            eleccion = D.aviso(raiz, "Configuración no encontrada", "aviso",
                               "No se pudo leer ninguna de las dos copias de la configuración. Mientras decides, el "
                               "programa usa la configuración inicial. Hay copias de seguridad:",
                               [("Restaurar la más reciente", "restaurar", "primario"),
                                ("Seguir con la inicial", "inicial", "secundario")],
                               [f"{_fecha(c.creada_en)} · {c.motivo.replace('_', ' ')}" for c in restaurables[:5]])
            if eleccion == "restaurar":
                return almacen.restaurar(mas_reciente)
        else:
            D.aviso(raiz, "Configuración no encontrada", "aviso",
                    "No se pudo leer la configuración y no hay copias de seguridad. Se cargó la configuración inicial.",
                    [("Entendido", "ok", "primario")])
        return almacen.seguir_con_la_inicial()
    return r.configuracion


class Aplicacion:
    """Une las dos pantallas (principal y revisión) y lo que comparten: configuración y estado."""

    def __init__(self, raiz, almacen, config, estados, estado):
        self.raiz, self.almacen, self.config, self.estados, self.estado = raiz, almacen, config, estados, estado
        self.ventana = VentanaPrincipal(raiz, almacen, config, estados, estado)
        self.ventana.al_abrir_revision = self.abrir_revision
        self.ventana.app = self
        self.revision = None
        self.pantalla_config = None
        self.ventana.b_config.comando = self.abrir_configuracion
        self.ventana.b_config.activar(True)
        self.ventana.b_previa.comando = self.abrir_vista_previa
        self.ventana.actualizar()
        raiz.protocol("WM_DELETE_WINDOW", self.cerrar)

    def guardar_estado(self):
        self.estados.guardar(self.estado)
        self.ventana._pintar_ultimo()

    def guardar_config(self, config=None, ya_guardada=False):
        """Guarda la configuración al instante (en los dos lugares). Si ya hay un cuadro generado y la configuración
        cambió desde entonces, el cuadro queda con cambios sin incluir (decisión 5 de flujo)."""
        from ..revision import elementos_cambiados
        self.config = self.almacen.actual if ya_guardada else self.almacen.guardar(config or self.config)
        self.ventana.config = self.config
        self.ventana.programas = {p["nombre"]: p["id"] for p in self.config["programas"]}
        self.ventana.cb_programa.configure(values=list(self.ventana.programas))
        u = self.estado.ultima
        if u:
            u.cambios_sin_incluir = bool(elementos_cambiados(u.config_firmas, self.config) or u.filas_cambian)
            self.guardar_estado()
        return self.config

    def carpeta_actual(self):
        """La carpeta de la ventana principal o, si no hay, la del último cuadro (para listar instituciones)."""
        from pathlib import Path
        for c in (self.ventana.v_carpeta.get(), self.estado.ultima.carpeta if self.estado.ultima else None):
            if c and Path(c).is_dir():
                return c
        return None

    def abrir_modal(self, clave, duena=None, al_cerrar=None, **opciones):
        """Abre un modal de Configuración encima de la pantalla actual (decisión 3 de flujo)."""
        from ..revision import instituciones_de_la_matriz
        from . import configuracion as C
        duena = duena or self.raiz
        if clave == "programas":
            C.ModalProgramas(self, duena).mostrar()
        elif clave == "eq_inst":
            carpeta = self.carpeta_actual()
            opciones = [n for n, _ in instituciones_de_la_matriz(carpeta, self.config)] if carpeta else []
            C.ModalEqInstituciones(self, duena, opciones).mostrar()
        elif clave == "eq_prog":
            C.ModalEqProgramas(self, duena, [p["nombre"] for p in self.config["programas"]]).mostrar()
        elif clave == "tipos":
            u = self.estado.ultima
            vistos = []
            for d in (u.avisos_actuales if u and u.avisos_actuales is not None else (u.avisos_lista if u else [])):
                if d["tipo"] == "tipo_persona_no_reconocido" and d["detalle"].get("valor") not in vistos:
                    vistos.append(d["detalle"]["valor"])
            C.ModalTipos(self, duena, vistos).mostrar()
        elif clave == "copias":
            C.ModalCopias(self, duena).mostrar()
        elif clave == "fuentes":
            from .fuentes import ModalFuentes
            ModalFuentes(self, duena, **opciones).mostrar()
        elif clave == "campos":
            from .campos import ModalCampos
            ModalCampos(self, duena).mostrar()
        elif clave == "gemini":
            from .gemini import ModalGemini
            hecho = ModalGemini(self, duena, **opciones).mostrar()
            if hecho:
                D.aviso(duena, "Guardado", "ok", f"Se guardaron {len(hecho)} sugerencias de Gemini: " + "; ".join(hecho)
                        + ".", [("Entendido", "ok", "primario")])
        elif clave == "exportar":
            from .intercambio import ModalIntercambio
            ModalIntercambio(self, duena).mostrar()
        elif clave == "reglas":
            from .reglas import ModalReglas
            ModalReglas(self, duena).mostrar()
        if al_cerrar:
            al_cerrar()
        if self.revision:
            self.revision._pintar_pie()

    def abrir_vista_previa(self):
        from .vista_previa import VistaPrevia
        v = self.ventana
        desde, hasta = v.anios_elegidos()
        vp = VistaPrevia(self, v.v_carpeta.get(), v.programa_id(), desde, hasta)
        v.uso_vista_previa = True
        if vp.mostrar() == "generar":
            v.generar()

    def abrir_configuracion(self):
        from .configuracion import PantallaConfiguracion
        self.ventana.pack_forget()
        self.raiz.title("Cuadro maestro internacional · Configuración")
        self.pantalla_config = PantallaConfiguracion(self, self.volver_de_configuracion)
        self.pantalla_config.pack(fill="both", expand=True)

    def volver_de_configuracion(self):
        self.pantalla_config.destroy()
        self.pantalla_config = None
        self.volver_a_principal()

    def abrir_revision(self):
        from .revision import PantallaRevision
        if not self.estado.ultima:
            return
        self.ventana.pack_forget()
        self.raiz.title("Cuadro maestro internacional · Revisión")
        self.revision = PantallaRevision(self, self.volver_a_principal)
        self.revision.pack(fill="both", expand=True)

    def volver_a_principal(self):
        if self.revision:
            self.revision.destroy()
            self.revision = None
        self.raiz.title("Cuadro maestro internacional")
        self.ventana.pack(fill="both", expand=True)
        self.ventana.config = self.config
        self.ventana.actualizar()

    def cerrar(self):
        """Con cambios sin incluir no se cierra sin generar (mockup 13); si la generación falla, sí."""
        from .revision import salir_con_cambios
        u = self.estado.ultima
        if u and u.cambios_sin_incluir:
            recarga = self.revision.recarga if self.revision else None
            if not salir_con_cambios(self, recarga, self.revision):
                return
        self.raiz.destroy()


def principal():
    raiz = tk.Tk()
    raiz.withdraw()
    raiz.title("Cuadro maestro internacional")
    raiz.configure(bg=T.BLANCO)
    T.cargar_fuentes(raiz)
    raiz.minsize(560, 560)
    raiz.geometry("1000x900")
    almacen = AlmacenConfiguracion(carpeta_usuario(), carpeta_programa())
    config = cargar_configuracion(raiz, almacen)
    estados = AlmacenEstado(carpeta_usuario(), carpeta_programa())
    estado = estados.cargar()
    raiz.deiconify()
    app = Aplicacion(raiz, almacen, config, estados, estado)
    if estado.carpeta and not Path(estado.carpeta).is_dir():
        raiz.after(300, lambda: _carpeta_perdida(app.ventana, estado.carpeta))
    elif estado.ultima and estado.ultima.cambios_sin_incluir:
        raiz.after(300, lambda: reapertura_con_cambios(app))
    raiz.mainloop()


def reapertura_con_cambios(app):
    """Mockup 36: el programa se cerró antes de incluir los cambios en un cuadro nuevo."""
    from .revision import generar_de_nuevo
    u = app.estado.ultima
    r = D.aviso(app.raiz, "Hay cambios sin incluir en el último cuadro", "aviso",
                f"La última vez el programa se cerró antes de que el cuadro nuevo de {u.programa} quedara generado (por "
                "un cierre inesperado o porque la generación falló). El cuadro guardado no tiene esas correcciones.",
                [("Generar cuadro de nuevo", "generar", "primario"), ("Ver revisión", "revision", "secundario"),
                 ("Cerrar", "cerrar", "enlace")])
    if r == "generar":
        generar_de_nuevo(app)
    elif r == "revision":
        app.abrir_revision()

def _carpeta_perdida(ventana: VentanaPrincipal, carpeta: str):
    while True:
        r = D.aviso(ventana.raiz, "No se encontró la carpeta de la vez pasada", "aviso",
                    f"La carpeta «{carpeta}» no existe o no se puede abrir: puede que el disco, la memoria USB o la "
                    "unidad de red estén desconectados, o que haya cambiado de nombre. El programa y la vigencia se "
                    "conservan. El último cuadro estaba en esa carpeta y no se podrá abrir hasta que vuelva.",
                    [("Elegir otra carpeta…", "elegir", "primario"), ("Reintentar", "reintentar", "secundario"),
                     ("Cerrar", "cerrar", "enlace")])
        if r == "elegir":
            ventana.elegir_carpeta()
            return
        if r == "reintentar" and not Path(carpeta).is_dir():
            continue
        ventana.actualizar()
        return
