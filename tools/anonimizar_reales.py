"""Crea copias anonimizadas de los Excel reales para usarlas como datos de prueba en el repositorio público.

Uso: python3 -I tools/anonimizar_reales.py <carpeta_con_los_reales> <carpeta_salida>

Qué conserva: la estructura (hojas, hojas ocultas, filas de títulos y notas, fila de encabezados, celdas combinadas,
validaciones de datos) y las columnas de una lista blanca que no identifican a nadie: año, semestre, programa, sede,
institución, país, tipos, fechas, vigencia, estado y columnas APLICA / NO APLICA.
Qué cambia: todo lo demás se reemplaza por valores ficticios (nombres, correos, documentos, descripciones, enlaces,
valores en dinero, la fecha exacta, que pasa a ser el 1 de enero del mismo año). Los valores vacíos o del tipo "N/A" se dejan tal cual, porque son rarezas que hay que probar.
Qué quita: macros, tablas dinámicas y validaciones de datos (traen correos y nombres incrustados), comentarios de
celdas, hipervínculos, imágenes y autor del archivo.
Los .xlsm siguen siendo .xlsm (libro habilitado para macros, sin macros).

Al final se verifica que ningún texto de las columnas con datos de personas (nombres, correos, documentos,
teléfonos, cargos, descripciones, perfiles, evidencias) aparezca en ninguna celda de las copias, ni ningún correo real.
"""
import html
import re
import sys
import zipfile
import unicodedata
import warnings
from datetime import date, datetime
from pathlib import Path

import openpyxl
from openpyxl.cell.cell import MergedCell
from openpyxl.workbook.workbook import Workbook

warnings.filterwarnings("ignore")

XLSM = "application/vnd.ms-excel.sheet.macroEnabled.main+xml"

ARCHIVOS = {  # original (sin el prefijo de la subida) -> nombre en el repositorio
    "MATRIZ_CONVENIOS_INTERNACIONAL_VIGENTES_1.xlsx": "MATRIZ CONVENIOS INTERNACIONAL VIGENTES.xlsx",
    "CONSOLIDADO_DE_MOVILIDAD_INTERNACIONAL_2022_Pereira.xlsm": "CONSOLIDADO DE MOVILIDAD INTERNACIONAL 2022 Pereira.xlsm",
    "Reporte_Internacionalizaci_n_en_casa_2022-1_Pereira.xlsx": "Reporte Internacionalización en casa 2022-1 Pereira.xlsx",
    "Reporte_Internacionalizaci_n_en_casa_2022-2_Pereira.xlsm": "Reporte Internacionalización en casa 2022-2 Pereira.xlsm",
    "CM_20252_Administraci_n_de_Empresas_Pre_Per_Convenios.xlsx": "CM 2025-2 Administración de Empresas Pereira (ejemplo de salida).xlsx",
}
SIN_DATOS_PERSONALES = {"CM_20252_Administraci_n_de_Empresas_Pre_Per_Convenios.xlsx"}
# Hojas de listas y catálogos sin datos de personas: se copian enteras.
# Hojas de notas libres: solo se conserva el nombre de la institución.
HOJAS_LIBRES = {"a tenener en cuenta"}
HOJAS_CATALOGO = {"paises", "programas", "listas", "buscarv", "hoja2", "instrucciones"}

LISTA_BLANCA = {
    # matriz
    "n", "nombre de la institucion", "con actividades", "acronimo o sigla", "pais", "region", "ciudad",
    "objeto del convenio", "codigo alianza", "tipo de convenio", "fecha de inicio", "fecha de finalizacion",
    "vigencia en anos", "estado", "renovacion automatica o indefinido", "sede desde la cual se lidero el convenio",
    "tipo de oferta de movilidad", "cupos para movilidad", "periodos de cupos", "institucion", "iso3",
    # movilidad
    "ano", "semestre", "vinculo snies", "rol", "tipo movilidad", "impacto de movilidad", "modalidad", "sede",
    "facultad o area", "programa o dependencia", "codigo snies", "codigo sai", "metodologia", "nivel de formacion",
    "indicador estrategico", "pais origen destino", "codigo iso", "institucion de origen destino",
    "esquema de movilidad",
    # internacionalización en casa
    "tipo de actividad", "si selecciono otra cual", "alcance actividad", "fecha de inicio de la actividad",
    "fecha fin de la actividad", "metodologia de la actividad", "nombre programa dependencia", "facultad",
    "nivel de formacion programa", "modalidad programa", "sede o seccional",
    "entidad organizacion institucion internacional vinculada", "tipo participantes", "no de participantes",
}
VOCABULARIO_SEGURO = {"", "aplica", "no aplica", "si", "no", "x"}
VACIOS = {"", "n a", "na", "no aplica", "ninguna", "ninguno", "sin convenio", "0"}


