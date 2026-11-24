"""Escribe el cuadro maestro con el formato del cuadro hecho a mano (CNA, cuadro No. 10).

Hoja «Convenios»: títulos del CNA (filas 1 a 3), sección de convenios nacionales vacía con sus filas de ejemplo
(P13) y la sección internacional desde la fila 16. Century Gothic 10, celdas centradas con ajuste de texto, marco
exterior grueso y líneas finas por dentro. Las columnas salen de Configuración › Campos del cuadro maestro.
Hoja «Acerca de este cuadro»: programa, vigencia, fecha, matriz usada (nombre y fecha), archivos leídos y cifras. Ninguna de las dos tiene datos de personas.
"""
from __future__ import annotations

import math
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side
from openpyxl.utils import get_column_letter

from .. import __version__
from ..cruce import texto_resultados
from ..cruce.modelos import EXCEL, INFORMATIVO, PROGRAMA, ResultadoCruce
from .nombre import CARPETA_SALIDA, nombre_cuadro, ruta_libre, vigencia_texto

FUENTE = "Century Gothic"
TITULOS = ("CONSEJO NACIONAL DE ACREDITACIÓN", "PROCESO DE ACREDITACIÓN DE PROGRAMAS ACADÉMICOS",
           "CUADRO No. 10. CONVENIOS Y ALIANZAS ESTRATÉGICAS DEL PROGRAMA")
TITULO_NACIONALES = "CONVENIOS ACTIVOS NACIONALES DE COOPERACIÓN"
TITULO_INTERNACIONALES = "CONVENIOS INTERNACIONALES DE COOPERACIÓN"
FILAS_EJEMPLO_NACIONALES = ("1", "2", "3", "4", ".", ".", "N")
FILA_TITULO_INTERNACIONALES = 16
ALTO_LINEA = 12.5
LOGO_TAMANO = (230, 84)              # cabe en las filas 1 a 4 (63 puntos); el original es 268 × 98 y se monta sobre la 5

FINA, GRUESA = Side(style="thin"), Side(style="medium")
CENTRO = Alignment(horizontal="center", vertical="center", wrap_text=True)
NORMAL, NEGRITA = Font(name=FUENTE, size=10), Font(name=FUENTE, size=10, bold=True)


class Cancelado(Exception):
    """La persona canceló mientras se escribía: no queda ningún archivo."""


class ErrorEscritura(Exception):
    def __init__(self, carpeta: Path, causa: str, detalle: str = ""):
        super().__init__(detalle or causa)
        self.carpeta, self.causa, self.detalle = carpeta, causa, detalle


# ---------------------------------------------------------------- contenido de cada celda
def valor_campo(campo: dict, fila, config: dict):
    c = fila.convenio
    if campo["fuente"] == "vacio":
        return None
    if campo["fuente"] == "calculado":
        r5 = config["reglas"]["r5_activo"]
        return {"numeracion": fila.numero,
                "resultados": texto_resultados(fila, config["tipos_persona"]),
                "activo": r5["etiqueta_activo"] if c.activo else r5["etiqueta_no_activo"]}.get(campo.get("dato"))
    if campo["fuente"] == "matriz":
        dato = campo.get("dato")
        especiales = {"institucion": c.institucion, "objeto": c.objeto, "vigencia_anios": c.vigencia_anios}
        valor = especiales[dato] if dato in especiales else c.datos.get(dato)
        return valor.strip() if isinstance(valor, str) else valor
    return None          # «reportes»: por definir qué dato de los reportes iría en una columna propia


def _formato(campo: dict) -> str:
    return {"numero": "0", "texto": "@", "texto_calculado": "@", "opciones": "@", "fecha": "DD/MM/YYYY"}.get(
        campo["tipo"], "General")


def _alto(valores, anchos) -> float:
    """Alto de fila aproximado: 12,5 puntos por línea (medido en el cuadro real). Se calculan 0,85 letras por unidad
    de ancho (en el real son 0,93) para dejar margen si el equipo no tiene Century Gothic y usa una letra más ancha."""
    lineas = 1
    for v, ancho in zip(valores, anchos):
        if v is None:
            continue
        por_linea = max(1, int(ancho * 0.85))
        lineas = max(lineas, sum(max(1, math.ceil(len(t) / por_linea)) for t in str(v).split("\n")))
    return max(13.5, round(ALTO_LINEA * lineas + 0.5, 1))


