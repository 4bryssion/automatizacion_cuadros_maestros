"""Hoja, fila de encabezados y columna de cada dato, sin posiciones fijas.

Solo lo exacto (tras normalizar) se aplica solo. Lo parecido queda «por confirmar» con su sugerencia, y lo que no se
parece a nada queda «sin identificar»: así lo pide el diseño (lo dudoso nunca se aplica sin que alguien lo confirme).
"""
from __future__ import annotations

import difflib

from ..texto import normalizar
from .modelos import EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR, Columna

FILAS_A_REVISAR = 15
UMBRAL_COLUMNA = 0.75
UMBRAL_PROGRAMA = 0.85


def similitud(encabezado: str, sinonimo: str) -> float:
    if not encabezado or not sinonimo:
        return 0.0
    if encabezado == sinonimo:
        return 1.0
    if len(sinonimo) > 5 and len(encabezado) > 5 and (encabezado.startswith(sinonimo) or sinonimo.startswith(encabezado)):
        return 0.95
    if len(sinonimo) > 5 and sinonimo in encabezado:
        return 0.9
    return difflib.SequenceMatcher(None, encabezado, sinonimo).ratio()


def _sinonimos(col: dict) -> list[str]:
    s = [normalizar(x) for x in col.get("sinonimos", [])]
    if col.get("elegida"):
        s.insert(0, normalizar(col["elegida"]))
    return s


def puntaje_fila(valores, fuente: dict) -> int:
    normal = {normalizar(v) for v in valores if isinstance(v, str)}
    return sum(1 for col in fuente["columnas"].values() if normal & set(_sinonimos(col)))


def detectar_fila(filas: list[tuple], fuente: dict) -> int | None:
    """Número de fila (1 = primera) con más datos reconocidos; None si ninguna reconoce alguno."""
    conf = fuente.get("fila_encabezado", {})
    if not conf.get("automatica", True):
        return conf.get("fila")
    mejor, fila = 0, None
    for i, valores in enumerate(filas[:FILAS_A_REVISAR], start=1):
        p = puntaje_fila(valores, fuente)
        if p > mejor:
            mejor, fila = p, i
    return fila


def elegir_hoja(libro, fuente: dict):
    """La hoja preferida si existe; si no, la hoja visible cuyos encabezados reconocen más datos."""
    preferida = normalizar((fuente.get("hoja") or {}).get("preferida") or "")
    hojas = libro.worksheets
    if preferida:
        for ws in hojas:
            if normalizar(ws.title) == preferida:
                return ws
    visibles = [ws for ws in hojas if getattr(ws, "sheet_state", "visible") == "visible"] or hojas

    def puntaje(ws):
        filas = list(ws.iter_rows(min_row=1, max_row=FILAS_A_REVISAR, values_only=True))
        return max((puntaje_fila(f, fuente) for f in filas), default=0)

    return max(visibles, key=puntaje)   # max devuelve la primera en caso de empate


def mapear(encabezados: tuple, fuente: dict) -> dict[str, Columna]:
    normales = [normalizar(h) if h is not None else "" for h in encabezados]
    tomadas: set[int] = set()
    resultado: dict[str, Columna] = {}
    # 1) exactas (incluida la columna que la persona eligió)
    for dato, col in fuente["columnas"].items():
        for s in _sinonimos(col):
            j = next((j for j, h in enumerate(normales) if h == s and j not in tomadas), None)
            if j is not None:
                resultado[dato] = Columna(dato, EXACTA, j, str(encabezados[j]).strip(), 1.0)
                tomadas.add(j)
                break
    # 2) parecidas: se proponen, de la más parecida a la menos, sin repetir columna
    propuestas = []
    for dato, col in fuente["columnas"].items():
        if dato in resultado:
            continue
        for j, h in enumerate(normales):
            if j in tomadas or not h:
                continue
            p = max((similitud(h, s) for s in _sinonimos(col)), default=0)
            if p >= UMBRAL_COLUMNA:
                propuestas.append((p, dato, j))
    for p, dato, j in sorted(propuestas, key=lambda x: (-x[0], x[2])):
        if dato in resultado or j in tomadas:
            continue
        resultado[dato] = Columna(dato, POR_CONFIRMAR, j, str(encabezados[j]).strip(), round(p, 2))
        tomadas.add(j)
    for dato in fuente["columnas"]:
        resultado.setdefault(dato, Columna(dato, SIN_IDENTIFICAR))
    return {d: resultado[d] for d in fuente["columnas"]}


def mapear_programas(encabezados: tuple, programas: list[dict], sede: str):
    """Columna de cada programa en la matriz, y columnas de la sede que no son de ningún programa configurado."""
    normales = [normalizar(h) if h is not None else "" for h in encabezados]
    sufijo = " " + normalizar(sede)
    de_la_sede = {j for j, h in enumerate(normales) if h.endswith(sufijo)}
    tomadas: set[int] = set()
    resultado: dict[str, Columna] = {}
    for p in programas:
        objetivo = normalizar(p["columna_matriz"])
        j = next((j for j, h in enumerate(normales) if h == objetivo and j not in tomadas), None)
        if j is not None:
            resultado[p["id"]] = Columna(p["id"], EXACTA, j, str(encabezados[j]).strip(), 1.0)
            tomadas.add(j)
    for p in programas:
        if p["id"] in resultado:
            continue
        objetivo = normalizar(p["columna_matriz"])
        opciones = [(difflib.SequenceMatcher(None, normales[j], objetivo).ratio(), j) for j in de_la_sede - tomadas]
        mejor = max(opciones, default=(0, None))
        if mejor[0] >= UMBRAL_PROGRAMA:
            j = mejor[1]
            resultado[p["id"]] = Columna(p["id"], POR_CONFIRMAR, j, str(encabezados[j]).strip(), round(mejor[0], 2))
            tomadas.add(j)
        else:
            resultado[p["id"]] = Columna(p["id"], SIN_IDENTIFICAR)
    nuevas = [str(encabezados[j]).strip() for j in sorted(de_la_sede - tomadas)]
    return resultado, nuevas
