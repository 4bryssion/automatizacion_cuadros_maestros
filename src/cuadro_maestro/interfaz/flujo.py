"""Generar el cuadro desde cualquier pantalla: confirmar, progreso, hoja de errores y guardar la última generación."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .. import __version__
from ..cruce.modelos import EXCEL, INFORMATIVO, PROGRAMA
from ..estado import UltimaGeneracion
from ..revision import aviso_a_dict, firmas_config, firmas_filas
from . import dialogos as D
from .modelo import cuando, resumir, vigencia


OK, CANCELADO, FALLO = "ok", "cancelado", "fallo"


def generar(raiz, almacen, config, carpeta, programa_id, desde, hasta, uso_vista_previa=False):
    """Devuelve (OK, Generacion), (CANCELADO, None) o (FALLO, None). Pasa siempre por la alerta de confirmación.

    FALLO es una generación que se detuvo o terminó con error: con cambios sin incluir, eso deja salir (el estado
    pendiente queda guardado para la próxima apertura). CANCELADO no deja salir.
    """
    programa = next(p for p in config["programas"] if p["id"] == programa_id)
    r = resumir(carpeta, config, desde, hasta)
    guardado = datetime.fromisoformat(almacen.actual["guardado_en"]).astimezone().replace(tzinfo=None) \
        if almacen.actual else datetime.now()
    if not D.confirmar_generacion(raiz, programa["nombre"], desde, hasta, r.encontrados, r.esperados, r.faltan,
                                  cuando(guardado), uso_vista_previa):
        return CANCELADO, None
    parametros = dict(carpeta=Path(carpeta), config=config, programa_id=programa_id, anio_inicio=desde, anio_fin=hasta)
    chips = [f"Programa: {programa['nombre']}", f"Vigencia: {vigencia(desde, hasta)}", f"{r.esperados + 1} archivos"]
    while True:
        salida = D.Progreso(raiz, parametros, chips).mostrar()
        tipo = salida[0] if salida else "cancelado"
        if tipo == "fin":
            return OK, salida[1]
        if tipo == "cancelado":
            return CANCELADO, None
        if tipo == "detenida":
            ctx = {"Programa": programa["nombre"], "Vigencia": vigencia(desde, hasta, "-"), "Carpeta": str(carpeta),
                   "Versión del programa": __version__}
            if D.generacion_detenida(raiz, salida[1], ctx) == "reintentar":
                continue
            return FALLO, None
        if tipo == "fallo":
            D.aviso(raiz, "Ocurrió un error inesperado", "error",
                    "La generación no terminó y no se creó ningún archivo. Copia este detalle y envíalo a Sistemas.",
                    [("Cerrar", "cerrar", "primario")], [f"{type(salida[1]).__name__}: {salida[1]}"])
        return FALLO, None


def ultima_generacion(g, config) -> UltimaGeneracion:
    r = g.resultado
    grupos = r.por_grupo()
    por_anio = [e for e in g.lectura.esperados if e.fuente != "matriz"]
    return UltimaGeneracion(
        r.programa["id"], r.programa["nombre"], r.anio_inicio, r.anio_fin, str(g.lectura.carpeta), str(g.ruta),
        g.ahora.isoformat(), {EXCEL: len(grupos[EXCEL]), PROGRAMA: len(grupos[PROGRAMA]),
                              INFORMATIVO: len(grupos[INFORMATIVO])},
        False, [aviso_a_dict(a) for a in r.avisos], None, firmas_filas(r, config), firmas_config(config), 0,
        sum(e.encontrado for e in por_anio), len(por_anio), g.ahora.isoformat())