# ---------------------------------------------------------------- libro
def construir_libro(resultado: ResultadoCruce, config: dict, ahora: datetime, carpeta_excel: Path,
                    logo: Path | None = None, matriz: Path | None = None) -> Workbook:
    campos = config["campos"]
    n = len(campos)
    ultima = get_column_letter(n)
    anchos = [c.get("ancho") or 15 for c in campos]
    wb = Workbook()
    ws = wb.active
    ws.title = "Convenios"
    for j, w in enumerate(anchos, start=1):
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 70
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    for i, t in enumerate(TITULOS, start=1):
        _titulo(ws, i, t, ultima, caja=False)
    for fila, alto in ((1, 16.5), (2, 16.5), (3, 13.5), (4, 16.5)):
        ws.row_dimensions[fila].height = alto

    # Convenios nacionales: vacía, con las filas de ejemplo del cuadro original (P13).
    _titulo(ws, 5, TITULO_NACIONALES, ultima, caja=True)
    _encabezados(ws, 6, campos)
    filas_nac = [[e] + [None] * (n - 1) for e in FILAS_EJEMPLO_NACIONALES]
    _tabla(ws, 7, filas_nac, campos, altos=[13.5] * len(filas_nac))
    ws.row_dimensions[14].height = ws.row_dimensions[15].height = 15

    # Convenios internacionales
    r0 = FILA_TITULO_INTERNACIONALES
    _titulo(ws, r0, TITULO_INTERNACIONALES, ultima, caja=True)
    _encabezados(ws, r0 + 1, campos)
    datos = [[valor_campo(c, f, config) for c in campos] for f in resultado.filas]
    _tabla(ws, r0 + 2, datos, campos, altos=[_alto(fila, anchos) for fila in datos])

    if logo and Path(logo).is_file():
        try:
            from openpyxl.drawing.image import Image
            img = Image(str(logo))
            img.width, img.height = LOGO_TAMANO
            ws.add_image(img, "B1")
        except Exception:   # noqa: BLE001 — sin logo el cuadro sigue siendo válido
            pass

    _hoja_acerca(wb.create_sheet("Acerca de este cuadro"), resultado, ahora, carpeta_excel, matriz)
    wb.properties.creator = "Cuadro maestro internacional"
    wb.properties.title = f"Cuadro maestro - {resultado.programa['nombre']}"
    return wb


def _titulo(ws, fila, texto, ultima, caja):
    ws.merge_cells(f"A{fila}:{ultima}{fila}")
    c = ws[f"A{fila}"]
    c.value, c.font, c.alignment, c.number_format = texto, NEGRITA, CENTRO, "@"
    if caja:
        n = ws[f"{ultima}{fila}"].column
        for celda in ws[f"A{fila}:{ultima}{fila}"][0]:
            celda.border = Border(top=GRUESA, bottom=GRUESA, left=GRUESA if celda.column == 1 else None,
                                  right=GRUESA if celda.column == n else None)
    ws.row_dimensions[fila].height = 17.25 if caja else ws.row_dimensions[fila].height


def _encabezados(ws, fila, campos):
    n = len(campos)
    for j, campo in enumerate(campos, start=1):
        c = ws.cell(fila, j, campo["nombre"])
        c.font, c.alignment, c.number_format = NEGRITA, CENTRO, "@"
        c.border = Border(left=GRUESA if j == 1 else FINA, right=GRUESA if j == n else FINA, bottom=FINA)
    ws.row_dimensions[fila].height = max(25.5, _alto([c["nombre"] for c in campos], [c.get("ancho") or 15 for c in campos]))


def _tabla(ws, fila0, filas, campos, altos):
    n = len(campos)
    for i, valores in enumerate(filas):
        r = fila0 + i
        ultima_fila = i == len(filas) - 1
        for j, (v, campo) in enumerate(zip(valores, campos), start=1):
            c = ws.cell(r, j, v)
            c.font, c.alignment = NORMAL, CENTRO
            c.number_format = "General" if campo.get("dato") == "numeracion" else _formato(campo)
            c.border = Border(left=GRUESA if j == 1 else FINA, right=GRUESA if j == n else FINA, top=FINA,
                              bottom=GRUESA if ultima_fila else FINA)
        ws.row_dimensions[r].height = altos[i]


def fecha_modificacion(ruta: Path | None) -> datetime | None:
    try:
        return datetime.fromtimestamp(Path(ruta).stat().st_mtime) if ruta else None
    except OSError:
        return None


