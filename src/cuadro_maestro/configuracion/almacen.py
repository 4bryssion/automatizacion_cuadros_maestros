"""Guardado de la configuración en dos lugares a la vez, con copias de seguridad.

Reglas (docs/decisiones_de_proyecto.md, «Cómo funciona el guardado en dos lugares»):

1. Al guardar se escribe en los dos lugares; cada escritura va a un archivo temporal que luego se renombra.
2. Al abrir se valida cada copia y se usa la más reciente según la fecha guardada dentro del archivo.
3. Si falta una copia o no se puede leer, se restaura desde la otra y se avisa.
4. Si la carpeta del programa no permite escribir, se usa solo la del usuario.
5. Se conservan las últimas 10 copias de seguridad (en los dos lugares).
6. Si las dos copias son válidas pero distintas, gana la más reciente y se avisa cuál se usó.

Además, para que nunca se pierda nada sin querer, antes de sobrescribir una copia se guarda aparte como copia de
seguridad si no se podía leer (dañada o de una versión más nueva) o si era válida pero distinta y más antigua.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import esquema
from .valores_iniciales import configuracion_inicial

NOMBRE_ARCHIVO = "configuracion.json"
CARPETA_COPIAS = "copias"
MAX_COPIAS = 10
FORMATO_COPIA = "cuadro-maestro-copia"

USUARIO, PROGRAMA = "usuario", "programa"

# Motivos de una copia de seguridad (el texto en pantalla lo pone la interfaz).
AUTOMATICA = "automatica"            # antes del primer cambio de cada sesión
ANTES_DE_IMPORTAR = "antes_de_importar"
ANTES_DE_RESTAURAR = "antes_de_restaurar"
CREADA_POR_TI = "creada_por_ti"
DANADA = "danada"                    # contenido ilegible que se guardó aparte
VERSION_NUEVA = "version_nueva"      # guardada por una versión más nueva del programa
DESCARTADA = "descartada"            # la copia válida más antigua cuando las dos eran distintas
MOTIVOS = {AUTOMATICA, ANTES_DE_IMPORTAR, ANTES_DE_RESTAURAR, CREADA_POR_TI, DANADA, VERSION_NUEVA, DESCARTADA}

# Situaciones al abrir; cada una corresponde a un aviso (o a ninguno).
NORMAL = "normal"                    # sin aviso
PRIMERA_VEZ = "primera_vez"          # sin aviso: primera apertura (mockup 34)
RESTAURADA = "restaurada"            # mockup 46
DISTINTAS = "distintas"              # aviso informativo: se usó la más reciente
NO_ENCONTRADA = "no_encontrada"      # mockup 47


class ErrorDeGuardado(Exception):
    """No se pudo escribir en ninguno de los dos lugares."""


@dataclass
class EstadoLugar:
    lugar: str
    carpeta: Path
    estado: str = "falta"            # ok | falta | danada | version_nueva
    escribible: bool = True
    guardado_en: str | None = None
    detalle: str = ""
    restaurada: bool = False         # se reescribió al abrir con la copia del otro lugar

    @property
    def ruta(self) -> Path:
        return self.carpeta / NOMBRE_ARCHIVO


@dataclass
class CopiaDeSeguridad:
    ruta: Path
    creada_en: str
    motivo: str
    restaurable: bool
    configuracion: dict | None = None

    @property
    def guardado_en(self) -> str | None:
        return (self.configuracion or {}).get("guardado_en")


@dataclass
class ResultadoCarga:
    configuracion: dict
    situacion: str
    lugares: list[EstadoLugar]
    usada: str | None
    copias: list[CopiaDeSeguridad] = field(default_factory=list)

    @property
    def solo_usuario(self) -> bool:
        return not self._lugar(PROGRAMA).escribible

    def _lugar(self, nombre):
        return next(x for x in self.lugares if x.lugar == nombre)


def _ahora() -> datetime:
    return datetime.now(timezone.utc)


def _fecha(texto: str | None) -> datetime:
    try:
        return datetime.fromisoformat(texto)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return datetime.min.replace(tzinfo=timezone.utc)


class AlmacenConfiguracion:
    def __init__(self, carpeta_usuario: Path, carpeta_programa: Path, *,
                 reloj: Callable[[], datetime] = _ahora, max_copias: int = MAX_COPIAS,
                 version_programa: str = "0.1.0"):
        self.lugares = {USUARIO: Path(carpeta_usuario), PROGRAMA: Path(carpeta_programa)}
        self.reloj = reloj
        self.max_copias = max_copias
        self.version_programa = version_programa
        self.actual: dict | None = None
        self._copia_de_sesion_hecha = False
        self._escribible: dict[str, bool] = {}

    # ------------------------------------------------------------------ abrir
    def cargar(self) -> ResultadoCarga:
        estados: dict[str, EstadoLugar] = {}
        validos: dict[str, dict] = {}
        for nombre, carpeta in self.lugares.items():
            e = EstadoLugar(nombre, carpeta, escribible=self._probar_escritura(nombre))
            doc = self._leer(e)
            if doc is not None:
                validos[nombre] = doc
                e.guardado_en = doc["guardado_en"]
            estados[nombre] = e
        lugares = [estados[USUARIO], estados[PROGRAMA]]
        ilegibles = [e for e in lugares if e.estado in ("danada", "version_nueva")]
        for e in ilegibles:
            self._apartar_ilegible(e)

        if not validos:
            copias = self.copias_de_seguridad()
            if not ilegibles and not any(c.restaurable for c in copias):
                self.actual = None
                self.guardar(configuracion_inicial())
                self._copia_de_sesion_hecha = False   # escribir la inicial no es un cambio de la persona
                return ResultadoCarga(self.actual, PRIMERA_VEZ, lugares, None, copias)
            # No se escribe nada hasta que la persona decida (restaurar una copia o seguir con la inicial).
            self.actual = None
            inicial = self._con_metadatos(configuracion_inicial(), revision=0)
            return ResultadoCarga(inicial, NO_ENCONTRADA, lugares, None, copias)

        usada = max(validos, key=lambda n: (_fecha(validos[n]["guardado_en"]), validos[n]["revision"]))
        doc = validos[usada]
        self.actual = doc
        otra = PROGRAMA if usada == USUARIO else USUARIO
        situacion = NORMAL
        if otra not in validos:
            # Si el otro lugar no permite escribir (p. ej. el programa está en un disco protegido) no hay nada
            # que restaurar: Configuración ya indica que se usa solo la carpeta del usuario.
            situacion = RESTAURADA if estados[otra].escribible else NORMAL
        elif esquema.sin_metadatos(validos[otra]) != esquema.sin_metadatos(doc):
            situacion = DISTINTAS
            self._crear_copia(DESCARTADA, validos[otra])   # nada se pierde: se puede restaurar si hacía falta
        if validos.get(otra) != doc and estados[otra].escribible:
            estados[otra].restaurada = self._escribir(otra, doc)
        return ResultadoCarga(doc, situacion, lugares, usada, self.copias_de_seguridad())

    def seguir_con_la_inicial(self) -> dict:
        """Tras «Configuración no encontrada»: empezar de cero (lo ilegible ya quedó guardado aparte)."""
        doc = self.guardar(configuracion_inicial())
        self._copia_de_sesion_hecha = False
        return doc

    # ------------------------------------------------------------------ guardar
    def guardar(self, configuracion: dict) -> dict:
        """Guarda en los dos lugares y devuelve el documento guardado (con metadatos nuevos)."""
        if self.actual is not None and not self._copia_de_sesion_hecha:
            self._crear_copia(AUTOMATICA, self.actual)
        self._copia_de_sesion_hecha = True
        revision = (self.actual or {}).get("revision", 0) + 1
        doc = self._con_metadatos(esquema.sin_metadatos(configuracion), revision)
        problemas = esquema.validar(doc)
        if problemas:
            raise ValueError("Configuración inválida: " + "; ".join(problemas[:5]))
        escritos = [n for n in self.lugares if self._escribible.get(n, True) and self._escribir(n, doc)]
        if not escritos:
            raise ErrorDeGuardado("No se pudo guardar la configuración en ninguno de los dos lugares.")
        self.actual = doc
        return doc

    # ------------------------------------------------------------------ copias
    def crear_copia(self, motivo: str = CREADA_POR_TI) -> CopiaDeSeguridad:
        if self.actual is None:
            raise ValueError("No hay una configuración cargada.")
        return self._crear_copia(motivo, self.actual)

    def copias_de_seguridad(self) -> list[CopiaDeSeguridad]:
        """Copias de los dos lugares, sin repetir, de la más reciente a la más antigua."""
        vistas: dict[str, CopiaDeSeguridad] = {}
        for carpeta in self.lugares.values():
            d = carpeta / CARPETA_COPIAS
            if not d.is_dir():
                continue
            for ruta in d.glob("*.json"):
                if ruta.name in vistas:
                    continue
                c = self._leer_copia(ruta)
                if c:
                    vistas[ruta.name] = c
        return sorted(vistas.values(), key=lambda c: (_fecha(c.creada_en), c.ruta.name), reverse=True)

    def restaurar(self, copia: CopiaDeSeguridad) -> dict:
        if not copia.restaurable or copia.configuracion is None:
            raise ValueError("Esta copia no se puede restaurar.")
        doc = esquema.migrar(dict(copia.configuracion))
        problemas = esquema.validar(doc)
        if problemas:
            raise ValueError("La copia no es válida: " + "; ".join(problemas[:5]))
        if self.actual is not None:
            self._crear_copia(ANTES_DE_RESTAURAR, self.actual)
            self._copia_de_sesion_hecha = True
        return self.guardar(doc)

    # ------------------------------------------------------------------ internos
    def _con_metadatos(self, contenido: dict, revision: int) -> dict:
        return {"formato": esquema.FORMATO, "version_esquema": esquema.VERSION_ESQUEMA,
                "guardado_en": self.reloj().isoformat(), "revision": revision,
                "version_programa": self.version_programa, **contenido}

    def _probar_escritura(self, nombre: str) -> bool:
        carpeta = self.lugares[nombre]
        prueba = carpeta / f".prueba-escritura-{os.getpid()}"
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
            prueba.write_bytes(b"")
            prueba.unlink()
            ok = True
        except OSError:
            ok = False
        self._escribible[nombre] = ok
        return ok

    def _leer(self, e: EstadoLugar) -> dict | None:
        try:
            crudo = e.ruta.read_bytes()
        except (FileNotFoundError, NotADirectoryError):
            e.estado = "falta"
            return None
        except OSError as err:
            e.estado, e.detalle = "danada", f"No se pudo abrir: {err.strerror or err}"
            return None
        try:
            doc = json.loads(crudo.decode("utf-8"))
            doc = esquema.migrar(doc) if isinstance(doc, dict) else doc
        except esquema.VersionMasNueva as err:
            e.estado, e.detalle = "version_nueva", str(err)
            return None
        except (UnicodeDecodeError, json.JSONDecodeError):
            e.estado, e.detalle = "danada", "El contenido no se puede leer."
            return None
        problemas = esquema.validar(doc)
        if problemas:
            e.estado, e.detalle = "danada", problemas[0]
            return None
        e.estado = "ok"
        return doc

    def _escribir(self, nombre: str, doc: dict) -> bool:
        carpeta = self.lugares[nombre]
        datos = json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8")
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
            escribir_atomico(carpeta / NOMBRE_ARCHIVO, datos)
            return True
        except OSError:
            return False

    def _crear_copia(self, motivo: str, doc: dict | None, crudo: str | None = None,
                     huella: str | None = None) -> CopiaDeSeguridad:
        if motivo not in MOTIVOS:
            raise ValueError(f"Motivo desconocido: {motivo}")
        creada = self.reloj()
        nombre = f"{creada.strftime('%Y%m%d-%H%M%S-%f')}_{motivo}.json"
        envoltura = {"formato": FORMATO_COPIA, "motivo": motivo, "creada_en": creada.isoformat()}
        if doc is not None:
            envoltura["configuracion"] = doc
        else:
            envoltura["contenido_crudo"], envoltura["huella"] = crudo, huella
        datos = json.dumps(envoltura, ensure_ascii=False, indent=2).encode("utf-8")
        guardada = None
        for n, carpeta in self.lugares.items():
            if not self._escribible.get(n, True):
                continue
            d = carpeta / CARPETA_COPIAS
            try:
                d.mkdir(parents=True, exist_ok=True)
                escribir_atomico(d / nombre, datos)
                guardada = guardada or d / nombre
                self._podar(d)
            except OSError:
                continue
        if guardada is None:
            raise ErrorDeGuardado("No se pudo crear la copia de seguridad.")
        return CopiaDeSeguridad(guardada, creada.isoformat(), motivo, doc is not None, doc)

    def _apartar_ilegible(self, e: EstadoLugar) -> None:
        """Guarda aparte el contenido de una copia ilegible (una sola vez por contenido)."""
        try:
            crudo = e.ruta.read_bytes()
        except OSError:
            return
        huella = hashlib.sha256(crudo).hexdigest()
        motivo = VERSION_NUEVA if e.estado == "version_nueva" else DANADA
        for c in self.copias_de_seguridad():
            if c.motivo == motivo and _huella_de(c.ruta) == huella:
                return
        try:
            self._crear_copia(motivo, None, crudo.decode("utf-8", errors="replace"), huella)
        except ErrorDeGuardado:
            pass

    def _leer_copia(self, ruta: Path) -> CopiaDeSeguridad | None:
        try:
            env = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            return None
        if not isinstance(env, dict) or env.get("formato") != FORMATO_COPIA:
            return None
        doc = env.get("configuracion")
        restaurable = False
        if isinstance(doc, dict):
            try:
                restaurable = not esquema.validar(esquema.migrar(dict(doc)))
            except esquema.VersionMasNueva:
                restaurable = False
        return CopiaDeSeguridad(ruta, str(env.get("creada_en")), str(env.get("motivo")), restaurable,
                                doc if isinstance(doc, dict) else None)

    def _podar(self, carpeta_copias: Path) -> None:
        copias = sorted(carpeta_copias.glob("*.json"), key=lambda r: r.name, reverse=True)
        for vieja in copias[self.max_copias:]:
            try:
                vieja.unlink()
            except OSError:
                pass


def _huella_de(ruta: Path) -> str | None:
    try:
        return json.loads(ruta.read_text(encoding="utf-8")).get("huella")
    except (OSError, ValueError, AttributeError):
        return None


def escribir_atomico(destino: Path, datos: bytes, intentos: int = 5) -> None:
    """Escribe en un temporal de la misma carpeta y lo renombra sobre el destino.

    En Windows el renombrado falla si otro proceso (antivirus, indexador) tiene el archivo abierto un instante;
    por eso se reintenta unas veces antes de rendirse. Si algo falla, el temporal se borra.
    """
    tmp = destino.with_name(f".{destino.name}.{os.getpid()}.tmp")
    try:
        with open(tmp, "wb") as f:
            f.write(datos)
            f.flush()
            os.fsync(f.fileno())
        for i in range(intentos):
            try:
                os.replace(tmp, destino)
                return
            except PermissionError:
                if i == intentos - 1:
                    raise
                time.sleep(0.05 * (i + 1))
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
