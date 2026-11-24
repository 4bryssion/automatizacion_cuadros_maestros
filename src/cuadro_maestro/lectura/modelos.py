"""Resultados de la lectura: qué se encontró, cómo se leyó, qué impide seguir y qué hay que revisar."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Estado de una columna (semáforo de Fuentes de datos)
EXACTA, POR_CONFIRMAR, SIN_IDENTIFICAR = "exacta", "por_confirmar", "sin_identificar"

# Causas de un archivo que existe pero no se puede leer (detienen la generación, mockup 43)
EN_USO, CON_CONTRASENA, DANADO = "en_uso", "con_contrasena", "danado"

# Tipos de aviso (no detienen; van a la revisión, a la vista previa y a la prueba de lectura)
FALTA_ARCHIVO = "falta_archivo"
FALTA_MATRIZ = "falta_matriz"                    # este sí bloquea Generar y Previsualizar
ABIERTO_EN_EXCEL = "abierto_en_excel"            # informativo (gris)
ARCHIVOS_REPETIDOS = "archivos_repetidos"
COLUMNA_POR_CONFIRMAR = "columna_por_confirmar"
COLUMNA_SIN_IDENTIFICAR = "columna_sin_identificar"
PROGRAMA_NUEVO_EN_MATRIZ = "programa_nuevo_en_matriz"
PROGRAMA_SIN_COLUMNA = "programa_sin_columna"
SIN_ENCABEZADOS = "sin_encabezados"
ARCHIVO_SIN_PERIODO = "archivo_sin_periodo"      # se reconoce la fuente pero no el año o el semestre


@dataclass
class Esperado:
    """Un archivo que la vigencia pide (la matriz, la movilidad de un año o la IC de un semestre)."""
    fuente: str
    anio: int | None = None
    semestre: int | None = None
    ruta: Path | None = None
    otros: list[Path] = field(default_factory=list)   # candidatos descartados para el mismo hueco

    @property
    def encontrado(self) -> bool:
        return self.ruta is not None


@dataclass
class Columna:
    dato: str
    estado: str
    indice: int | None = None          # posición (0 = columna A)
    encabezado: str | None = None      # tal como está en el Excel
    puntaje: float = 0.0

    @property
    def letra(self) -> str | None:
        if self.indice is None:
            return None
        n, s = self.indice + 1, ""
        while n:
            n, r = divmod(n - 1, 26)
            s = chr(65 + r) + s
        return s


@dataclass
class Registro:
    fila: int                          # número de fila en Excel (para citarla en la revisión)
    valores: dict


@dataclass
class ArchivoLeido:
    fuente: str
    ruta: Path
    anio: int | None
    semestre: int | None
    hoja: str
    fila_encabezados: int
    columnas: dict[str, Columna]
    registros: list[Registro]
    programas: dict[str, Columna] = field(default_factory=dict)   # solo la matriz: programa -> su columna
    encabezados: list[str] = field(default_factory=list)          # tal como están en el Excel (para «Elegir columna…»)

    @property
    def estado(self) -> str:
        estados = {c.estado for c in [*self.columnas.values(), *self.programas.values()]}
        if SIN_IDENTIFICAR in estados:
            return SIN_IDENTIFICAR
        return POR_CONFIRMAR if POR_CONFIRMAR in estados else EXACTA


@dataclass
class ErrorLectura:
    """Archivo que existe pero no se pudo leer. Detiene la generación (Hoja de errores)."""
    ruta: Path
    fuente: str
    anio: int | None
    semestre: int | None
    causa: str
    detalle: str = ""

    @property
    def que_paso(self) -> str:
        return {
            EN_USO: "Otro programa tiene el archivo en uso (casi seguro está abierto en Excel) y no se pudo leer.",
            CON_CONTRASENA: "El archivo tiene contraseña. El programa no puede abrir archivos protegidos.",
            DANADO: "El archivo está dañado o no es un .xlsx de verdad (por ejemplo, un .xls o un .csv con el nombre cambiado).",
        }[self.causa]

    @property
    def que_hacer(self) -> str:
        return {
            EN_USO: "Ciérralo en Excel, guarda si hace falta y pulsa Reintentar.",
            CON_CONTRASENA: "En Excel: Archivo › Información › Proteger libro › Cifrar con contraseña, borra la "
                            "contraseña y guarda. Luego pulsa Reintentar.",
            DANADO: "Ábrelo en Excel y guárdalo como Libro de Excel (.xlsx). Si no abre, pide otra copia a quien lo envió.",
        }[self.causa]


@dataclass
class Aviso:
    tipo: str
    fuente: str | None = None
    ruta: Path | None = None
    anio: int | None = None
    semestre: int | None = None
    dato: str | None = None
    detalle: dict = field(default_factory=dict)


@dataclass
class Lectura:
    carpeta: Path
    anio_inicio: int
    anio_fin: int
    esperados: list[Esperado]
    archivos: list[ArchivoLeido]
    errores: list[ErrorLectura]
    avisos: list[Aviso]

    @property
    def puede_seguir(self) -> bool:
        """Sin errores de lectura y con matriz: se puede cruzar y generar."""
        return not self.errores and self.matriz is not None

    @property
    def matriz(self) -> ArchivoLeido | None:
        return next((a for a in self.archivos if a.fuente == "matriz"), None)

    def de_fuente(self, fuente: str) -> list[ArchivoLeido]:
        return [a for a in self.archivos if a.fuente == fuente]
