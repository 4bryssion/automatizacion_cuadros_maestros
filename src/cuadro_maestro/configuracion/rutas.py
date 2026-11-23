"""Los dos lugares donde se guarda la configuración."""
import os
import sys
from pathlib import Path

NOMBRE_APLICACION = "Cuadro maestro internacional"
CARPETA_JUNTO_AL_PROGRAMA = "Configuración"


def carpeta_usuario() -> Path:
    """%APPDATA%\\Cuadro maestro internacional en Windows; ~/.local/share/… en otros sistemas (desarrollo)."""
    base = os.environ.get("APPDATA")
    if base:
        return Path(base) / NOMBRE_APLICACION
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / NOMBRE_APLICACION


def carpeta_programa() -> Path:
    """Carpeta «Configuración» junto al .exe portable (o junto al código fuente cuando no está empaquetado)."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parents[3]
    return base / CARPETA_JUNTO_AL_PROGRAMA
