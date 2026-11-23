"""La configuración inicial frente a los Excel de entrada.

Cada prueba corre sobre tres juegos de archivos:

- **sintetica:** muestra inventada con las rarezas de los reales (tests/muestra_sintetica.py). Corre siempre.
- **anonimizados:** copias anonimizadas de los reales en tests/datos/reales_anonimizados. Solo existen en el equipo
  de quien las generó con tools/anonimizar_reales.py; no se suben al repositorio. Si no están, se saltan.
- **originales:** los Excel reales, si la variable de entorno CUADRO_EXCEL_REALES apunta a su carpeta.
"""
import os
import re
import warnings
import zipfile
from pathlib import Path

import openpyxl
import pytest

from cuadro_maestro.configuracion.valores_iniciales import configuracion_inicial
from cuadro_maestro.texto import normalizar

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

from muestra_sintetica import crear_muestra

ANONIMIZADOS = Path(__file__).parent / "datos" / "reales_anonimizados"
HAY_ANONIMIZADOS = any(ANONIMIZADOS.glob("*.xls*"))
ORIGINALES = os.environ.get("CUADRO_EXCEL_REALES")
solo_con_anonimizados = pytest.mark.skipif(not HAY_ANONIMIZADOS, reason="copias anonimizadas solo en el equipo local")


@pytest.fixture(scope="module", params=["sintetica", "anonimizados", "originales"])
def carpeta(request, tmp_path_factory):
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

PATRONES = {  # fuente -> (patrón del nombre de archivo, hoja con los datos, fila de encabezados esperada)
    "matriz": [("*MATRIZ*CONVENIOS*", "CONV_INTERNACIONALES", 3)],
    "movilidad": [("*MOVILIDAD*2022*", "BD GENERAL", 1)],
    "internacionalizacion_en_casa": [("*Internacionalizaci*2022-1*", None, 1), ("*Internacionalizaci*2022-2*", None, 2)],
}


def archivo(carpeta, patron):
    encontrados = sorted(carpeta.glob(patron))
    assert encontrados, f"No se encontró {patron} en {carpeta}"
    return encontrados[0]


def encabezados(ruta, hoja, fila):
    wb = openpyxl.load_workbook(ruta, read_only=True, data_only=True)
    ws = wb[hoja] if hoja else wb.worksheets[0]
    valores = next(ws.iter_rows(min_row=fila, max_row=fila, values_only=True))
    return [normalizar(v) for v in valores]


@pytest.fixture(scope="module")
def config():
    return configuracion_inicial()


def test_los_25_programas_tienen_su_columna_en_la_matriz(carpeta, config):
    hdr = set(encabezados(archivo(carpeta, "*MATRIZ*CONVENIOS*"), "CONV_INTERNACIONALES", 3))
    faltan = [p["columna_matriz"] for p in config["programas"] if normalizar(p["columna_matriz"]) not in hdr]
    assert faltan == []


@pytest.mark.parametrize("fuente", list(PATRONES))
def test_cada_dato_de_cada_fuente_se_reconoce_por_un_sinonimo(carpeta, fuente, config):
    f = next(x for x in config["fuentes"] if x["id"] == fuente)
    for patron, hoja, fila in PATRONES[fuente]:
        ruta = archivo(carpeta, patron)
        hdr = set(encabezados(ruta, hoja or f["hoja"]["preferida"], fila))
        sin_reconocer = [d for d, c in f["columnas"].items() if not hdr & set(c["sinonimos"])]
        assert sin_reconocer == [], f"{ruta.name}: {sin_reconocer}"


def test_los_nombres_de_archivo_coinciden_con_lo_que_busca_cada_fuente(carpeta, config):
    for f in config["fuentes"]:
        for patron, _, _ in PATRONES[f["id"]]:
            nombre = normalizar(archivo(carpeta, patron).name)
            assert all(t in nombre for t in f["archivo"]["contiene"]), (f["id"], nombre)
            if f["archivo"]["patron_anio"]:
                assert re.search(f["archivo"]["patron_anio"], archivo(carpeta, patron).name).group(1) == "2022"


# ---------------------------------------------------------------- muestra y copias: rarezas y limpieza
def test_la_muestra_sintetica_reproduce_las_rarezas(tmp_path):
    rutas = crear_muestra(tmp_path)
    ic2 = openpyxl.load_workbook(rutas["ic2"], data_only=True)
    ws = ic2.worksheets[0]
    assert ws["B1"].value.startswith("Tener en cuenta") and ws["B2"].value == "AÑO" and ws["A2"].value is None
    assert "UNIVERSIDAD INVENTADA" in [str(c.value).strip() for c in ws[2]]
    assert [s.title for s in ic2.worksheets if s.sheet_state == "hidden"] == ["LISTAS", "PROGRAMAS", "PAISES"]
    with zipfile.ZipFile(rutas["ic2"]) as z:
        assert b"macroEnabled" in z.read("[Content_Types].xml")
    matriz = openpyxl.load_workbook(rutas["matriz"], data_only=True)["CONV_INTERNACIONALES"]
    assert matriz["Q6"].value == "INDEFINIDO" and matriz["P8"].value == "SIN FECHA"


@solo_con_anonimizados
def test_las_copias_conservan_las_rarezas_de_los_reales():
    ic2 = openpyxl.load_workbook(archivo(ANONIMIZADOS, "*2022-2*"), data_only=True)
    ws = ic2.worksheets[0]
    assert ws["B1"].value.startswith("Tener en cuenta")          # nota en la fila 1; encabezado en la 2
    assert ws["B2"].value == "AÑO"                                # la primera columna es la B
    assert "UNIVERSIDAD METODISTA" in [str(c.value).strip() for c in ws[2]]   # encabezado sobrescrito
    assert [s.title for s in ic2.worksheets if s.sheet_state == "hidden"] == ["LISTAS", "PROGRAMAS", "PAISES"]
    matriz = openpyxl.load_workbook(archivo(ANONIMIZADOS, "*MATRIZ*"), read_only=True)
    assert "CATALOGOS" in matriz.sheetnames and "HOMOLOGACIONES" in matriz.sheetnames


@solo_con_anonimizados
def test_las_copias_no_traen_correos_reales_macros_ni_tablas_dinamicas():
    for ruta in ANONIMIZADOS.glob("*.xls*"):
        with zipfile.ZipFile(ruta) as z:
            partes = z.namelist()
            assert not [p for p in partes if re.search(r"vba|pivot|comments|media", p, re.I)], ruta.name
            contenido = b"".join(z.read(p) for p in partes)
        correos = {m for m in re.findall(rb"[\w.+-]+@[\w-]+\.[\w.]+", contenido) if b"ejemplo.org" not in m}
        assert correos == set(), ruta.name
