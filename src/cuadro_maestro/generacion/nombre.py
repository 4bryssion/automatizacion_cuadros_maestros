"""Nombre y carpeta del cuadro generado (docs/diseno_generacion.md)."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

CARPETA_SALIDA = "Cuadros generados"
_PROHIBIDOS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def vigencia_texto(anio_inicio: int, anio_fin: int) -> str:
    return str(anio_inicio) if anio_inicio == anio_fin else f"{anio_inicio}-{anio_fin}"


def nombre_cuadro(programa: str, anio_inicio: int, anio_fin: int, ahora: datetime) -> str:
    """`Cuadro maestro - Fisioterapia - 2019-2023 - 2026-11-23 1432.xlsx` (sin caracteres que Windows no acepta)."""
    limpio = " ".join(_PROHIBIDOS.sub(" ", programa).split()).rstrip(". ")
    return f"Cuadro maestro - {limpio} - {vigencia_texto(anio_inicio, anio_fin)} - {ahora:%Y-%m-%d %H%M}.xlsx"


def ruta_libre(carpeta: Path, nombre: str) -> Path:
    """Si ya existe un cuadro con ese nombre (mismo minuto), el siguiente lleva « (2)», « (3)»…; nunca se sobrescribe."""
    ruta = Path(carpeta) / nombre
    base, ext = ruta.stem, ruta.suffix
    n = 2
    while ruta.exists():
        ruta = ruta.with_name(f"{base} ({n}){ext}")
        n += 1
    return ruta
