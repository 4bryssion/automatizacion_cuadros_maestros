"""Archivos que acompañan al programa (logo del CNA), dentro del .exe o junto al código fuente.

El material de marca no se sube al repositorio público (carpeta `assets/`, en .gitignore). Si el logo no está,
el cuadro se genera igual, sin logo.
"""
import sys
from pathlib import Path


def carpeta_recursos() -> Path:
    base = getattr(sys, "_MEIPASS", None)          # carpeta temporal del .exe de PyInstaller
    return Path(base) / "assets" if base else Path(__file__).resolve().parents[2] / "assets"


def logo_cna() -> Path | None:
    for ext in (".png", ".jpg", ".jpeg"):
        ruta = carpeta_recursos() / f"logo_cna{ext}"
        if ruta.is_file():
            return ruta
    return None
