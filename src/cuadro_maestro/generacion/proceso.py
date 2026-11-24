"""La generación completa en 5 pasos: leer la matriz, la movilidad e internacionalización en casa, cruzar y escribir.

Se detiene (Hoja de errores) si algún archivo existe pero no se puede leer, si falta la matriz, si ningún convenio
queda en el cuadro o si no se puede escribir el archivo. Un archivo que falta es solo un aviso. Cancelar es inmediato y
no deja ningún archivo. La interfaz recibe el avance por `al_avanzar(paso, estado, texto)`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from ..cruce import ResultadoCruce, cruzar
from ..recursos import logo_cna
from ..lectura import Lectura, leer_carpeta
from ..lectura import Cancelado as CanceladoLectura
from ..lectura.modelos import FALTA_ARCHIVO
from . import errores as E
from .escritor import Cancelado as CanceladoEscritura
from .escritor import ErrorEscritura, escribir

# Estados de cada paso en el modal de progreso (mockup 30) y en la hoja de errores (43-45)
PENDIENTE, EN_CURSO, HECHO, CON_AVISO, ERROR, NO_SE_LLEGO = (
    "pendiente", "en_curso", "hecho", "con_aviso", "error", "no_se_llego")


class Cancelado(Exception):
    """La persona canceló: no se creó ningún archivo y la última generación guardada no cambia."""


@dataclass
class EstadoPaso:
    paso: str
    estado: str = PENDIENTE
    texto: str = ""


class GeneracionDetenida(Exception):
    def __init__(self, errores: list[E.ErrorGeneracion], pasos: list[EstadoPaso], lectura: Lectura | None = None):
        super().__init__(f"{len(errores)} error(es)")
        self.errores, self.pasos, self.lectura = errores, pasos, lectura


@dataclass
class Generacion:
    ruta: Path
    resultado: ResultadoCruce
    lectura: Lectura
    pasos: list[EstadoPaso]
    ahora: datetime
    contexto: dict = field(default_factory=dict)


def generar(carpeta: Path, config: dict, programa_id: str, anio_inicio: int, anio_fin: int, *,
            ahora: datetime | None = None, logo: Path | None = None,
            al_avanzar: Callable[[str, str, str], None] | None = None,
            cancelado: Callable[[], bool] | None = None) -> Generacion:
    pasos = {p: EstadoPaso(p) for p, _ in E.PASOS}
    orden = [p for p, _ in E.PASOS]

    def marcar(paso, estado, texto=""):
        pasos[paso].estado, pasos[paso].texto = estado, texto
        if al_avanzar:
            al_avanzar(paso, estado, texto)

    def detener(errores, lectura=None):
        fallidos = {e.paso for e in errores}
        ultimo = max(orden.index(p) for p in fallidos)
        for p in orden:
            if p in fallidos:
                pasos[p].estado = ERROR
            elif orden.index(p) > ultimo:
                pasos[p].estado, pasos[p].texto = NO_SE_LLEGO, "No se llegó"
        raise GeneracionDetenida(errores, list(pasos.values()), lectura)

    actual = [E.PASO_MATRIZ]
    marcar(E.PASO_MATRIZ, EN_CURSO)

    def avance_lectura(fuente, ruta):
        paso = E.PASO_DE_FUENTE.get(fuente, E.PASO_IC)
        if paso != actual[0]:
            marcar(actual[0], HECHO)
            actual[0] = paso
            marcar(paso, EN_CURSO, ruta.name)

    try:
        lectura = leer_carpeta(carpeta, config, anio_inicio, anio_fin, al_avanzar=avance_lectura, cancelado=cancelado)
    except CanceladoLectura as e:
        raise Cancelado() from e

    # Estado final de los pasos de lectura: con aviso si falta algún archivo de ese paso.
    for fuente, paso in E.PASO_DE_FUENTE.items():
        faltan = [a for a in lectura.avisos if a.tipo == FALTA_ARCHIVO and a.fuente == fuente]
        texto = ("falta " + ", ".join(str(_periodo(a)) for a in faltan)) if faltan else ""
        marcar(paso, CON_AVISO if faltan else HECHO, texto)

    errores = [E.de_lectura(e) for e in lectura.errores]
    if lectura.matriz is None and not any(e.paso == E.PASO_MATRIZ for e in errores):
        errores.insert(0, E.sin_matriz(Path(carpeta)))
    if errores:
        detener(errores, lectura)

    if cancelado and cancelado():
        raise Cancelado()
    marcar(E.PASO_CRUCE, EN_CURSO)
    resultado = cruzar(lectura, config, programa_id)
    if resultado.sin_convenios:
        detener([E.sin_convenios(resultado.programa, lectura.matriz.ruta, len(lectura.matriz.registros),
                                 resultado.convenios_del_programa)], lectura)
    marcar(E.PASO_CRUCE, HECHO, f"{resultado.convenios_en_cuadro} convenios")

    marcar(E.PASO_ESCRITURA, EN_CURSO)
    ahora = ahora or datetime.now()
    try:
        ruta = escribir(resultado, config, Path(carpeta), ahora, logo=logo or logo_cna(),
                       matriz=lectura.matriz.ruta, cancelado=cancelado)
    except CanceladoEscritura as e:
        raise Cancelado() from e
    except ErrorEscritura as e:
        detener([E.de_escritura(e.carpeta, e.causa, e.detalle)], lectura)
    marcar(E.PASO_ESCRITURA, HECHO, ruta.name)
    contexto = {"programa": resultado.programa["nombre"], "vigencia": f"{anio_inicio}-{anio_fin}",
                "carpeta": str(carpeta)}
    return Generacion(ruta, resultado, lectura, list(pasos.values()), ahora, contexto)


def _periodo(aviso):
    return f"{aviso.anio}-{aviso.semestre}" if aviso.semestre else aviso.anio
