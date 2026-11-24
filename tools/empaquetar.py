"""Arma el .exe portable de Windows con PyInstaller (un solo archivo, sin consola).

    python tools/empaquetar.py

Si `assets/` tiene el material de marca (ver tools/marca.py), lo incluye y crea el icono a partir de la «A» del
logotipo. Si no, arma el .exe igual (Segoe UI, sin logo del CNA). El resultado queda en `dist/`.
"""
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from cuadro_maestro import __version__  # noqa: E402

NOMBRE = "Cuadro maestro internacional"
ASSETS = RAIZ / "assets"
TRABAJO = RAIZ / "build" / "empaquetado"


def icono() -> Path | None:
    """La primera «A» del logotipo, centrada en un cuadrado blanco: se reconoce en la barra de tareas."""
    logo = ASSETS / "marca" / "logotipo_verde.png"
    if not logo.is_file():
        return None
    from PIL import Image
    img = Image.open(logo).convert("RGBA")
    w, h = img.size
    # La «A» ocupa ~ del 10,7 % al 19,6 % del ancho y del 34 % al 54,5 % del alto (logotipo de 2806 × 1627).
    a = img.crop((round(w * 0.105), round(h * 0.335), round(w * 0.198), round(h * 0.548)))
    lado = round(max(a.size) * 1.3)
    fondo = Image.new("RGBA", (lado, lado), (255, 255, 255, 255))
    fondo.alpha_composite(a, ((lado - a.width) // 2, (lado - a.height) // 2))
    ico, png = ASSETS / "icono.ico", ASSETS / "icono.png"
    fondo.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    fondo.resize((128, 128), Image.LANCZOS).save(png)
    return ico


def version_windows() -> Path:
    """Propiedades del archivo en Windows (clic derecho › Propiedades › Detalles)."""
    n = [int(x) for x in __version__.split(".")] + [0] * 4
    tupla = tuple(n[:4])
    texto = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={tupla}, prodvers={tupla}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1,
                    subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040A04B0', [
      StringStruct('CompanyName', 'Fundación Universitaria del Área Andina'),
      StringStruct('FileDescription', '{NOMBRE}'),
      StringStruct('FileVersion', '{__version__}'),
      StringStruct('InternalName', '{NOMBRE}'),
      StringStruct('OriginalFilename', '{NOMBRE}.exe'),
      StringStruct('ProductName', '{NOMBRE}'),
      StringStruct('ProductVersion', '{__version__}'),
      StringStruct('LegalCopyright', 'Oficina de Relaciones Internacionales, sede Pereira')])]),
        VarFileInfo([VarStruct('Translation', [0x040A, 1200])])]
)
"""
    TRABAJO.mkdir(parents=True, exist_ok=True)
    ruta = TRABAJO / "version.txt"
    ruta.write_text(texto, encoding="utf-8")
    return ruta


def main() -> int:
    marca = (ASSETS / "marca" / "logotipo_verde.png").is_file()
    ico = icono() if marca else None
    args = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", NOMBRE, "--paths", str(RAIZ / "src"), "--workpath", str(TRABAJO / "pyinstaller"),
            "--specpath", str(TRABAJO), "--distpath", str(RAIZ / "dist"),
            "--version-file", str(version_windows()),
            "--exclude-module", "pytest", "--exclude-module", "cryptography"]
    if ASSETS.is_dir() and any(ASSETS.iterdir()):
        args += ["--add-data", f"{ASSETS}{';' if sys.platform == 'win32' else ':'}assets"]
    if ico:
        args += ["--icon", str(ico)]
    args.append(str(RAIZ / "src" / "cuadro_maestro" / "__main__.py"))
    print("Material de marca:", "incluido" if marca else "NO incluido (Segoe UI, sin logo del CNA)")
    r = subprocess.run(args, cwd=RAIZ)
    if r.returncode == 0:
        exe = RAIZ / "dist" / (NOMBRE + (".exe" if sys.platform == "win32" else ""))
        print(f"Listo: {exe} ({exe.stat().st_size / 1e6:.1f} MB)")
    shutil.rmtree(TRABAJO / "pyinstaller", ignore_errors=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
