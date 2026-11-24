"""Resultado del cruce: las filas del cuadro, los avisos de la revisión y las cifras del resumen."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

# Grupos de la revisión (docs/diseno_revision.md): dónde se arregla cada aviso.
EXCEL, PROGRAMA, INFORMATIVO = "excel", "programa", "informativo"
ORDEN_GRUPOS = (EXCEL, PROGRAMA, INFORMATIVO)

# Acciones (botones) que puede llevar un aviso; la interfaz pone el texto.
ABRIR_ARCHIVO = "abrir_archivo"
ABRIR_CARPETA = "abrir_carpeta"
ELEGIR_INSTITUCION = "elegir_institucion"
PREGUNTAR_A_GEMINI = "preguntar_a_gemini"
CONFIRMAR_SUGERENCIA = "confirmar_sugerencia"
ABRIR_FUENTES = "abrir_fuentes"
ABRIR_PROGRAMAS = "abrir_programas"
ABRIR_TIPOS = "abrir_tipos"
ABRIR_EQUIVALENCIAS_PROGRAMAS = "abrir_equivalencias_programas"


@dataclass
class Convenio:
    fila: int                      # fila de la matriz
    institucion: str               # tal como está en la matriz
    clave: str                     # institución normalizada (con equivalencias)
    tipo: str                      # "marco", "especifico" u "otro"
    tipo_texto: str
    codigo: str | None
    objeto: str | None
    inicio: date | None
    anio_inicio: int | None
    anio_fin: int | None
    vigencia_anios: int | None
    estado: str
    activo: bool
    datos: dict = field(default_factory=dict)   # todos los datos de su fila en la matriz (para campos creados)


@dataclass
class FilaCuadro:
    numero: int
    convenio: Convenio
    resultados: dict[int, dict[str, int]]      # año -> tipo de persona -> cantidad

    @property
    def total(self) -> int:
        return sum(n for por_tipo in self.resultados.values() for n in por_tipo.values())


@dataclass
class AvisoRevision:
    grupo: str
    tipo: str
    titulo: str
    donde: str
    que_paso: str
    que_hacer: str
    acciones: list[str] = field(default_factory=list)
    ruta: Path | None = None
    cantidad: int = 1
    filas: list[int] = field(default_factory=list)
    detalle: dict = field(default_factory=dict)
    clave: str = ""                # estable entre lecturas: sirve para saber qué se resolvió al recargar


@dataclass
class Ejemplo:
    """Un registro real y lo que decidió una regla con él («Ver cómo se aplican las reglas», mockup 21)."""
    registro: str
    decision: str
    regla: int
    cuenta: bool = True               # False: el registro no se contó o el convenio quedó fuera


@dataclass
class Traza:
    """Cifras de lo que decidió cada regla y un ejemplo por cada clase de decisión."""
    fuera_por_regla_1: int = 0                    # aplican al programa pero la regla 1 los deja fuera
    vigentes_fuera: int = 0
    vencidos_fuera: int = 0
    sin_convenio_que_cubra: int = 0               # registros de una institución con convenio, pero no para ese año
    vigencia_calculada: int = 0                   # regla 4: año de inicio + vigencia en años
    sin_fin_usable: int = 0                       # regla 4: van a la revisión
    sin_inicio: int = 0
    ejemplos: dict[str, Ejemplo] = field(default_factory=dict)

    def ejemplo(self, clase: str, e: Ejemplo) -> None:
        self.ejemplos.setdefault(clase, e)


@dataclass
class ResultadoCruce:
    programa: dict
    anio_inicio: int
    anio_fin: int
    filas: list[FilaCuadro]
    avisos: list[AvisoRevision]
    archivos_leidos: int
    movilidades_contadas: int
    actividades_contadas: int
    actividades_sin_institucion: int
    convenios_del_programa: int = 0            # los que APLICAN, antes de la regla 1
    traza: Traza = field(default_factory=Traza)

    @property
    def registros_asignados(self) -> int:
        return self.movilidades_contadas + self.actividades_contadas

    @property
    def sin_resultados(self) -> int:
        return sum(1 for f in self.filas if not f.total)

    @property
    def activos(self) -> int:
        return sum(1 for f in self.filas if f.convenio.activo)

    @property
    def sin_convenios(self) -> bool:
        """No queda ningún convenio en el cuadro: se bloquea Generar (mockups 42 y 45)."""
        return not self.filas

    @property
    def convenios_en_cuadro(self) -> int:
        return len(self.filas)

    def por_grupo(self) -> dict[str, list[AvisoRevision]]:
        return {g: [a for a in self.avisos if a.grupo == g] for g in ORDEN_GRUPOS}

    @property
    def avisos_para_revisar(self) -> int:
        return len(self.avisos)
