"""Muestra inventada de los cuatro Excel de entrada, con las mismas rarezas que los reales de 2022.

No contiene datos de nadie: instituciones, personas y actividades son ficticias. Los encabezados sí copian los
reales (son la estructura que el programa debe reconocer), incluidos sus espacios sobrantes, tildes y "(*)".
Se genera al correr las pruebas; también sirve para probar a mano:

    python3 tests/muestra_sintetica.py <carpeta_salida>
"""
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.workbook.workbook import Workbook

XLSM = "application/vnd.ms-excel.sheet.macroEnabled.main+xml"

NOMBRES = {
    "matriz": "MATRIZ CONVENIOS INTERNACIONAL VIGENTES.xlsx",
    "movilidad": "CONSOLIDADO DE MOVILIDAD INTERNACIONAL 2022 Pereira.xlsm",
    "ic1": "Reporte Internacionalización en casa 2022-1 Pereira.xlsx",
    "ic2": "Reporte Internacionalización en casa 2022-2 Pereira.xlsm",
}

# Encabezados de programa tal como están en la matriz real (con sus espacios dobles y sobrantes).
PROGRAMAS_MATRIZ = [
    "Administración de empresas - Pereira", "Administración de empresas - Bogotá ",
    "Contaduría Pública - Pereira  ", "Administración de negocios internacionales - Pereira   ",
    "Técnico Laboral en Auxiliar en Enfermería - Pereira", "Enfermería - Pereira", "Enfermería - Bogotá",
    "Fisioterapia - Pereira", "Instrumentación Quirúrgica - Pereira", "Odontología - Pereira", "Optometría - Pereira",
    "Entrenamiento Deportivo - Pereira", "Tecnología en Radiología e Imágenes Diagnósticas -  Pereira",
    "Terapia Respiratoria - Pereira", "Especialización en Auditoria en Salud - Pereira",
    "Especialización en Epidemiología - Pereira",
    "Especialización en Gerencia en Seguridad y Salud en el Trabajo - Pereira", "Psicología - Pereira",
    "Derecho - Pereira", "Especialización en Contratación Pública - Pereira",
    "Especialización en Derecho Administrativo - Pereira",
    "Especialización en Derecho Administrativo y Constitucional - Pereira", "Arquitectura - Pereira",
    "Comunicación Audiovisual y Digital - Pereira", "Tecnología en Animación y Posproducción Audiovisual - Pereira",
    "Licenciatura en Educación Infantil - Pereira", "Ingeniería Industrial Distancia - Pereira",
]
MATRIZ_GENERALES = ["N°", "NOMBRE DE LA INSTITUCIÓN", "CON ACTIVIDADES", "ACRÓNIMO O SIGLA", "PAÍS", "REGIÓN",
                    "CIUDAD", "OBJETO DEL CONVENIO", "NOMBRE", "CARGO O DEPENDENDENCIA", "CORREO ELECTRÓNICO",
                    "TELEFONO", "PÁGINA", "CÓDIGO ALIANZA", "TIPO DE CONVENIO", "FECHA DE INICIO",
                    "FECHA DE FINALIZACIÓN", "VIGENCIA EN AÑOS", "ESTADO"]
# (institución, tipo, inicio, fin, vigencia, estado, programas de Pereira que APLICAN)
CONVENIOS = [
    ("UNIVERSIDAD FICTICIA DEL NORTE", "MARCO", datetime(2019, 3, 1), datetime(2024, 3, 1), 5.0, "VENCIDO", {0, 10}),
    ("UNIVERSIDAD FICTICIA DEL NORTE", "ESPECÍFICO", datetime(2021, 6, 15), datetime(2031, 6, 15), 10.0, "VIGENTE", {0}),
    ("INSTITUTO DE PRUEBA DEL SUR", "MARCO", datetime(2020, 1, 10), "INDEFINIDO", 5.0, "VIGENTE", {0, 5}),
    ("Universidad Inventada de Ultramar", "ESPECÍFICO", datetime(2018, 2, 1), None, 3.0, "VENCIDO", {0}),
    ("ACADEMIA IMAGINARIA", "MARCO", "SIN FECHA", 2025, 5.0, "ANULADO", {0}),
    ("CENTRO DE ESTUDIOS FALSOS", "MARCO", datetime(2022, 8, 1), 2027, 5.0, "VIGENTE", {7}),
]


