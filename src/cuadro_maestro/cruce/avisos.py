"""Textos de los avisos de la revisión (Título, Dónde, Qué pasó, Qué hacer y botones).

Siguen los mockups 10 a 13 y docs/diseno_revision.md. «Dónde» nunca lleva datos de personas: archivo, hoja, fila e
institución. Los avisos del grupo «Corrige el Excel» terminan con «pulsa Recargar archivos».
"""
from __future__ import annotations

from pathlib import Path

from ..lectura import archivos as LA
from ..lectura import modelos as LM
from ..texto import normalizar
from . import modelos as M
from .modelos import AvisoRevision

SEP = "  ·  "
NOMBRE_FUENTE = {"matriz": "Matriz de convenios", "movilidad": "Movilidad",
                 "internacionalizacion_en_casa": "Internacionalización en casa"}
NOMBRE_DATO = {"institucion": "Institución", "objeto": "Objeto del convenio", "codigo": "Código alianza",
               "tipo_convenio": "Tipo de convenio", "fecha_inicio": "Fecha de inicio", "fecha_fin": "Fecha de fin",
               "vigencia_anios": "Vigencia en años", "estado": "Estado", "anio": "Año", "semestre": "Semestre",
               "vinculo": "Vínculo", "sede": "Sede", "programa": "Programa", "tipo_actividad": "Tipo de actividad"}
SIN_LA_COLUMNA = {"vinculo": "Sin ella no distingue el tipo de persona.",
                  "institucion": "Sin ella no se puede saber a qué convenio va cada fila.",
                  "programa": "Sin ella no se sabe de qué programa es cada fila.",
                  "fecha_inicio": "Sin ella no se sabe en qué años cuenta cada convenio.",
                  "estado": "Sin ella no se sabe si cada convenio está activo."}


def usar_nombres(config: dict) -> None:
    """Los avisos y la Hoja de errores nombran cada fuente como se llama en Configuración (se puede cambiar)."""
    NOMBRE_FUENTE.update({f["id"]: f["nombre"] for f in config.get("fuentes", [])})
    FUENTES.update({f["id"]: f for f in config.get("fuentes", [])})


FUENTES: dict[str, dict] = {}            # las de la configuración en uso (para los nombres de ejemplo)


def periodo(anio, semestre) -> str:
    if anio and semestre:
        return f"{anio}-{semestre}"
    return str(anio) if anio else ""


def nombre_fuente(fuente: str, anio=None, semestre=None) -> str:
    return " ".join(x for x in (NOMBRE_FUENTE.get(fuente, fuente), periodo(anio, semestre)) if x)


def donde(ruta: Path | None, hoja: str | None = None, fila: int | None = None, extra: str | None = None) -> str:
    partes = [ruta.name if ruta else None, f"hoja {hoja}" if hoja else None, f"fila {fila}" if fila else None, extra]
    return SEP.join(p for p in partes if p)


def _clave(*partes) -> str:
    return "|".join("" if p is None else str(p) for p in partes)


