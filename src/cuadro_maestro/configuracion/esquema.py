"""Esquema del archivo de configuración: metadatos, validación y migración entre versiones.

Se valida a mano (sin dependencias) porque el .exe debe ser pequeño y porque los mensajes tienen que poder
mostrarse a una persona: cada problema es una frase que dice dónde está y qué está mal.
"""
FORMATO = "cuadro-maestro-configuracion"
VERSION_ESQUEMA = 1
METADATOS = ("formato", "version_esquema", "guardado_en", "revision", "version_programa")

FUENTES_DE_CAMPO = {"matriz", "reportes", "calculado", "vacio"}
TIPOS_DE_CAMPO = {"numero", "texto", "texto_calculado", "opciones", "fecha"}
ORIGENES_EQUIVALENCIA = {"tu", "gemini", "revision"}
SECCIONES = ("programas", "campos", "fuentes", "equivalencias_instituciones", "equivalencias_programas",
             "tipos_persona", "reglas")


class VersionMasNueva(Exception):
    """El archivo lo guardó una versión más nueva del programa; no se interpreta para no perder datos."""


def sin_metadatos(doc: dict) -> dict:
    return {k: v for k, v in doc.items() if k not in METADATOS}


def migrar(doc: dict) -> dict:
    """Lleva un documento de una versión anterior a la actual. Hoy solo existe la versión 1."""
    version = doc.get("version_esquema")
    if isinstance(version, int) and version > VERSION_ESQUEMA:
        raise VersionMasNueva(f"La configuración es de la versión {version} y este programa entiende hasta la "
                              f"{VERSION_ESQUEMA}. Usa una versión más nueva del programa.")
    # Aquí irán los pasos 1 -> 2, 2 -> 3, … cuando cambie el esquema.
    return doc


def validar(doc) -> list[str]:
    """Devuelve la lista de problemas; vacía si el documento es válido."""
    p: list[str] = []
    if not isinstance(doc, dict):
        return ["El archivo no contiene una configuración."]
    if doc.get("formato") != FORMATO:
        p.append("El archivo no es una configuración de este programa.")
    if doc.get("version_esquema") != VERSION_ESQUEMA:
        p.append(f"Versión de esquema no reconocida: {doc.get('version_esquema')!r}.")
    if not isinstance(doc.get("guardado_en"), str):
        p.append("Falta la fecha de guardado.")
    if not isinstance(doc.get("revision"), int):
        p.append("Falta el número de revisión.")
    for s in SECCIONES:
        if s not in doc:
            p.append(f"Falta la sección «{s}».")
    if p:
        return p

    _lista(p, doc, "programas", {"id": str, "nombre": str, "columna_matriz": str})
    _lista(p, doc, "campos", {"id": str, "nombre": str, "fuente": str, "tipo": str, "base": bool})
    for i, c in enumerate(_items(doc, "campos")):
        if c.get("fuente") not in FUENTES_DE_CAMPO:
            p.append(f"campos[{i}]: fuente «{c.get('fuente')}» no reconocida.")
        if c.get("tipo") not in TIPOS_DE_CAMPO:
            p.append(f"campos[{i}]: tipo «{c.get('tipo')}» no reconocido.")
    _lista(p, doc, "fuentes", {"id": str, "nombre": str, "archivo": dict, "columnas": dict, "filtros": dict})
    for i, f in enumerate(_items(doc, "fuentes")):
        for dato, col in (f.get("columnas") or {}).items():
            if not isinstance(col, dict) or not isinstance(col.get("sinonimos"), list):
                p.append(f"fuentes[{i}].columnas.{dato}: debe tener una lista de sinónimos.")
    for s in ("equivalencias_instituciones", "equivalencias_programas"):
        _lista(p, doc, s, {"como_aparece": str, "es": str, "origen": str}, clave_unica="como_aparece")
        for i, e in enumerate(_items(doc, s)):
            if e.get("origen") not in ORIGENES_EQUIVALENCIA:
                p.append(f"{s}[{i}]: origen «{e.get('origen')}» no reconocido.")
    _lista(p, doc, "tipos_persona", {"id": str, "nombre": str, "valores": list, "base": bool})
    if not isinstance(doc.get("reglas"), dict):
        p.append("«reglas» debe ser un objeto.")
    return p


def _items(doc, seccion):
    v = doc.get(seccion)
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []


def _lista(p, doc, seccion, campos, clave_unica="id"):
    v = doc.get(seccion)
    if not isinstance(v, list):
        p.append(f"«{seccion}» debe ser una lista.")
        return
    vistos = set()
    for i, x in enumerate(v):
        if not isinstance(x, dict):
            p.append(f"{seccion}[{i}]: no es un elemento válido.")
            continue
        for k, t in campos.items():
            if not isinstance(x.get(k), t):
                p.append(f"{seccion}[{i}]: falta «{k}» o no es del tipo esperado.")
        clave = x.get(clave_unica)
        if clave in vistos:
            p.append(f"{seccion}[{i}]: «{clave}» está repetido.")
        vistos.add(clave)
