"""Material de marca para el .exe: cifrarlo para el repositorio público y descifrarlo al empaquetar.

El logotipo de Areandina, el logo del CNA y la tipografía Brown Std no se publican. Van cifrados en
`empaquetado/marca.cifrada` (AES con Fernet); la clave solo está en el secreto MARCA_CLAVE de GitHub y en el equipo de
quien mantiene el programa. Sin la clave el archivo no sirve para nada, y sin el material el .exe se arma igual (con
Segoe UI y sin el logo del CNA en el cuadro).

    python tools/marca.py cifrar [--clave-en archivo]    # assets/ -> empaquetado/marca.cifrada (clave nueva o MARCA_CLAVE)
    python tools/marca.py descifrar [--destino carpeta]  # empaquetado/marca.cifrada -> assets/ (clave en MARCA_CLAVE)
"""
import argparse
import io
import os
import sys
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

RAIZ = Path(__file__).resolve().parents[1]
ASSETS = RAIZ / "assets"
CIFRADO = RAIZ / "empaquetado" / "marca.cifrada"
ARCHIVOS = ["logo_cna.png", "marca/logotipo_verde.png", "marca/fuentes/BrownStd-Regular.otf",
            "marca/fuentes/BrownStd-Bold.otf", "marca/fuentes/BrownStd-Light.otf"]


def cifrar(destino_clave: Path | None) -> None:
    faltan = [a for a in ARCHIVOS if not (ASSETS / a).is_file()]
    if faltan:
        sys.exit("Faltan en assets/: " + ", ".join(faltan))
    clave = os.environ.get("MARCA_CLAVE", "").strip().encode() or Fernet.generate_key()
    memoria = io.BytesIO()
    with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as z:
        for a in ARCHIVOS:
            z.write(ASSETS / a, a)
    CIFRADO.parent.mkdir(exist_ok=True)
    CIFRADO.write_bytes(Fernet(clave).encrypt(memoria.getvalue()))
    if destino_clave:
        destino_clave.write_text(clave.decode() + "\n", encoding="utf-8")
        print(f"Clave guardada en {destino_clave} (no la subas al repositorio).")
    print(f"Cifrado: {CIFRADO.relative_to(RAIZ)} ({CIFRADO.stat().st_size:,} bytes, {len(ARCHIVOS)} archivos)")


def descifrar(destino: Path = ASSETS) -> bool:
    if not CIFRADO.is_file():
        print("::warning::No está empaquetado/marca.cifrada: el .exe se arma sin el material de marca.")
        return False
    clave = os.environ.get("MARCA_CLAVE", "").strip()
    if not clave:
        print("::warning::Sin el secreto MARCA_CLAVE: el .exe se arma sin el material de marca.")
        return False
    try:
        datos = Fernet(clave.encode()).decrypt(CIFRADO.read_bytes())
    except (InvalidToken, ValueError):
        sys.exit("La clave MARCA_CLAVE no abre empaquetado/marca.cifrada (¿se cifró con otra clave?).")
    with zipfile.ZipFile(io.BytesIO(datos)) as z:
        for a in z.namelist():
            if a not in ARCHIVOS:                   # solo lo de la lista conocida, nunca rutas raras
                continue
            ruta = destino / a
            ruta.parent.mkdir(parents=True, exist_ok=True)
            ruta.write_bytes(z.read(a))
    print(f"Material de marca listo en {destino} ({len(ARCHIVOS)} archivos).")
    return True


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("accion", choices=["cifrar", "descifrar"])
    p.add_argument("--clave-en", type=Path)
    p.add_argument("--destino", type=Path, default=ASSETS)
    a = p.parse_args()
    cifrar(a.clave_en) if a.accion == "cifrar" else descifrar(a.destino)
