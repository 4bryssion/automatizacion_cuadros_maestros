"""Conversión tolerante de los valores que llegan de los Excel.

Los reales traen años como 2022, 2022.0 o "2022"; fechas como fecha, como texto ("20/05/2022") o mal escritas
("20/05/222"); vacíos como "", "N/A", "NA". Estas funciones devuelven None cuando el valor no sirve, para que quien
las usa decida si eso es un aviso.
"""
import re
from datetime import date, datetime

from ..texto import normalizar

VACIOS_POR_DEFECTO = frozenset({"", "n a", "na", "no aplica", "ninguna", "ninguno", "none", "null", "sin informacion"})


def es_vacio(valor, vacios=VACIOS_POR_DEFECTO) -> bool:
    return valor is None or normalizar(valor) in vacios


def a_entero(valor):
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        return int(valor) if valor.is_integer() else None
    if isinstance(valor, str):
        t = valor.strip().replace(",", ".")
        try:
            f = float(t)
        except ValueError:
            return None
        return int(f) if f.is_integer() else None
    return None


def a_anio(valor):
    """Año de cuatro cifras entre 1990 y 2100, desde número, texto o fecha."""
    if isinstance(valor, (datetime, date)):
        return valor.year
    n = a_entero(valor)
    if n is None and isinstance(valor, str):
        m = re.fullmatch(r"\s*((?:19|20)\d{2})\s*", valor)
        n = int(m.group(1)) if m else None
    return n if n is not None and 1990 <= n <= 2100 else None


def a_semestre(valor):
    n = a_entero(valor)
    if n in (1, 2):
        return n
    if isinstance(valor, str):
        m = re.search(r"\b([12])\b", valor)
        return int(m.group(1)) if m else None
    return None


def a_fecha(valor):
    """Fecha desde fecha de Excel o texto dd/mm/aaaa, dd-mm-aaaa o aaaa-mm-dd. Lo demás, None."""
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if not isinstance(valor, str):
        return None
    t = valor.strip()
    for patron, orden in ((r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", "dma"), (r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", "amd")):
        m = re.fullmatch(patron, t)
        if m:
            a, b, c = (int(x) for x in m.groups())
            d, mes, anio = (a, b, c) if orden == "dma" else (c, b, a)
            try:
                return date(anio, mes, d)
            except ValueError:
                return None
    return None


def separar_lista(valor) -> list[str]:
    """Una celda con varios valores separados por saltos de línea (p. ej. varios programas)."""
    if valor is None:
        return []
    return [p.strip() for p in str(valor).splitlines() if p.strip()]
