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
        raiz.protocol("WM_DELETE_WINDOW", self.cerrar)

    def guardar_estado(self):
        self.estados.guardar(self.estado)
        self.ventana._pintar_ultimo()

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