# ---------------------------------------------------------------- avisos que vienen de la lectura
def desde_lectura(a: LM.Aviso, carpeta: Path, programa: dict, hojas: dict) -> AvisoRevision | None:
    """Convierte un aviso de la lectura; devuelve None si no afecta al cuadro de este programa."""
    f, hoja = nombre_fuente(a.fuente or "", a.anio, a.semestre), hojas.get(a.ruta)
    if a.tipo == LM.FALTA_MATRIZ:
        return AvisoRevision(M.EXCEL, a.tipo, "Falta la Matriz de convenios", f"Carpeta {carpeta}",
                             "No hay un archivo de convenios en la carpeta. Sin él no se puede armar el cuadro.",
                             "Copia la matriz a la carpeta (un nombre que contenga «Convenios») y pulsa Recargar archivos.",
                             [M.ABRIR_CARPETA], clave=_clave(a.tipo))
    if a.tipo == LM.FALTA_ARCHIVO:
        unidad = "semestre quedó sin actividades" if a.semestre else "año quedó sin movilidades"
        if a.fuente == "internacionalizacion_en_casa" and not a.semestre:
            unidad = "año quedó sin actividades"
        ejemplo = LA.ejemplo(FUENTES[a.fuente], a.anio, a.semestre) if a.fuente in FUENTES else \
            f"{a.fuente}_{periodo(a.anio, a.semestre)}.xlsx"
        return AvisoRevision(M.EXCEL, a.tipo, f"Falta el archivo de {f}", f"Carpeta {carpeta}",
                             f"No hay un archivo de {f.lower()} en la carpeta, así que ese {unidad}.",
                             f"Copia el archivo a la carpeta con un nombre que lleve el {'año y el semestre' if a.semestre else 'año'} "
                             f"({ejemplo}). Cierra el Excel y pulsa Recargar archivos.",
                             [M.ABRIR_CARPETA], clave=_clave(a.tipo, a.fuente, a.anio, a.semestre))
    if a.tipo == LM.ARCHIVOS_REPETIDOS:
        otros = ", ".join(f"«{n}»" for n in a.detalle.get("descartados", []))
        return AvisoRevision(M.EXCEL, a.tipo, f"Dos archivos para {f}", f"Carpeta {carpeta}",
                             f"Se usó «{a.ruta.name}», el modificado más recientemente, y se dejó de lado {otros}.",
                             "Si no es el correcto, quita o renombra el que sobra en la carpeta y pulsa Recargar archivos.",
                             [M.ABRIR_CARPETA], ruta=a.ruta, clave=_clave(a.tipo, a.fuente, a.anio, a.semestre))
    if a.tipo == LM.ARCHIVO_SIN_PERIODO:
        return AvisoRevision(M.EXCEL, a.tipo, f"No se sabe de qué periodo es «{a.ruta.name}»", f"Carpeta {carpeta}",
                             f"Parece un archivo de {NOMBRE_FUENTE.get(a.fuente, a.fuente).lower()}, pero su nombre no dice "
                             "el año y el semestre, así que no se leyó.",
                             "Cambia el nombre para que lleve el año y el semestre (por ejemplo «… 2022-1 …»), cierra el "
                             "Excel y pulsa Recargar archivos.", [M.ABRIR_CARPETA], ruta=a.ruta, clave=_clave(a.tipo, a.ruta.name))
    if a.tipo == LM.SIN_ENCABEZADOS:
        return AvisoRevision(M.EXCEL, a.tipo, f"No se encontraron los encabezados de {f}", donde(a.ruta, hoja),
                             "En las primeras filas no hay ningún encabezado conocido, así que no se leyó ninguna fila.",
                             "Revisa que sea el archivo correcto y que tenga la fila de títulos de las columnas. Si los títulos "
                             "cambiaron, indícalos en Fuentes de datos y pulsa Recargar archivos.",
                             [M.ABRIR_ARCHIVO, M.ABRIR_FUENTES], ruta=a.ruta, detalle={"fuente": a.fuente},
                             clave=_clave(a.tipo, a.ruta.name))
    if a.tipo == LM.ABIERTO_EN_EXCEL:
        return AvisoRevision(M.INFORMATIVO, a.tipo, f"Archivo abierto en Excel: {f}", donde(a.ruta),
                             "Este archivo está abierto en Excel; lo que no se haya guardado no se lee.",
                             "Guarda y cierra el Excel; si cambiaste algo, pulsa Recargar archivos.", [],
                             ruta=a.ruta, clave=_clave(a.tipo, a.ruta.name))
    if a.tipo == LM.PROGRAMA_NUEVO_EN_MATRIZ:
        enc = a.detalle["encabezado"]
        return AvisoRevision(M.PROGRAMA, a.tipo, f"Programa nuevo en la matriz: «{enc}»", donde(a.ruta, hoja),
                             "Ese programa aparece en la matriz, pero no está en la lista de Configuración. Por eso no se "
                             "puede elegir al generar y sus convenios no entran a ningún cuadro.",
                             "Agrégalo en Programas. Si es otro nombre de un programa que ya existe, cambia la columna de ese programa.",
                             [M.ABRIR_PROGRAMAS], ruta=a.ruta, detalle=dict(a.detalle), clave=_clave(a.tipo, enc))
    if a.tipo in (LM.COLUMNA_POR_CONFIRMAR, LM.COLUMNA_SIN_IDENTIFICAR, LM.PROGRAMA_SIN_COLUMNA):
        es_programa = (a.dato or "").startswith("programa:")
        if es_programa and a.dato != f"programa:{programa['id']}":
            return None                                  # columna de otro programa: no afecta a este cuadro
        enc = a.detalle.get("encabezado")
        if a.tipo == LM.COLUMNA_POR_CONFIRMAR:
            que = (f"la columna del programa {programa['nombre']}" if es_programa
                   else f"el dato «{NOMBRE_DATO.get(a.dato, a.dato)}»")
            return AvisoRevision(M.PROGRAMA, a.tipo, f"Columna por confirmar: «{enc}»", donde(a.ruta, hoja),
                                 f"El programa cree que esta columna trae {que}, pero el nombre no es idéntico. Mientras no "
                                 "lo confirmes no la usa.",
                                 "Confirma que es la columna correcta o elige otra en Fuentes de datos. Se guarda para los "
                                 "próximos archivos.", [M.CONFIRMAR_SUGERENCIA, M.ABRIR_FUENTES], ruta=a.ruta,
                                 detalle={**a.detalle, "dato": a.dato, "fuente": a.fuente},
                                 clave=_clave(a.tipo, a.ruta.name, a.dato))
        if es_programa:
            return AvisoRevision(M.PROGRAMA, a.tipo, f"No se encontró la columna de {programa['nombre']} en la matriz",
                                 donde(a.ruta, hoja),
                                 f"La matriz no tiene una columna «{programa['columna_matriz']}», así que no se sabe qué "
                                 "convenios aplican a este programa.",
                                 "Revisa en Programas el nombre de la columna de este programa en la matriz.",
                                 [M.ABRIR_PROGRAMAS], ruta=a.ruta, clave=_clave(a.tipo, a.dato))
        nombre = NOMBRE_DATO.get(a.dato, a.dato)
        return AvisoRevision(M.PROGRAMA, a.tipo, f"Columna sin identificar: «{nombre}»", donde(a.ruta, hoja),
                             "El programa no pudo saber qué columna trae este dato. "
                             + SIN_LA_COLUMNA.get(a.dato, "Sin ella ese dato queda vacío."),
                             "Indica qué columna es en Fuentes de datos. Se guarda y sirve también para los próximos archivos.",
                             [M.ABRIR_FUENTES], ruta=a.ruta, detalle={"dato": a.dato, "fuente": a.fuente},
                             clave=_clave(a.tipo, a.ruta.name, a.dato))
    return None


