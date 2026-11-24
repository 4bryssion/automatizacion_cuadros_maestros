"""Lógica de Ver revisión, sin ventanas: lo que se guarda de cada generación, recargar y comparar.

- Con la última generación se guardan sus avisos, una huella de cada fila del cuadro y una huella de cada sección de la
  configuración. Así Ver revisión funciona al reabrir el programa y se sabe si algo cambió.
- **Recargar** vuelve a leer y cruzar (sin escribir nada) y compara los avisos por su clave: resueltos, siguen, nuevos.
- **Cambios sin incluir** (docs/diseno_revision.md): el cuadro que saldría ahora es distinto del último generado, o la
  configuración cambió después de generar. Guardar un Excel sin cambiar nada no cuenta.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .configuracion.esquema import SECCIONES
from .cruce import AvisoRevision, ResultadoCruce, cruzar
from .cruce.modelos import ORDEN_GRUPOS
from .generacion.escritor import valor_campo
from .lectura import leer_carpeta

NOMBRE_SECCION = {"programas": "Programas", "campos": "Campos del cuadro maestro", "fuentes": "Fuentes de datos",
                  "equivalencias_instituciones": "Equivalencias de instituciones",
                  "equivalencias_programas": "Equivalencias de programas", "tipos_persona": "Tipos de persona",
                  "reglas": "Reglas de cruce"}


def _hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- huellas
def firmas_filas(resultado: ResultadoCruce, config: dict) -> list[str]:
    """Una huella por fila del cuadro, con los valores tal como se escriben en el Excel."""
    return [_hash([valor_campo(c, f, config) for c in config["campos"]]) for f in resultado.filas]


def firmas_config(config: dict) -> dict[str, str]:
    return {s: _hash(config.get(s)) for s in SECCIONES}


def elementos_cambiados(antes: dict, config: dict) -> dict[str, int]:
    """Secciones de la configuración que cambiaron desde que se generó (el valor es 1: se cambió algo en ella)."""
    ahora = firmas_config(config)
    return {NOMBRE_SECCION[s]: 1 for s in SECCIONES if antes.get(s) and antes[s] != ahora[s]}


def filas_que_cambian(antes: list[str], ahora: list[str]) -> int:
    """Filas que no están igual en los dos cuadros (las que se agregan, se quitan o cambian de contenido)."""
    from collections import Counter
    a, b = Counter(antes), Counter(ahora)
    return max(sum((a - b).values()), sum((b - a).values()))


# ---------------------------------------------------------------- avisos guardados
def aviso_a_dict(a: AvisoRevision) -> dict:
    d = asdict(a)
    d["ruta"] = str(a.ruta) if a.ruta else None
    return d


def aviso_de_dict(d: dict) -> AvisoRevision:
    d = dict(d)
    d["ruta"] = Path(d["ruta"]) if d.get("ruta") else None
    return AvisoRevision(**d)


@dataclass
class Comparacion:
    resueltos: list[AvisoRevision]
    siguen: list[AvisoRevision]
    nuevos: list[AvisoRevision]

    @property
    def antes(self) -> int:
        return len(self.resueltos) + len(self.siguen)

    @property
    def ahora(self) -> int:
        return len(self.siguen) + len(self.nuevos)


def comparar(antes: list[AvisoRevision], ahora: list[AvisoRevision]) -> Comparacion:
    claves_antes = {a.clave for a in antes}
    claves_ahora = {a.clave for a in ahora}
    return Comparacion([a for a in antes if a.clave not in claves_ahora],
                       [a for a in ahora if a.clave in claves_antes],
                       [a for a in ahora if a.clave not in claves_antes])


def que_se_logro(a: AvisoRevision) -> str:
    """Frase corta para la caja «Resueltos desde la última lectura»."""
    return {"convenio_sin_inicio": "ya tiene fecha, vuelve a contar en el cuadro",
            "convenio_fin_antes_de_inicio": "las fechas ya son coherentes",
            "convenio_sin_fin": "ya se sabe hasta qué año cuenta",
            "falta_archivo": "archivo encontrado",
            "falta_matriz": "matriz encontrada",
            "institucion_sin_coincidencia": "ya se cuenta en su convenio",
            "tipo_persona_no_reconocido": "ya se cuenta con su tipo de persona",
            "programa_parecido": "ya se cuenta en el programa",
            "columna_por_confirmar": "columna confirmada",
            "columna_sin_identificar": "columna identificada"}.get(a.tipo, "ya no aparece")


# ---------------------------------------------------------------- recargar
@dataclass
class Recarga:
    resultado: ResultadoCruce
    comparacion: Comparacion
    errores: list = field(default_factory=list)       # archivos que existen y no se pueden leer
    filas_cambian: int = 0
    config_cambiada: dict = field(default_factory=dict)
    leidos: int = 0
    esperados: int = 0

    @property
    def hay_cambios(self) -> bool:
        return bool(self.filas_cambian or self.config_cambiada)


def recargar(carpeta, config: dict, programa_id: str, anio_inicio: int, anio_fin: int,
             avisos_antes: list[AvisoRevision], firmas_antes: list[str], config_antes: dict) -> Recarga:
    lectura = leer_carpeta(Path(carpeta), config, anio_inicio, anio_fin)
    resultado = cruzar(lectura, config, programa_id)
    por_anio = [e for e in lectura.esperados if e.fuente != "matriz"]
    return Recarga(resultado, comparar(avisos_antes, resultado.avisos), list(lectura.errores),
                   filas_que_cambian(firmas_antes, firmas_filas(resultado, config)),
                   elementos_cambiados(config_antes, config), sum(e.encontrado for e in por_anio), len(por_anio))


def contar_por_grupo(avisos: list[AvisoRevision]) -> dict[str, int]:
    return {g: sum(1 for a in avisos if a.grupo == g) for g in ORDEN_GRUPOS}


# ---------------------------------------------------------------- resolver dentro del programa
def instituciones_de_la_matriz(carpeta, config: dict) -> list[tuple[str, int]]:
    """Instituciones de la matriz con su cantidad de convenios (para buscar en «Elegir institución…»)."""
    from collections import Counter

    from .texto import normalizar
    lectura = leer_carpeta(Path(carpeta), config, 1, 0)          # vigencia vacía: solo la matriz
    if lectura.matriz is None:
        return []
    nombres, cuenta = {}, Counter()
    for r in lectura.matriz.registros:
        n = r.valores.get("institucion")
        if n and str(n).strip():
            k = normalizar(n)
            nombres.setdefault(k, " ".join(str(n).split()))
            cuenta[k] += 1
    return sorted(((nombres[k], cuenta[k]) for k in nombres), key=lambda x: normalizar(x[0]))


def guardar_equivalencia_institucion(config: dict, como_aparece: str, es: str, origen: str = "revision") -> dict:
    lista = [e for e in config["equivalencias_instituciones"] if e["como_aparece"] != como_aparece]
    lista.append({"como_aparece": como_aparece, "es": es, "origen": origen})
    config["equivalencias_instituciones"] = lista
    return config


def confirmar_sugerencia(config: dict, aviso: AvisoRevision) -> str:
    """Aplica la sugerencia del aviso en la configuración. Devuelve qué se guardó (para mostrarlo)."""
    d = aviso.detalle
    if aviso.tipo == "programa_parecido":
        lista = [e for e in config["equivalencias_programas"] if e["como_aparece"] != d["como_aparece"]]
        lista.append({"como_aparece": d["como_aparece"], "es": d["es"], "origen": "revision"})
        config["equivalencias_programas"] = lista
        return f"«{d['como_aparece']}» es {d['es']} (Equivalencias de programas)"
    if aviso.tipo == "columna_por_confirmar":
        dato = d.get("dato") or ""
        if dato.startswith("programa:"):
            pid = dato.split(":", 1)[1]
            for p in config["programas"]:
                if p["id"] == pid:
                    p["columna_matriz"] = d["encabezado"]
            return f"La columna «{d['encabezado']}» es la del programa (Programas)"
        fuente = next(f for f in config["fuentes"] if f["id"] == d["fuente"])
        fuente["columnas"][dato]["elegida"] = d["encabezado"]
        return f"La columna «{d['encabezado']}» trae ese dato (Fuentes de datos)"
    raise ValueError(f"El aviso «{aviso.tipo}» no tiene una sugerencia para confirmar")
