"""Abrir un Excel sin dejarlo bloqueado y con una causa clara cuando no se puede."""
from __future__ import annotations

import io
import warnings
import zipfile
from pathlib import Path

import openpyxl

from .modelos import CON_CONTRASENA, DANADO, EN_USO

FIRMA_ZIP = b"PK\x03\x04"
FIRMA_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"          # contenedor de Office antiguo (.xls) o cifrado
MARCA_CIFRADO = "EncryptedPackage".encode("utf-16-le")   # flujo que tiene un .xlsx con contraseña


class NoSePudoAbrir(Exception):
    def __init__(self, causa: str, detalle: str = ""):
        super().__init__(detalle or causa)
        self.causa, self.detalle = causa, detalle


def leer_bytes(ruta: Path) -> bytes:
    """Lee el archivo completo de una vez: así no queda abierto mientras se procesa (en Windows bloquearía a Excel)."""
    try:
        return Path(ruta).read_bytes()
    except PermissionError as e:
        raise NoSePudoAbrir(EN_USO, str(e)) from e
    except OSError as e:
        # En Windows, un archivo bloqueado por otro proceso da a veces OSError con winerror 32 o 33.
        if getattr(e, "winerror", None) in (32, 33):
            raise NoSePudoAbrir(EN_USO, str(e)) from e
        raise NoSePudoAbrir(DANADO, str(e)) from e


def abrir(ruta: Path):
    """Devuelve el libro (solo lectura, valores en lugar de fórmulas) o lanza NoSePudoAbrir."""
    datos = leer_bytes(ruta)
    if datos.startswith(FIRMA_OLE):
        if MARCA_CIFRADO in datos:
            raise NoSePudoAbrir(CON_CONTRASENA)
        raise NoSePudoAbrir(DANADO, "Formato de Excel antiguo (.xls)")
    if not datos.startswith(FIRMA_ZIP):
        raise NoSePudoAbrir(DANADO, "No es un libro de Excel .xlsx")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")      # avisos de openpyxl sobre validaciones o extensiones no soportadas
            return openpyxl.load_workbook(io.BytesIO(datos), read_only=True, data_only=True)
    except (zipfile.BadZipFile, KeyError, ValueError, TypeError, OSError) as e:
        raise NoSePudoAbrir(DANADO, f"{type(e).__name__}: {e}") from e
    except Exception as e:   # noqa: BLE001 — cualquier otra rareza del archivo es "dañado", nunca un cierre del programa
        raise NoSePudoAbrir(DANADO, f"{type(e).__name__}: {e}") from e