class _LibroXlsm(Workbook):
    @property
    def mime_type(self):
        return XLSM


def guardar(wb, ruta: Path):
    """Guarda conservando el tipo .xlsm cuando la extensión lo pide."""
    if ruta.suffix.lower() == ".xlsm":
        wb.__class__ = _LibroXlsm
    wb.save(ruta)


def _matriz(ruta):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "CONV_INTERNACIONALES"
    ws["A2"], ws["N2"], ws["T2"] = "INFORMACIÓN GENERAL", "DATOS GENERALES DEL CONVENIO", "F.C. ADMINISTRATIVAS "
    ws.merge_cells("A2:H2")
    for j, h in enumerate(MATRIZ_GENERALES + PROGRAMAS_MATRIZ, start=1):
        ws.cell(3, j, h)
    for i, (inst, tipo, ini, fin, vig, estado, aplica) in enumerate(CONVENIOS, start=1):
        fila = [float(i), inst, None, None, "PAÍS FICTICIO", "REGIÓN", "CIUDAD", f"Objeto ficticio del convenio {i}",
                f"Persona ficticia {i}", "Cargo ficticio", f"contacto{i}@ejemplo.org", "000", "https://ejemplo.org",
                f"FUAA-{1000 + i}", tipo, ini, fin, vig, estado]
        fila += ["APLICA" if k in aplica else "NO APLICA" for k in range(len(PROGRAMAS_MATRIZ))]
        for j, v in enumerate(fila, start=1):
            ws.cell(3 + i, j, v)
    oculta = wb.create_sheet("CATALOGOS")
    oculta.append(["PAÍS", "REGIÓN"])
    oculta.sheet_state = "hidden"
    guardar(wb, ruta)


def _movilidad(ruta):
    wb = openpyxl.Workbook()
    wb.active.title = "Instrucciones "
    wb.active.sheet_state = "hidden"
    ws = wb.create_sheet("BD GENERAL")
    wb.active = 1
    ws.append(["AÑO (*)", "SEMESTRE (*)", "VINCULO SNIES (*)", "ROL", "TIPO MOVILIDAD", "IMPACTO DE MOVILIDAD (*)",
               "MODALIDAD (*)", "SEDE (*)", "FACULTAD O ÁREA", "PROGRAMA O DEPENDENCIA (*)", "CODIGO SNIES",
               "CODIGO SAI", "METODOLOGÍA (*)", "NIVEL DE FORMACIÓN", "INDICADOR ESTRATÉGICO (*)",
               "PAIS ORIGEN / DESTINO (*)", "Código ISO", "Institución de Origen/Destino (*)", "Esquema de Movilidad",
               "TIPO DE CONVENIO", "PRIMER NOMBRE (*)", "PRIMER APELLIDO (*)", "E-mail (*)"])
    filas = [
        (2022.0, 1.0, "Experto Internacional", "Pereira", "Administración de Empresas", "Universidad Ficticia del Norte ", "ESPECIFICO"),
        (2022.0, 2.0, "Estudiantes en el exterior", "Pereira", "Administración de Empresas\nContaduría Pública", "Instituto de Prueba del Sur", "MARCO"),
        (2022.0, 2.0, "Profesores extranjeros", "Bogotá", "Administración de Empresas", "Universidad Ficticia del Norte", "RED"),
        (2022.0, 1.0, "Estudiantes extranjeros", "Pereira", "Optometría", "Universidad Sin Convenio", "SIN CONVENIO"),
    ]
    for i, (anio, sem, vinc, sede, prog, inst, tconv) in enumerate(filas, start=1):
        ws.append([anio, sem, vinc, "ROL", "ENTRANTE", "ALTO", "MODALIDAD", sede, "Facultad", prog, 1.0, 2.0,
                   "Presencial", "Profesional", "Indicador", "País", 0.0, inst, "Esquema", tconv,
                   f"Nombre{i}", f"Apellido{i}", f"persona{i}@ejemplo.org"])
    listas = wb.create_sheet("LISTAS")
    listas.append(["VINCULO_SNIES"])
    listas.sheet_state = "hidden"
    guardar(wb, ruta)


