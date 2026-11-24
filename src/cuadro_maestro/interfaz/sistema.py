"""Abrir archivos y carpetas con el programa del sistema (Excel, Explorador de archivos)."""
import os
import subprocess
import sys
from pathlib import Path


def abrir(ruta) -> bool:
    """Devuelve False si la ruta ya no existe (la ventana muestra entonces el aviso correspondiente)."""
    ruta = Path(ruta)
    if not ruta.exists():
        return False
    try:
        if sys.platform == "win32":
            os.startfile(str(ruta))   # noqa: S606 — abre con la aplicación asociada
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(ruta)])
        else:
            subprocess.Popen(["xdg-open", str(ruta)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False
