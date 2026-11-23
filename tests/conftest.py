"""Juegos de archivos compartidos por las pruebas (ver tests/test_datos_reales.py)."""
import os
from pathlib import Path

import pytest

from muestra_sintetica import crear_muestra

ANONIMIZADOS = Path(__file__).parent / "datos" / "reales_anonimizados"
HAY_ANONIMIZADOS = any(ANONIMIZADOS.glob("*.xls*"))
ORIGINALES = os.environ.get("CUADRO_EXCEL_REALES")


@pytest.fixture(scope="module", params=["sintetica", "anonimizados", "originales"])
def carpeta(request, tmp_path_factory):
    """La misma prueba sobre la muestra inventada, las copias anonimizadas (si están) y los originales (si se indican)."""
    if request.param == "sintetica":
        d = tmp_path_factory.mktemp("muestra")
        crear_muestra(d)
        return d
    if request.param == "anonimizados":
        if not HAY_ANONIMIZADOS:
            pytest.skip("copias anonimizadas solo en el equipo local")
        return ANONIMIZADOS
    if not ORIGINALES:
        pytest.skip("CUADRO_EXCEL_REALES no está definida")
    return Path(ORIGINALES)


@pytest.fixture
def muestra(tmp_path):
    """Una muestra inventada nueva, para modificarla en la prueba."""
    crear_muestra(tmp_path)
    return tmp_path
