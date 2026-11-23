"""Normalización de textos para comparar nombres de columnas, instituciones y programas."""
import re
import unicodedata


def normalizar(valor) -> str:
    """Minúsculas, sin tildes, sin signos ni paréntesis y con un solo espacio entre palabras.

    >>> normalizar("  Institución de Origen/Destino (*) ")
    'institucion de origen destino'
    """
    if valor is None:
        return ""
    s = unicodedata.normalize("NFD", str(valor)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()
