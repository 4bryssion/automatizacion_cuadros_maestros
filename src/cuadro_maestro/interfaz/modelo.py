"""Lógica de la ventana principal, sin Tkinter (se prueba sola): tabla de archivos, conteos y mensajes."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from ..lectura import archivos as A
from ..lectura.modelos import ABIERTO_EN_EXCEL, ARCHIVOS_REPETIDOS, Esperado

ENCONTRADO, FALTA = "encontrado", "falta"
CORTO = {"movilidad": "Movilidad", "internacionalizacion_en_casa": "Int. en casa"}


@dataclass
class Celda:
    estado: str
    texto: str
    ruta: Path | None = None
    aviso: str | None = None          # "abierto en Excel", "hay otro archivo para este año"


@dataclass
class ResumenArchivos:
    carpeta: Path
    carpeta_existe: bool
    matriz: Esperado | None
    matriz_modificada: datetime | None
    filas: list[tuple[int, Celda, Celda, Celda]]
    esperados: int
    encontrados: int
    faltan: list[str] = field(default_factory=list)
    reconocidos: int = 0              # archivos de la carpeta que el programa reconoce (de cualquier año)

    @property
    def completo(self) -> bool:
        return self.encontrados == self.esperados

    @property
    def sin_archivos(self) -> bool:
        """La carpeta existe pero no tiene ningún archivo reconocible (mockup 39)."""
        return self.carpeta_existe and self.reconocidos == 0


def resumir(carpeta, config: dict, desde: int, hasta: int) -> ResumenArchivos:
    carpeta = Path(carpeta)
    existe = carpeta.is_dir()
    esperados, avisos = A.buscar(carpeta, config, desde, hasta) if existe else ([], [])
    abiertos = {a.ruta for a in avisos if a.tipo == ABIERTO_EN_EXCEL}
    repetidos = {a.ruta for a in avisos if a.tipo == ARCHIVOS_REPETIDOS}
    matriz = next((e for e in esperados if e.fuente == "matriz"), None)
    por_clave = {(e.fuente, e.anio, e.semestre): e for e in esperados}

    def celda(fuente, anio, semestre=None):
        e = por_clave.get((fuente, anio, semestre))
        if not e or not e.encontrado:
            return Celda(FALTA, "Falta este archivo")
        aviso = ("abierto en Excel" if e.ruta in abiertos else
                 "hay otro archivo para este periodo" if e.ruta in repetidos else None)
        return Celda(ENCONTRADO, "Encontrado", e.ruta, aviso)

    filas, faltan = [], []
    for anio in range(desde, hasta + 1):
        fila = (anio, celda("movilidad", anio), celda("internacionalizacion_en_casa", anio, 1),
                celda("internacionalizacion_en_casa", anio, 2))
        filas.append(fila)
        for c, nombre in zip(fila[1:], (f"Movilidad {anio}", f"Int. en casa {anio}-1", f"Int. en casa {anio}-2")):
            if c.estado == FALTA:
                faltan.append(nombre)
    por_anio = [e for e in esperados if e.fuente != "matriz"]
    reconocidos = sum(1 for p in A.candidatos(carpeta) if any(A.reconocer(p.name, f) for f in config["fuentes"])) \
        if existe else 0
    modificada = None
    if matriz and matriz.encontrado:
        try:
            modificada = datetime.fromtimestamp(matriz.ruta.stat().st_mtime)
        except OSError:
            pass
    return ResumenArchivos(carpeta, existe, matriz, modificada, filas, len(por_anio),
                           sum(e.encontrado for e in por_anio), faltan, reconocidos)


def mensaje_faltantes(faltan: list[str]) -> str | None:
    if not faltan:
        return None
    if len(faltan) == 1:
        return f"Falta {faltan[0]}. Puedes generar igual: quedará anotado en la revisión."
    lista = ", ".join(faltan[:3]) + ("…" if len(faltan) > 3 else "")
    return f"Faltan {len(faltan)} archivos ({lista}). Puedes generar igual: quedarán anotados en la revisión."


def motivo_para_no_generar(carpeta: str | None, programa_id: str | None, desde, hasta,
                           resumen: ResumenArchivos | None) -> str | None:
    """None si se puede generar; si no, la razón (se muestra junto al botón desactivado)."""
    if not carpeta:
        return "Elige la carpeta con los Excel."
    if resumen is None or not resumen.carpeta_existe:
        return "No se encuentra la carpeta."
    if not programa_id:
        return "Elige el programa."
    if desde is None or hasta is None:
        return "Elige la vigencia."
    if desde > hasta:
        return "«Desde» no puede ser mayor que «Hasta»."
    if not resumen.matriz or not resumen.matriz.encontrado:
        return "Falta la Matriz de convenios en la carpeta."
    return None


def cuando(momento: datetime, ahora: datetime | None = None) -> str:
    """«hoy 14:32», «ayer 09:10» o «21/11/2026 14:32»."""
    ahora = ahora or datetime.now()
    dias = (ahora.date() - momento.date()).days
    if dias == 0:
        return f"hoy {momento:%H:%M}"
    if dias == 1:
        return f"ayer {momento:%H:%M}"
    return f"{momento:%d/%m/%Y %H:%M}"


def vigencia(desde: int, hasta: int, separador: str = "–") -> str:
    return str(desde) if desde == hasta else f"{desde}{separador}{hasta}"