# ---------------------------------------------------------------- avisos del cruce
def convenio_sin_inicio(ruta, hoja, fila, inst):
    return AvisoRevision(M.EXCEL, "convenio_sin_inicio", "Convenio sin fecha de inicio válida", donde(ruta, hoja, fila, inst),
                         "La celda «Fecha de inicio» está vacía o no es una fecha. Sin ella no se sabe en qué años cuenta "
                         "el convenio, así que quedó fuera del cuadro.",
                         "Abre el archivo y escribe la fecha en esa celda (por ejemplo 15/03/2021). Guarda y cierra el "
                         "Excel; luego pulsa Recargar archivos.", [M.ABRIR_ARCHIVO], ruta=ruta, filas=[fila],
                         clave=_clave("convenio_sin_inicio", fila, inst))


def convenio_fin_antes(ruta, hoja, fila, inst, inicio, fin):
    return AvisoRevision(M.EXCEL, "convenio_fin_antes_de_inicio", "Fecha de fin anterior a la de inicio",
                         donde(ruta, hoja, fila, inst),
                         f"El convenio tiene fecha de inicio {inicio:%d/%m/%Y} pero termina el {fin:%d/%m/%Y}. Una vigencia "
                         "no puede terminar antes de empezar, así que quedó fuera del cuadro.",
                         "Revisa las dos fechas de esa fila, corrígelas, guarda y cierra el Excel, y pulsa Recargar archivos.",
                         [M.ABRIR_ARCHIVO], ruta=ruta, filas=[fila], clave=_clave("convenio_fin_antes_de_inicio", fila, inst))


