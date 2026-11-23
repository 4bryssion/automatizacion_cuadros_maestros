"""Busca en la carpeta los archivos que pide la vigencia y los asigna a cada fuente, año y semestre."""
from __future__ import annotations

import re
from pathlib import Path

from ..texto import normalizar
from .modelos import ABIERTO_EN_EXCEL, ARCHIVO_SIN_PERIODO, ARCHIVOS_REPETIDOS, Aviso, Esperado

EXTENSIONES = {".xlsx", ".xlsm", ".xls", ".xlsb"}   # .xls y .xlsb se encuentran, pero al abrirlos dan error claro


def reconocer(nombre: str, fuente: dict) -> bool:
    """El nombre contiene todos los textos de «contiene» y ninguna de las palabras de «excluye»."""
    regla = fuente["archivo"]
    n = normalizar(Path(nombre).stem)
    palabras = set(n.split())
    return all(normalizar(t) in n for t in regla.get("contiene", [])) and not any(
        normalizar(t) in palabras for t in regla.get("excluye", []))


def periodo(nombre: str, fuente: dict):
    regla = fuente["archivo"]
    anio = semestre = None
    if regla.get("patron_anio"):
        m = re.search(regla["patron_anio"], Path(nombre).stem)
        anio = int(m.group(1)) if m else None
    if regla.get("patron_semestre"):
        m = re.search(regla["patron_semestre"], Path(nombre).stem)
        semestre = int(m.group(1)) if m else None
    return anio, semestre


def candidatos(carpeta: Path) -> list[Path]:
    try:
        return sorted(p for p in Path(carpeta).iterdir()
                      if p.is_file() and p.suffix.lower() in EXTENSIONES and not p.name.startswith(("~$", ".")))
    except OSError:
        return []


def buscar(carpeta: Path, config: dict, anio_inicio: int, anio_fin: int) -> tuple[list[Esperado], list[Aviso]]:
    carpeta = Path(carpeta)
    archivos = candidatos(carpeta)
    esperados: list[Esperado] = []
    avisos: list[Aviso] = []
    for fuente in config["fuentes"]:
        regla = fuente["archivo"]
        por_semestre, por_anio = bool(regla.get("patron_semestre")), bool(regla.get("patron_anio"))
        huecos: dict[tuple, Esperado] = {}
        if por_semestre:
            for a in range(anio_inicio, anio_fin + 1):
                for s in (1, 2):
                    huecos[(a, s)] = Esperado(fuente["id"], a, s)
        elif por_anio:
            for a in range(anio_inicio, anio_fin + 1):
                huecos[(a, None)] = Esperado(fuente["id"], a)
        else:
            huecos[(None, None)] = Esperado(fuente["id"])
        for ruta in archivos:
            if not reconocer(ruta.name, fuente):
                continue
            anio, semestre = periodo(ruta.name, fuente)
            clave = (anio if por_anio or por_semestre else None, semestre if por_semestre else None)
            if (por_anio or por_semestre) and anio is None or por_semestre and semestre is None:
                if anio is None or anio_inicio <= anio <= anio_fin:
                    avisos.append(Aviso(ARCHIVO_SIN_PERIODO, fuente["id"], ruta, anio))
                continue
            if clave in huecos:
                huecos[clave].otros.append(ruta)
        for e in huecos.values():
            if not e.otros:
                continue
            # Si hay varios para el mismo hueco se usa el modificado más recientemente y se avisa.
            e.otros.sort(key=_modificado, reverse=True)
            e.ruta, e.otros = e.otros[0], e.otros[1:]
            if e.otros:
                avisos.append(Aviso(ARCHIVOS_REPETIDOS, e.fuente, e.ruta, e.anio, e.semestre,
                                    detalle={"descartados": [p.name for p in e.otros]}))
            if (carpeta / f"~${e.ruta.name}").exists():
                avisos.append(Aviso(ABIERTO_EN_EXCEL, e.fuente, e.ruta, e.anio, e.semestre))
        esperados.extend(huecos.values())
    return esperados, avisos


def _modificado(ruta: Path) -> float:
    try:
        return ruta.stat().st_mtime
    except OSError:
        return 0.0