def _hoja_acerca(ws, r: ResultadoCruce, ahora: datetime, carpeta_excel: Path, matriz: Path | None = None):
    grupos = r.por_grupo()
    modificada = fecha_modificacion(matriz)
    filas = [
        ("Programa", r.programa["nombre"]),
        ("Sede", "Pereira"),
        ("Vigencia", vigencia_texto(r.anio_inicio, r.anio_fin)),
        ("Generado el", f"{ahora:%d/%m/%Y %H:%M}"),
        ("Carpeta de los Excel", str(carpeta_excel)),
        ("Matriz de convenios usada", matriz.name if matriz else "—"),
        ("Matriz modificada el", f"{modificada:%d/%m/%Y %H:%M}" if modificada else "—"),
        ("Archivos leídos", r.archivos_leidos),
        ("Convenios en el cuadro", r.convenios_en_cuadro),
        ("Movilidades contadas", r.movilidades_contadas),
        ("Actividades de internacionalización en casa contadas", r.actividades_contadas),
        ("Actividades sin institución omitidas", r.actividades_sin_institucion),
        ("Avisos para corregir en el Excel", len(grupos[EXCEL])),
        ("Avisos para resolver en el programa", len(grupos[PROGRAMA])),
        ("Avisos informativos", len(grupos[INFORMATIVO])),
        ("Versión del programa", __version__),
    ]
    ws.column_dimensions["A"].width, ws.column_dimensions["B"].width = 52, 70
    ws["A1"], ws["A1"].font = "Acerca de este cuadro", Font(name=FUENTE, size=12, bold=True)
    for i, (k, v) in enumerate(filas, start=3):
        ws.cell(i, 1, k).font = NEGRITA
        ws.cell(i, 2, v).font = NORMAL
        ws.cell(i, 2).alignment = Alignment(horizontal="left", wrap_text=True)
    nota = len(filas) + 4
    ws.cell(nota, 1, "Generado por el programa «Cuadro maestro internacional». Las columnas «Nº de usuarios» y "
                     "«No Aplica» las llena cada programa (P12). El detalle de los avisos está en Ver revisión.").font = NORMAL
    ws.merge_cells(start_row=nota, start_column=1, end_row=nota, end_column=2)
    ws.cell(nota, 1).alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[nota].height = 32


# ---------------------------------------------------------------- archivo
def escribir(resultado: ResultadoCruce, config: dict, carpeta_excel: Path, ahora: datetime | None = None, *,
             logo: Path | None = None, matriz: Path | None = None,
             cancelado: Callable[[], bool] | None = None) -> Path:
    """Escribe en `Cuadros generados` a un temporal y lo renombra al final. Nunca sobrescribe ni deja nada a medias."""
    ahora = ahora or datetime.now()
    salida = Path(carpeta_excel) / CARPETA_SALIDA
    wb = construir_libro(resultado, config, ahora, Path(carpeta_excel), logo, matriz)
    tmp = salida / f".~cuadro-{uuid.uuid4().hex[:8]}.xlsx"
    try:
        salida.mkdir(parents=True, exist_ok=True)
        if cancelado and cancelado():
            raise Cancelado()
        wb.save(tmp)
        if cancelado and cancelado():
            raise Cancelado()
        nombre = nombre_cuadro(resultado.programa["nombre"], resultado.anio_inicio, resultado.anio_fin, ahora)
        for _ in range(50):
            destino = ruta_libre(salida, nombre)
            try:
                _renombrar_sin_sobrescribir(tmp, destino)
                return destino
            except FileExistsError:
                continue                              # otro cuadro tomó ese nombre en este instante
        raise ErrorEscritura(salida, "sin_nombre", "No se encontró un nombre libre")
    except (Cancelado, ErrorEscritura):
        raise
    except PermissionError as e:
        raise ErrorEscritura(salida, "sin_permiso", str(e)) from e
    except OSError as e:
        causa = "disco_lleno" if getattr(e, "errno", None) == 28 else "no_se_pudo_escribir"
        raise ErrorEscritura(salida, causa, str(e)) from e
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def _renombrar_sin_sobrescribir(origen: Path, destino: Path) -> None:
    if os.name == "nt":
        os.rename(origen, destino)                   # en Windows falla si el destino existe
        return
    try:
        os.link(origen, destino)                     # en otros sistemas: falla si existe, nunca pisa
    except FileExistsError:
        raise
    except OSError:                                  # sistema de archivos sin enlaces: comprobar y renombrar
        if destino.exists():
            raise FileExistsError(destino) from None
        os.rename(origen, destino)
        return
    os.unlink(origen)
