"""`python -m cuadro_maestro` (o doble clic en el .exe) abre la ventana del programa.

`--comprobar archivo.json` no abre la ventana: escribe qué encontró (versión, material de marca, tipografía) y sale.
Lo usa GitHub Actions para comprobar que el .exe recién armado arranca.
"""
import sys

from cuadro_maestro.interfaz.app import comprobar, principal

if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--comprobar":
        sys.exit(comprobar(sys.argv[2]))
    principal()