def norm(s):
    s = unicodedata.normalize("NFD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)|\*", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def fila_de_encabezados(ws, max_fila=6):
    mejor, fila = 0, 1
    for r in range(1, min(max_fila, ws.max_row) + 1):
        n = sum(1 for c in ws[r] if isinstance(c.value, str) and c.value.strip())
        if n > mejor:
            mejor, fila = n, r
    return fila


def ficticio(valor, col, contador):
    if isinstance(valor, datetime):
        return datetime(valor.year, 1, 1)          # se conserva el año; la fecha exacta no
    if isinstance(valor, date):
        return date(valor.year, 1, 1)
    if valor is None or isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return 0
    if norm(valor) in VACIOS:
        return valor
    contador[col] = contador.get(col, 0) + 1
    n = contador[col]
    if "@" in valor:
        return f"persona{n:04d}@ejemplo.org"
    if valor.strip().lower().startswith("http"):
        return f"https://ejemplo.org/evidencia/{n}"
    return f"Dato ficticio {col}-{n}"


def limpiar_hoja(ws):
    """Quita de cualquier hoja lo que puede guardar datos fuera de las celdas.

    Comentarios (guardan el autor), hipervínculos, imágenes, tablas dinámicas (su caché copia todos los datos
    originales) y validaciones de datos (algunas listas desplegables tienen nombres y correos escritos dentro).
    """
    ws._pivots = []
    ws.data_validations.dataValidation = []
    for fila in ws.iter_rows(min_row=1, max_row=ws.max_row):
        for celda in fila:
            if isinstance(celda, MergedCell):
                continue
            celda.comment = None
            celda.hyperlink = None
    ws._images = []


def anonimizar_hoja(ws, reemplazados):
    limpiar_hoja(ws)
    if norm(ws.title) in HOJAS_CATALOGO:
        return
    hdr = fila_de_encabezados(ws)
    contador, vistos = {}, set()
    for c in ws[hdr]:
        letra = c.column_letter
        valores = [ws.cell(r, c.column).value for r in range(hdr + 1, ws.max_row + 1)]
        if norm(ws.title) in HOJAS_LIBRES:
            conservar = norm(c.value) == "nombre de la institucion"
        else:
            # Si un encabezado se repite (p. ej. «Código ISO» del destino y del origen), solo vale el primero.
            repetido = norm(c.value) in vistos and norm(c.value) != ""
            conservar = not repetido and (norm(c.value) in LISTA_BLANCA or norm(c.value).endswith(" pereira") or all(
                norm(v) in VOCABULARIO_SEGURO for v in valores))
        vistos.add(norm(c.value))
        if conservar:
            continue
        for r in range(hdr + 1, ws.max_row + 1):
            celda = ws.cell(r, c.column)
            if isinstance(celda, MergedCell):
                continue
            nuevo = ficticio(celda.value, letra, contador)
            if nuevo != celda.value:
                if isinstance(celda.value, str):
                    reemplazados.add(celda.value.strip())
                celda.value = nuevo


def limpiar_libro(wb):
    wb.properties.creator = "Datos de prueba anonimizados"
    wb.properties.lastModifiedBy = "Datos de prueba anonimizados"
    wb.properties.title = wb.properties.subject = wb.properties.description = None
    wb.properties.keywords = wb.properties.category = None


class LibroXlsm(Workbook):
    @property
    def mime_type(self):
        return XLSM


def procesar(origen: Path, destino: Path, nombre_original: str):
    wb = openpyxl.load_workbook(origen, data_only=True)   # valores, no fórmulas: así se leen los reales
    reemplazados = set()
    if nombre_original not in SIN_DATOS_PERSONALES:
        for ws in wb.worksheets:
            anonimizar_hoja(ws, reemplazados)
    else:
        for ws in wb.worksheets:
            limpiar_hoja(ws)
    limpiar_libro(wb)
    wb.vba_archive = None
    if destino.suffix.lower() == ".xlsm":
        wb.__class__ = LibroXlsm
    wb.save(destino)
    return reemplazados


PERSONALES = ("nombre", "apellido", "correo", "e mail", "documento", "telefono", "experto", "estudiante",
              "docente", "cargo", "evidencia", "descripcion", "perfil", "contacto", "solicitante", "comentario")


def textos_personales(origen: Path) -> set:
    """Textos que en el original solo aparecen en columnas de datos de personas.

    Un texto que también está en una columna conservada (p. ej. «Granada» como país) es una coincidencia, no una fuga.
    """
    wb = openpyxl.load_workbook(origen, data_only=True, read_only=True)
    textos, conservados = set(), set()
    for ws in wb.worksheets:
        filas = list(ws.iter_rows(values_only=True))
        if not filas:
            continue
        hdr = max(range(min(6, len(filas))),
                  key=lambda i: sum(1 for v in filas[i] if isinstance(v, str) and v.strip()))
        catalogo = norm(ws.title) in HOJAS_CATALOGO
        for j, h in enumerate(filas[hdr]):
            nh = norm(h)
            personal = not catalogo and nh not in LISTA_BLANCA and any(p in nh for p in PERSONALES)
            conservado = catalogo or nh in LISTA_BLANCA or nh.endswith(" pereira")
            for f in filas[hdr + 1:]:
                v = f[j] if j < len(f) else None
                if isinstance(v, str) and len(v.strip()) > 3 and norm(v) not in VACIOS:
                    if personal:
                        textos.add(v.strip())
                    elif conservado:
                        conservados.add(v.strip())
    return textos - conservados


def textos_del_paquete(destino: Path) -> list[str]:
    """Todos los textos del archivo por dentro (celdas, fórmulas, listas, atributos), no solo los valores."""
    textos = []
    with zipfile.ZipFile(destino) as z:
        for parte in z.namelist():
            if not parte.endswith((".xml", ".rels", ".vml")):
                textos.append(z.read(parte).decode("latin-1"))   # binarios: se buscan correos igual
                continue
            xml = z.read(parte).decode("utf-8", errors="replace")
            for t in re.findall(r">([^<]+)<", xml) + re.findall(r'="([^"]*)"', xml):
                textos.append(html.unescape(t))
    return textos


def verificar(origen: Path, destino: Path):
    """Ningún texto de una columna personal del original ni ningún correo real debe estar en la copia (por dentro)."""
    buscados = textos_personales(origen)
    fugas, correos = set(), set()
    for t in textos_del_paquete(destino):
        for trozo in {t.strip(), *(x.strip().strip('"') for x in re.split(r"[,;\n]", t))}:
            if trozo in buscados:
                fugas.add(trozo[:40])
        correos.update(m for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", t) if "ejemplo.org" not in m)
    return len(buscados), fugas, correos


def main(entrada: Path, salida: Path):
    salida.mkdir(parents=True, exist_ok=True)
    ok = True
    for original, nuevo in ARCHIVOS.items():
        encontrados = sorted(entrada.glob(f"*{original}"))
        if not encontrados:
            print(f"FALTA  {original}")
            ok = False
            continue
        destino = salida / nuevo
        reemplazados = procesar(encontrados[0], destino, original)
        n_personales, fugas, correos = verificar(encontrados[0], destino)
        estado = "OK    " if not fugas and not correos else "FUGA  "
        ok &= not fugas and not correos
        print(f"{estado}{nuevo}: {len(reemplazados)} textos reemplazados; {n_personales} textos personales "
              f"buscados; fugas={len(fugas)} correos={len(correos)}")
        for f in list(fugas)[:5] + list(correos)[:5]:
            print("        ", f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
