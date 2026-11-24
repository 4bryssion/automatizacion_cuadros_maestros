"""Hoja de errores: por qué se detuvo la generación (mockups 43, 44 y 45).

Cada error es una tarjeta con título, dónde, qué pasó, qué hacer, botones y etiqueta. «Copiar detalle del error»
produce un texto plano con archivo, paso y causa técnica, para enviarlo a Sistemas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..cruce import modelos as CM
from ..cruce.avisos import NOMBRE_FUENTE, SEP, periodo
from ..lectura.modelos import CON_CONTRASENA, DANADO, EN_USO, ErrorLectura

# Pasos de la generación (modal de progreso y hoja de errores)
PASO_MATRIZ, PASO_MOVILIDAD, PASO_IC, PASO_CRUCE, PASO_ESCRITURA = "matriz", "movilidad", "ic", "cruce", "escritura"
PASOS = ((PASO_MATRIZ, "Leer la Matriz de convenios"), (PASO_MOVILIDAD, "Leer la Movilidad anual"),
         (PASO_IC, "Leer Internacionalización en casa"), (PASO_CRUCE, "Cruzar convenios con movilidades"),
         (PASO_ESCRITURA, "Escribir el cuadro maestro"))
PASO_DE_FUENTE = {"matriz": PASO_MATRIZ, "movilidad": PASO_MOVILIDAD, "internacionalizacion_en_casa": PASO_IC}
ETIQUETA = {EN_USO: "Archivo en uso", CON_CONTRASENA: "Con contraseña", DANADO: "Dañado"}


@dataclass
class ErrorGeneracion:
    paso: str
    titulo: str
    donde: str
    que_paso: str
    que_hacer: str
    acciones: list[str] = field(default_factory=list)
    etiqueta: str = ""
    ruta: Path | None = None
    detalle_tecnico: str = ""


def de_lectura(e: ErrorLectura) -> ErrorGeneracion:
    donde = SEP.join(x for x in (NOMBRE_FUENTE.get(e.fuente, e.fuente), periodo(e.anio, e.semestre)) if x)
    return ErrorGeneracion(PASO_DE_FUENTE.get(e.fuente, PASO_IC), e.ruta.name, donde, e.que_paso, e.que_hacer,
                           [CM.ABRIR_CARPETA], ETIQUETA[e.causa], e.ruta, f"{e.causa}: {e.detalle}".strip(": "))


def sin_convenios(programa: dict, matriz_ruta: Path | None, filas_matriz: int, aplican: int) -> ErrorGeneracion:
    nombre = matriz_ruta.name if matriz_ruta else "Matriz de convenios"
    if aplican:
        return ErrorGeneracion(PASO_CRUCE, f"Ningún convenio de {programa['nombre']} entra al cuadro",
                               f"{nombre}  ·  columna «{programa['columna_matriz']}»",
                               f"{aplican} convenios dicen APLICA, pero ninguno queda en el cuadro: los vencidos sin "
                               "resultados no entran y los que no tienen fechas válidas están en la revisión.",
                               "Revisa las fechas y el estado de esos convenios en la matriz, o la regla 1 en Reglas de cruce.",
                               [CM.ABRIR_ARCHIVO], "Sin convenios", matriz_ruta, "aplican>0, filas=0")
    return ErrorGeneracion(PASO_MATRIZ, f"Ningún convenio aplica a {programa['nombre']}",
                           f"{nombre}  ·  columna «{programa['columna_matriz']}»",
                           f"La matriz se leyó bien ({filas_matriz} filas), pero ninguna dice APLICA para este programa.",
                           "Revisa que la columna diga APLICA para este programa, o que su nombre en la matriz esté "
                           "en Programas.", [CM.ABRIR_ARCHIVO, CM.ABRIR_PROGRAMAS], "Sin convenios", matriz_ruta,
                           "aplican=0")


def sin_matriz(carpeta: Path) -> ErrorGeneracion:
    return ErrorGeneracion(PASO_MATRIZ, "Falta la Matriz de convenios", f"Carpeta {carpeta}",
                           "No hay un archivo de convenios en la carpeta. Sin él no se puede armar el cuadro.",
                           "Copia la matriz a la carpeta (un nombre que contenga «Convenios») y pulsa Reintentar.",
                           [CM.ABRIR_CARPETA], "Falta la matriz", None, "falta_matriz")


def de_escritura(carpeta: Path, causa: str, detalle: str) -> ErrorGeneracion:
    return ErrorGeneracion(PASO_ESCRITURA, "No se pudo guardar el cuadro", str(carpeta),
                           "Windows no permitió crear el archivo en esa carpeta: no hay permiso de escritura o el disco "
                           "está lleno.",
                           "Libera espacio o pide permiso sobre la carpeta de los Excel y pulsa Reintentar. También "
                           "puedes elegir otra carpeta en el paso 1.", [CM.ABRIR_CARPETA], "No se pudo escribir",
                           carpeta, f"{causa}: {detalle}")


def detalle_para_sistemas(errores: list[ErrorGeneracion], contexto: dict) -> str:
    """Texto de «Copiar detalle del error»: sin datos de personas, con lo que Sistemas necesita."""
    nombres = dict(PASOS)
    lineas = ["La generación del cuadro maestro se detuvo.", ""]
    lineas += [f"{k}: {v}" for k, v in contexto.items()]
    for i, e in enumerate(errores, start=1):
        lineas += ["", f"Error {i}: {e.titulo}", f"  Paso: {nombres.get(e.paso, e.paso)}", f"  Dónde: {e.donde}",
                   f"  Qué pasó: {e.que_paso}", f"  Causa técnica: {e.detalle_tecnico}"]
        if e.ruta:
            lineas.append(f"  Archivo: {e.ruta}")
    return "\n".join(lineas)
