"""Exportar e importar la configuración (mockup 23): llevarla a otro equipo o guardar una copia aparte.

El archivo es el mismo JSON que se guarda en los dos lugares (con su formato y versión de esquema), así que se valida
igual. Importar siempre deja antes una copia de seguridad «Antes de importar».
"""
from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

from ..texto import normalizar
from . import esquema

EXTENSION = ".json"
REEMPLAZAR, COMBINAR = "reemplazar", "combinar"


class ErrorImportar(Exception):
    """El archivo elegido no se puede importar; el mensaje se muestra tal cual."""


def nombre_sugerido(hoy: date | None = None) -> str:
    return f"Configuracion_CuadroMaestro_{(hoy or date.today()).isoformat()}{EXTENSION}"


def ruta_libre(carpeta: Path, nombre: str) -> Path:
    """No sobrescribe: si ya existe, «… (2).json», «… (3).json»…"""
    nombre = nombre.strip() or nombre_sugerido()
    if not nombre.lower().endswith(EXTENSION):
        nombre += EXTENSION
    ruta = Path(carpeta) / nombre
    n = 2
    while ruta.exists():
        ruta = Path(carpeta) / f"{Path(nombre).stem} ({n}){EXTENSION}"
        n += 1
    return ruta


def exportar(doc: dict, carpeta: Path, nombre: str) -> Path:
    from .almacen import escribir_atomico
    problemas = esquema.validar(doc)
    if problemas:
        raise ValueError("La configuración actual no es válida: " + "; ".join(problemas[:3]))
    if not Path(carpeta).is_dir():
        raise FileNotFoundError("La carpeta elegida ya no existe.")
    ruta = ruta_libre(carpeta, nombre)
    escribir_atomico(ruta, json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8"))
    return ruta


def leer(ruta: Path) -> dict:
    """Lee y valida un archivo para importar. Lanza ErrorImportar con un mensaje para la persona."""
    ruta = Path(ruta)
    try:
        texto = ruta.read_text(encoding="utf-8-sig")
    except OSError:
        raise ErrorImportar("No se pudo abrir el archivo. Revisa que exista y que no esté abierto en otro programa.")
    try:
        doc = json.loads(texto)
    except ValueError:
        raise ErrorImportar("El archivo no es una configuración exportada por este programa (no es un .json válido).")
    if not isinstance(doc, dict) or doc.get("formato") != esquema.FORMATO:
        raise ErrorImportar("El archivo no es una configuración exportada por este programa.")
    try:
        doc = esquema.migrar(doc)
    except esquema.VersionMasNueva as e:
        raise ErrorImportar(str(e))
    problemas = esquema.validar(doc)
    if problemas:
        raise ErrorImportar("El archivo está incompleto o dañado: " + "; ".join(problemas[:3]))
    return doc


# ---------------------------------------------------------------- qué cambiaría
ELEMENTOS = [("Programas", "programas", "id"), ("Campos del cuadro", "campos", "id"),
             ("Fuentes de datos", "fuentes", "id"), ("Equivalencias", "equivalencias", "como_aparece"),
             ("Tipos de persona", "tipos_persona", "id"), ("Reglas de cruce", "reglas", None)]


def _items(doc: dict, seccion: str) -> list:
    doc = esquema.sin_metadatos(doc)
    if seccion == "equivalencias":
        return [*doc["equivalencias_instituciones"], *doc["equivalencias_programas"]]
    if seccion == "reglas":
        return [(k, v) for k, v in doc["reglas"].items() if k != "confirmadas_el"]
    return doc[seccion]


def _clave(seccion, x, clave):
    if seccion == "reglas":
        return x[0]
    return normalizar(x[clave]) if seccion == "equivalencias" else x[clave]


def contar(doc: dict) -> list[tuple[str, int]]:
    return [(nombre, len(_items(doc, s))) for nombre, s, _ in ELEMENTOS]


def comparar(actual: dict, otro: dict) -> list[tuple[str, int, int, str]]:
    """[(elemento, hoy, el otro, cambio)]. La pantalla compara hoy con cómo quedaría (combinada o reemplazada); cambio: «Igual», «+n», «−n», «n distinta(s)» o combinaciones."""
    filas = []
    for nombre, s, clave in ELEMENTOS:
        a = {_clave(s, x, clave): x for x in _items(actual, s)}
        b = {_clave(s, x, clave): x for x in _items(otro, s)}
        nuevos, faltan = len(b.keys() - a.keys()), len(a.keys() - b.keys())
        distintos = sum(1 for k in a.keys() & b.keys() if a[k] != b[k])
        partes = []
        if nuevos:
            partes.append(f"+{nuevos}")
        if faltan:
            partes.append(f"−{faltan}")
        if distintos:
            partes.append(f"{distintos} distinta{'s' if distintos != 1 else ''}")
        filas.append((nombre, len(a), len(b), " · ".join(partes) or "Igual"))
    return filas


# ---------------------------------------------------------------- importar
def combinar(actual: dict, otro: dict) -> dict:
    """Conserva lo tuyo y agrega lo que falte: programas, campos, equivalencias y tipos nuevos, y los valores de tipo
    que no estén en ningún tipo. Las fuentes y las reglas se quedan como están (solo se agregan las columnas que
    necesitan los campos nuevos)."""
    r = copy.deepcopy(esquema.sin_metadatos(actual))
    o = esquema.sin_metadatos(otro)
    nombres = {normalizar(p["nombre"]) for p in r["programas"]}
    ids = {p["id"] for p in r["programas"]}
    for p in o["programas"]:
        if p["id"] not in ids and normalizar(p["nombre"]) not in nombres:
            r["programas"].append(copy.deepcopy(p))
    r["programas"].sort(key=lambda p: normalizar(p["nombre"]))
    ids = {c["id"] for c in r["campos"]}
    nombres = {normalizar(c["nombre"]) for c in r["campos"]}
    cols_mias = next(f for f in r["fuentes"] if f["id"] == "matriz")["columnas"]
    cols_otras = next((f for f in o["fuentes"] if f["id"] == "matriz"), {"columnas": {}})["columnas"]
    for c in o["campos"]:
        if c["id"] in ids or normalizar(c["nombre"]) in nombres:
            continue
        if c["fuente"] == "matriz" and c.get("dato") not in cols_mias:
            if c.get("dato") not in cols_otras:
                continue                                  # no se sabría de qué columna sale
            cols_mias[c["dato"]] = copy.deepcopy(cols_otras[c["dato"]])
        r["campos"].append(copy.deepcopy(c))
    for s in ("equivalencias_instituciones", "equivalencias_programas"):
        vistas = {normalizar(e["como_aparece"]) for e in r[s]}
        for e in o[s]:
            if normalizar(e["como_aparece"]) not in vistas:
                r[s].append(copy.deepcopy(e))
                vistas.add(normalizar(e["como_aparece"]))
    usados = {normalizar(v) for t in r["tipos_persona"] for v in t["valores"]}
    por_id = {t["id"]: t for t in r["tipos_persona"]}
    for t in o["tipos_persona"]:
        nuevos = [v for v in t["valores"] if normalizar(v) not in usados]
        usados.update(normalizar(v) for v in nuevos)
        if t["id"] in por_id:
            por_id[t["id"]]["valores"].extend(nuevos)
        elif not any(normalizar(x["nombre"]) == normalizar(t["nombre"]) for x in r["tipos_persona"]):
            r["tipos_persona"].append({**copy.deepcopy(t), "valores": nuevos})
    return r


def preparar(actual: dict, otro: dict, modo: str) -> dict:
    if modo == REEMPLAZAR:
        return copy.deepcopy(esquema.sin_metadatos(otro))
    if modo == COMBINAR:
        return combinar(actual, otro)
    raise ValueError(f"Modo de importación desconocido: {modo}")
