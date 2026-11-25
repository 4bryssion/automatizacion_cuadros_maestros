"""Lee todos los archivos de la vigencia: pasos 1 a 3 de la generación (matriz, movilidad, internacionalización en casa).

La lectura no depende del programa elegido: deja las filas tal como están, con su número de fila, y el cruce aplica
después los filtros (programa, sede, vacíos). Así la vista previa, la prueba de lectura y la generación leen igual.
Todos los errores se recogen y se devuelven juntos, para corregirlos de una vez (Hoja de errores, mockup 43).
"""
from __future__ import annotations

import warnings
from pathlib import Path
from typing import Callable

from . import archivos as A
from .encabezados import detectar_fila, elegir_hoja, mapear, mapear_programas
from .libro import NoSePudoAbrir, abrir
from .modelos import (COLUMNA_POR_CONFIRMAR, COLUMNA_SIN_IDENTIFICAR, FALTA_ARCHIVO, FALTA_MATRIZ, POR_CONFIRMAR,
                      PROGRAMA_NUEVO_EN_MATRIZ, PROGRAMA_SIN_COLUMNA, SIN_ENCABEZADOS, SIN_IDENTIFICAR, ArchivoLeido,
                      Aviso, Columna, ErrorLectura, Lectura, Registro)

ORDEN_FUENTES = ("matriz", "movilidad", "internacionalizacion_en_casa")
SEDE_POR_DEFECTO = "Pereira"


# Archivos ya leídos: si el archivo no cambió (misma fecha y tamaño) y su configuración tampoco, no se vuelve a abrir.
# Leer la matriz real tarda uno o dos segundos; la vista previa, Fuentes de datos, Campos, Gemini y la generación la
# leen una y otra vez. Se guardan pocas entradas (las más recientes).
_LEIDOS: dict = {}
MAX_LEIDOS = 48


def _clave(e, fuente, config, sede):
    import json
    try:
        st = e.ruta.stat()
    except OSError:
        return None
    extra = config["programas"] if fuente["id"] == "matriz" else None
    return (str(e.ruta), st.st_mtime_ns, st.st_size, e.anio, e.semestre, sede,
            json.dumps([fuente, extra], sort_keys=True, ensure_ascii=False, default=str))


def olvidar_leidos() -> None:
    _LEIDOS.clear()


class Cancelado(Exception):
    """La persona pulsó Cancelar: se detiene sin crear nada."""


def leer_carpeta(carpeta: Path, config: dict, anio_inicio: int, anio_fin: int, *,
                 al_avanzar: Callable[[str, Path], None] | None = None,
                 cancelado: Callable[[], bool] | None = None) -> Lectura:
    carpeta = Path(carpeta)
    esperados, avisos = A.buscar(carpeta, config, anio_inicio, anio_fin)
    fuentes = {f["id"]: f for f in config["fuentes"]}
    orden = [f for f in ORDEN_FUENTES if f in fuentes] + [f for f in fuentes if f not in ORDEN_FUENTES]
    esperados.sort(key=lambda e: (orden.index(e.fuente), e.anio or 0, e.semestre or 0))
    leidos: list[ArchivoLeido] = []
    errores: list[ErrorLectura] = []
    sede = (fuentes.get("movilidad", {}).get("filtros", {}) or {}).get("solo_sede") or SEDE_POR_DEFECTO

    for e in esperados:
        if cancelado and cancelado():
            raise Cancelado()
        if not e.encontrado:
            avisos.append(Aviso(FALTA_MATRIZ if e.fuente == "matriz" else FALTA_ARCHIVO, e.fuente, None, e.anio, e.semestre))
            continue
        if al_avanzar:
            al_avanzar(e.fuente, e.ruta)
        clave = _clave(e, fuentes[e.fuente], config, sede)
        if clave is not None and clave in _LEIDOS:
            leido, sus_avisos = _LEIDOS[clave]
            leidos.append(leido)
            avisos.extend(sus_avisos)
            continue
        try:
            libro = abrir(e.ruta)
        except NoSePudoAbrir as err:
            errores.append(ErrorLectura(e.ruta, e.fuente, e.anio, e.semestre, err.causa, err.detalle))
            continue
        try:
            with warnings.catch_warnings():
                # openpyxl avisa de fechas imposibles (las deja como error) y de extensiones que no soporta.
                warnings.simplefilter("ignore")
                propios: list = []
                leido = _leer_libro(libro, fuentes[e.fuente], e, config, sede, propios, cancelado)
                leidos.append(leido)
                avisos.extend(propios)
                if clave is not None:
                    if len(_LEIDOS) >= MAX_LEIDOS:
                        _LEIDOS.pop(next(iter(_LEIDOS)))
                    _LEIDOS[clave] = (leido, propios)
        except Cancelado:
            raise
        except Exception as err:  # noqa: BLE001 — un archivo raro por dentro es «dañado», nunca un cierre del programa
            errores.append(ErrorLectura(e.ruta, e.fuente, e.anio, e.semestre, "danado", f"{type(err).__name__}: {err}"))
        finally:
            libro.close()
    return Lectura(carpeta, anio_inicio, anio_fin, esperados, leidos, errores, avisos)