def convenio_sin_fin(ruta, hoja, fila, inst):
    return AvisoRevision(M.EXCEL, "convenio_sin_fin", "Convenio sin fecha de fin ni vigencia en años",
                         donde(ruta, hoja, fila, inst),
                         "La fecha de fin no es una fecha y la «Vigencia en años» está vacía, así que no se sabe hasta qué "
                         "año cuenta el convenio. Quedó fuera del cuadro.",
                         "Escribe la fecha de fin o la vigencia en años en esa fila. Guarda y cierra el Excel, y pulsa "
                         "Recargar archivos.", [M.ABRIR_ARCHIVO], ruta=ruta, filas=[fila],
                         clave=_clave("convenio_sin_fin", fila, inst))


def estado_no_reconocido(ruta, hoja, fila, inst, valor, etiqueta):
    return AvisoRevision(M.EXCEL, "estado_no_reconocido", f"Estado no reconocido: «{valor}»", donde(ruta, hoja, fila, inst),
                         f"La columna «Estado» no dice VIGENTE, VENCIDO ni ANULADO, así que el convenio se marcó como "
                         f"«{etiqueta}».",
                         "Corrige el estado en esa fila, guarda y cierra el Excel, y pulsa Recargar archivos.",
                         [M.ABRIR_ARCHIVO], ruta=ruta, filas=[fila], clave=_clave("estado_no_reconocido", fila, inst))


class Grupo:
    """Filas de un mismo archivo con el mismo problema (p. ej. la misma institución sin coincidencia)."""

    def __init__(self, ruta: Path, origen: str, nombre: str):
        self.ruta, self.origen, self.nombre = ruta, origen, " ".join(str(nombre).split())   # sin saltos de línea
        self.filas: list[int] = []

    @property
    def n(self) -> int:
        return len(self.filas)

    @property
    def plural(self) -> str:
        return "movilidades" if self.origen == "movilidad" else "actividades"

    @property
    def esas(self) -> str:
        singular = "movilidad" if self.origen == "movilidad" else "actividad"
        return f"esa {singular}" if self.n == 1 else f"esas {self.n} {self.plural}"

    def cuantas(self) -> str:
        singular = "movilidad" if self.origen == "movilidad" else "actividad"
        return f"1 {singular}" if self.n == 1 else f"{self.n} {self.plural}"

    def donde(self, con_nombre=True) -> str:
        f = self.filas
        filas = (f"fila {f[0]}" if len(f) == 1 else
                 "filas " + ", ".join(map(str, f[:3])) + ("…" if len(f) > 3 else ""))
        return SEP.join(x for x in (self.ruta.name, filas, self.nombre if con_nombre else None, self.cuantas()) if x)

    def aviso(self, grupo, tipo, titulo, que_paso, que_hacer, acciones, detalle=None, con_nombre=True):
        return AvisoRevision(grupo, tipo, titulo, self.donde(con_nombre), que_paso, que_hacer, acciones, ruta=self.ruta,
                             cantidad=self.n, filas=list(self.filas), detalle=detalle or {},
                             clave=_clave(tipo, self.ruta.name, normalizar(self.nombre)))