_IC = ["AÑO", "SEMESTRE", "TIPO DE ACTIVIDAD", "SI SELECCIONÓ OTRA. CUÁL.", "ALCANCE ACTIVIDAD",
       "FECHA DE INICIO DE LA ACTIVIDAD", "FECHA FIN DE LA ACTIVIDAD", "NOMBRE DE LA ACTIVIDAD DE INTERNACIONALIZACIÓN",
       "DESCRIPCIÓN ACTIVIDAD", "METODOLOGÍA DE LA ACTIVIDAD", "NOMBRE PROGRAMA, DEPENDENCIA", "FACULTAD",
       "NIVEL DE FORMACIÓN PROGRAMA", "MODALIDAD PROGRAMA", "SEDE O SECCIONAL",
       "NOMBRES EXPERTO(S) INTERNACIONAL(ES) VINCULADO(S)", "PERFIL(ES) DE INVITADO(S) INTERNACIONAL(ES). MÁX. 2 LÍNEAS",
       "ENTIDAD / ORGANIZACIÓN/ INSTITUCIÓN INTERNACIONAL VINCULADA", "PAÍS", "TIPO PARTICIPANTES",
       "No. DE PARTICIPANTES"]


def _fila_ic(anio, sem, prog, inst, participantes, inicio=datetime(2022, 3, 18)):
    return [anio, sem, "Clase espejo", "N/A", "PROGRAMAS", inicio, inicio, "Actividad ficticia", "Descripción ficticia",
            "Virtual", prog, "Facultad", "Profesional", "Presencial", "Pereira", "N/A", "N/A", inst, "País",
            "Estudiantes", participantes]


def _ic1(ruta):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hoja1"
    ws.append(_IC)
    ws.append(_fila_ic(2022.0, 1.0, "Administración de Empresas", "Instituto de Prueba del Sur", 30.0))
    ws.append(_fila_ic(2022.0, 1.0, "Administración de Empresas", "Instituto de prueba del sur ", 25.0))
    ws.append(_fila_ic(2022.0, 1.0, "Administración de Empresas", "N/A", 40.0))
    ws.append(_fila_ic(2022.0, 1.0, "Optometría", "Centro de Estudios Falsos", "300 invitados y 25 ponencias"))
    guardar(wb, ruta)


def _ic2(ruta):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "BASE DE DATOS"
    ws["B1"] = "Tener en cuenta que : \nAlgunas casillas tienen opción de desplegable."
    encabezado = list(_IC)
    encabezado[10] = "NOMBRE PROGRAMA, DEPENDENCIA "
    encabezado[15] = "UNIVERSIDAD INVENTADA "                 # encabezado sobrescrito por error
    for j, h in enumerate(encabezado, start=2):                # la primera columna es la B
        ws.cell(2, j, h)
    filas = [_fila_ic(2022.0, 2.0, "Administración de Empresas", "Universidad Ficticia del Norte", 12.0),
             _fila_ic(2022.0, 2.0, "Administración de Empresas", "NA", 8.0),
             _fila_ic(2022.0, 2.0, "Administración de Empresas", "Universidad Inventada de Ultramar", 5.0,
                      inicio="20/05/222")]                  # fecha escrita como texto
    for i, fila in enumerate(filas, start=3):
        for j, v in enumerate(fila, start=2):
            ws.cell(i, j, v)
    for nombre in ("LISTAS", "PROGRAMAS", "PAISES"):
        wb.create_sheet(nombre).sheet_state = "hidden"
    guardar(wb, ruta)


def crear_muestra(carpeta: Path) -> dict[str, Path]:
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = {k: carpeta / v for k, v in NOMBRES.items()}
    _matriz(rutas["matriz"])
    _movilidad(rutas["movilidad"])
    _ic1(rutas["ic1"])
    _ic2(rutas["ic2"])
    return rutas


if __name__ == "__main__":
    for r in crear_muestra(Path(sys.argv[1])).values():
        print(r)