def _leer_libro(libro, fuente, esperado, config, sede, avisos, cancelado) -> ArchivoLeido:
    ws = elegir_hoja(libro, fuente)
    filas = list(ws.iter_rows(values_only=True))
    fila_hdr = detectar_fila(filas, fuente)
    base = dict(fuente=fuente["id"], ruta=esperado.ruta, anio=esperado.anio, semestre=esperado.semestre, hoja=ws.title)
    if not fila_hdr or fila_hdr > len(filas):
        avisos.append(Aviso(SIN_ENCABEZADOS, fuente["id"], esperado.ruta, esperado.anio, esperado.semestre))
        columnas = {d: Columna(d, SIN_IDENTIFICAR) for d in fuente["columnas"]}
        return ArchivoLeido(**base, fila_encabezados=0, columnas=columnas, registros=[])

    encabezados = filas[fila_hdr - 1]
    columnas = mapear(encabezados, fuente)
    for c in columnas.values():
        if c.estado in (POR_CONFIRMAR, SIN_IDENTIFICAR):
            tipo = COLUMNA_POR_CONFIRMAR if c.estado == POR_CONFIRMAR else COLUMNA_SIN_IDENTIFICAR
            avisos.append(Aviso(tipo, fuente["id"], esperado.ruta, esperado.anio, esperado.semestre, c.dato,
                                detalle={"encabezado": c.encabezado, "letra": c.letra, "puntaje": c.puntaje}))
    programas: dict[str, Columna] = {}
    if fuente["id"] == "matriz":
        programas, nuevas = mapear_programas(encabezados, config["programas"], sede)
        for nombre in nuevas:
            avisos.append(Aviso(PROGRAMA_NUEVO_EN_MATRIZ, "matriz", esperado.ruta, detalle={"encabezado": nombre}))
        for pid, c in programas.items():
            if c.estado != "exacta":
                avisos.append(Aviso(PROGRAMA_SIN_COLUMNA if c.estado == SIN_IDENTIFICAR else COLUMNA_POR_CONFIRMAR,
                                    "matriz", esperado.ruta, dato=f"programa:{pid}",
                                    detalle={"encabezado": c.encabezado, "letra": c.letra, "puntaje": c.puntaje}))

    indices = {d: c.indice for d, c in columnas.items() if c.indice is not None}
    ind_prog = {p: c.indice for p, c in programas.items() if c.indice is not None}
    registros = []
    for n, fila in enumerate(filas[fila_hdr:], start=fila_hdr + 1):
        if cancelado and n % 500 == 0 and cancelado():
            raise Cancelado()
        valores = {d: _celda(fila, j) for d, j in indices.items()}
        if all(_en_blanco(v) for v in valores.values()):
            continue
        if ind_prog:
            valores["programas"] = {p: _celda(fila, j) for p, j in ind_prog.items()}
        registros.append(Registro(n, valores))
    nombres = [str(h).strip() for h in encabezados if h is not None and str(h).strip()]
    return ArchivoLeido(**base, fila_encabezados=fila_hdr, columnas=columnas, registros=registros, programas=programas,
                        encabezados=nombres)


def _celda(fila, j):
    return fila[j] if j < len(fila) else None


def _en_blanco(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())