def institucion_sin_coincidencia(g: Grupo, sugerencias):
    return g.aviso(M.PROGRAMA, "institucion_sin_coincidencia", f"Institución sin coincidencia: «{g.nombre}»",
                   "Ese nombre no coincide con ninguna institución de la matriz de convenios (puede ser un error de "
                   f"escritura), por eso no se contaron {g.esas}.",
                   "Elige a qué institución corresponde. El programa lo recuerda y no vuelve a preguntar. No tienes que "
                   "editar el Excel.", [M.ELEGIR_INSTITUCION, M.PREGUNTAR_A_GEMINI],
                   {"como_aparece": g.nombre, "sugerencias": sugerencias}, con_nombre=False)


def sin_convenio_vigente(g: Grupo):
    return g.aviso(M.INFORMATIVO, "sin_convenio_vigente", f"{g.plural.capitalize()} sin convenio vigente en su año",
                   "La institución tiene convenio con el programa, pero ningún convenio cubre el año de "
                   f"{g.esas}. Por eso no entran al cuadro.",
                   "Nada obligatorio. Si el convenio sí existía, corrige sus fechas en el Excel de convenios y recarga.", [])


def sin_convenio_del_programa(g: Grupo, programa):
    return g.aviso(M.INFORMATIVO, "sin_convenio_del_programa",
                   f"{g.plural.capitalize()} con una institución sin convenio para {programa['nombre']}",
                   f"La institución está en la matriz, pero ninguno de sus convenios aplica a {programa['nombre']}. "
                   f"Por eso {g.esas} no entran a este cuadro.",
                   "Nada obligatorio. Si el convenio sí aplica, márcalo como APLICA en la matriz y recarga.", [])


def sin_convenio_declarado(g: Grupo):
    if g.n == 1:
        que = f"El archivo dice que {g.esas} se hizo sin convenio (o no tiene institución) y no está en la matriz."
    else:
        que = f"El archivo dice que {g.esas} se hicieron sin convenio (o no tienen institución) y no están en la matriz."
    return g.aviso(M.INFORMATIVO, "sin_convenio_declarado", f"{g.plural.capitalize()} sin convenio",
                   que + " No entran al cuadro.", "Nada. Solo se informa.", [])


def tipo_no_reconocido(g: Grupo):
    return g.aviso(M.PROGRAMA, "tipo_persona_no_reconocido", f"Tipo de persona no reconocido: «{g.nombre}»",
                   "Ese valor de la columna de vínculo no corresponde a ningún tipo de persona del cuadro, por eso no se "
                   f"contaron {g.esas}.",
                   "Agrégalo al tipo que corresponda en Tipos de persona. Se guarda para los próximos archivos.",
                   [M.ABRIR_TIPOS], {"valor": g.nombre}, con_nombre=False)


def programa_parecido(g: Grupo, programa):
    return g.aviso(M.PROGRAMA, "programa_parecido", f"Programa parecido: «{g.nombre}»",
                   f"Ese nombre se parece a {programa['nombre']} pero no es igual, así que {g.esas} no se contaron.",
                   "Si es el mismo programa, confírmalo: se guarda como equivalencia de programas y no vuelve a preguntar.",
                   [M.CONFIRMAR_SUGERENCIA, M.ABRIR_EQUIVALENCIAS_PROGRAMAS],
                   {"como_aparece": g.nombre, "es": programa["nombre"]}, con_nombre=False)


def actividades_sin_institucion(ruta, n):
    return AvisoRevision(M.INFORMATIVO, "actividades_sin_institucion", "Actividades sin institución omitidas",
                         donde(ruta, extra=f"{n} actividad{'es' if n != 1 else ''}"),
                         "Hay actividades de internacionalización en casa sin institución; no se pueden asignar a un convenio.",
                         "Nada. Solo se informa la cantidad.", [], ruta=ruta, cantidad=n,
                         clave=_clave("actividades_sin_institucion", ruta.name))
