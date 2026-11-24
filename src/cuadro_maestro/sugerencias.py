"""Sugerencias que la persona confirma: el asistente con Gemini (mockups 08 y 09) y Confirmar sugerencias del
programa (mockup 29). Sin interfaz, para probarlo sin ventanas.

Gemini (P16): el programa no se conecta. Prepara un mensaje con **solo** nombres de instituciones y títulos de
columnas, la persona lo pega en Gemini en su navegador y pega la respuesta de vuelta. Nada se guarda sin marcarlo, y
solo se aceptan propuestas que existan tal cual en la matriz o en el Excel (Gemini no puede inventar un nombre).
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field

from . import ajustes as A
from .cruce.avisos import NOMBRE_DATO, NOMBRE_FUENTE
from .cruce.instituciones import MUY_PARECIDA, parecido_al_programa
from .lectura.modelos import COLUMNA_SIN_IDENTIFICAR, EXACTA
from .revision import confirmar_sugerencia, guardar_equivalencia_institucion
from .texto import normalizar

INSTITUCION, COLUMNA, PROGRAMA = "institucion", "columna", "programa"
POR_CONFIRMAR, NO_COINCIDE, NO_ESTA, SIN_RESPUESTA = "por_confirmar", "no_coincide", "no_esta", "sin_respuesta"
URL_GEMINI = "https://gemini.google.com/app"
MUY_PARECIDA_PCT = round(MUY_PARECIDA * 100)
NINGUNA = {"sin coincidencia", "ninguna", "ninguno", "no coincide", "no hay", "no", "n a", "na", "sin opcion",
           "no encontrado", "no se encontro", "sin correspondencia"}


# ---------------------------------------------------------------- asistente con Gemini
@dataclass
class Pregunta:
    id: str                         # «I1», «C1»…
    tipo: str                       # institucion o columna
    como_aparece: str               # el nombre en el Excel o el dato que se busca
    opciones: list[str]
    fuente: str | None = None       # columnas: de qué fuente
    dato: str | None = None
    archivos: list[str] = field(default_factory=list)


@dataclass
class Respuesta:
    pregunta: Pregunta
    propuesta: str | None           # tal como está en las opciones (o lo que dijo Gemini si no está)
    estado: str

    @property
    def se_puede_guardar(self) -> bool:
        return self.estado == POR_CONFIRMAR


def instituciones_de(lectura) -> list[str]:
    vistas, lista = set(), []
    for r in (lectura.matriz.registros if lectura and lectura.matriz else []):
        n = r.valores.get("institucion")
        if n and str(n).strip() and normalizar(n) not in vistas:
            vistas.add(normalizar(n))
            lista.append(" ".join(str(n).split()))
    return sorted(lista, key=normalizar)


def preguntas_para_gemini(lectura, resultado, config) -> list[Pregunta]:
    """Lo que el programa no reconoció: instituciones sin coincidencia y columnas sin identificar."""
    preguntas = []
    instituciones = instituciones_de(lectura)
    vistas = set()
    for a in resultado.avisos if resultado else []:
        if a.tipo == "institucion_sin_coincidencia" and instituciones:
            nombre = a.detalle["como_aparece"]
            if normalizar(nombre) not in vistas:
                vistas.add(normalizar(nombre))
                preguntas.append(Pregunta(f"I{len(vistas)}", INSTITUCION, nombre, instituciones))
    estados = {e.id: e for e in A.estado_fuentes(config, lectura)}
    columnas: dict[tuple, Pregunta] = {}
    for av in lectura.avisos if lectura else []:
        if av.tipo != COLUMNA_SIN_IDENTIFICAR or (av.dato or "").startswith("programa:"):
            continue
        clave = (av.fuente, av.dato)
        if clave not in columnas:
            e = estados[av.fuente]
            usadas = {normalizar(d.encabezado) for d in e.datos if d.encabezado and d.estado == EXACTA}
            opciones = [h for h in e.encabezados if normalizar(h) not in usadas]
            if not opciones:
                continue
            columnas[clave] = Pregunta(f"C{len(columnas) + 1}", COLUMNA, A.nombre_dato(config, av.fuente, av.dato),
                                       opciones, av.fuente, av.dato)
        columnas[clave].archivos.append(av.ruta.name)
    return preguntas + list(columnas.values())


def mensaje(preguntas: list[Pregunta]) -> str:
    """El mensaje que se copia. Solo nombres de instituciones y títulos de columnas: nunca filas ni personas."""
    inst = [p for p in preguntas if p.tipo == INSTITUCION]
    cols = [p for p in preguntas if p.tipo == COLUMNA]
    partes = ["Ayúdame a emparejar nombres. Para cada elemento, elige la opción de su lista que sea la misma "
              "institución o la misma columna, aunque esté escrita distinto (tildes, siglas, errores de escritura u otro "
              "idioma). Si ninguna es la misma, responde «sin coincidencia». No inventes opciones.",
              "",
              "Responde SOLO con una línea por elemento, con este formato exacto y copiando la opción tal cual:",
              "I1 → <opción>",
              "C1 → <opción>"]
    if inst:
        partes += ["", "INSTITUCIONES (cómo aparecen en los reportes):"]
        partes += [f"{p.id}. {p.como_aparece}" for p in inst]
        partes += ["", "Opciones para las instituciones (nombres en la matriz de convenios):"]
        partes += [f"- {o}" for o in inst[0].opciones]
    if cols:
        partes += ["", "COLUMNAS (qué dato busco y títulos de columnas disponibles en el Excel):"]
        for p in cols:
            partes.append(f"{p.id}. Dato: {p.como_aparece} ({NOMBRE_FUENTE.get(p.fuente, p.fuente)}). Opciones: "
                          + " | ".join(p.opciones))
    return "\n".join(partes)


_LINEA = re.compile(r"^\s*(?:[-*•]\s*)?\**\s*([ICic]\s*\d+)\s*\**\s*[.):\-]?\s*(.*?)\s*(?:→|->|=>|⇒|:)\s*(.+?)\s*$")


def _limpiar(texto: str) -> str:
    texto = texto.strip().strip("*").strip().strip("«»\"'`").strip()
    return re.sub(r"\s*(\.\.\.|…)$", "", texto)


def _elegir(propuesta: str, opciones: list[str]) -> str | None:
    """La opción que propone Gemini: idéntica tras normalizar, o recortada («…») y que empiece igual, o casi igual
    (98 %, por una tilde o un espacio). Nunca una opción solo «parecida»: eso sería adivinar."""
    p = normalizar(propuesta)
    if not p:
        return None
    por_clave = {normalizar(o): o for o in opciones}
    if p in por_clave:
        return por_clave[p]
    empiezan = [o for k, o in por_clave.items() if len(p) >= 12 and k.startswith(p)]
    if len(empiezan) == 1:
        return empiezan[0]
    mejor = max(por_clave, key=lambda k: difflib.SequenceMatcher(None, p, k).ratio(), default=None)
    if mejor and difflib.SequenceMatcher(None, p, mejor).ratio() >= 0.98:
        return por_clave[mejor]
    return None


def interpretar(texto: str, preguntas: list[Pregunta]) -> list[Respuesta]:
    """Lee la respuesta pegada. Acepta «I1 → X», «I1. nombre → X», «1. nombre -> X» o «nombre → X»."""
    por_id = {p.id.lower(): p for p in preguntas}
    por_nombre = {normalizar(p.como_aparece): p for p in preguntas}
    halladas: dict[str, str] = {}
    for linea in (texto or "").splitlines():
        m = _LINEA.match(linea)
        if m:
            ident, izquierda, derecha = re.sub(r"\s", "", m.group(1)).lower(), m.group(2), m.group(3)
            p = por_id.get(ident) or por_nombre.get(normalizar(_limpiar(izquierda)))
        else:
            m2 = re.match(r"^\s*(?:\d+[.)]\s*)?(.+?)\s*(?:→|->|=>|⇒)\s*(.+?)\s*$", linea)
            if not m2:
                continue
            p, derecha = por_nombre.get(normalizar(_limpiar(m2.group(1)))), m2.group(2)
        if p and p.id not in halladas:
            halladas[p.id] = _limpiar(derecha)
    respuestas = []
    for p in preguntas:
        if p.id not in halladas:
            respuestas.append(Respuesta(p, None, SIN_RESPUESTA))
            continue
        dicho = halladas[p.id]
        if normalizar(dicho) in NINGUNA or not normalizar(dicho):
            respuestas.append(Respuesta(p, None, NO_COINCIDE))
            continue
        opcion = _elegir(dicho, p.opciones)
        respuestas.append(Respuesta(p, opcion, POR_CONFIRMAR) if opcion else Respuesta(p, dicho, NO_ESTA))
    return respuestas


def lineas_pegadas(texto: str) -> int:
    return sum(1 for x in (texto or "").splitlines() if x.strip())


def guardar_respuestas(config: dict, respuestas: list[Respuesta]) -> list[str]:
    """Guarda las marcadas (solo las que se pueden guardar). Devuelve qué se guardó, para mostrarlo."""
    hecho = []
    for r in respuestas:
        if not r.se_puede_guardar:
            continue
        p = r.pregunta
        if p.tipo == INSTITUCION:
            guardar_equivalencia_institucion(config, p.como_aparece, r.propuesta, origen="gemini")
            hecho.append(f"«{p.como_aparece}» es {r.propuesta}")
        else:
            A.elegir_columna(config, p.fuente, p.dato, r.propuesta)
            hecho.append(f"«{r.propuesta}» trae {p.como_aparece}")
    return hecho


# ---------------------------------------------------------------- Confirmar sugerencias del programa (29)
@dataclass
class Sugerencia:
    tipo: str                       # institucion, programa o columna
    como_aparece: str
    donde: str
    propone: str | None
    parecido: int                   # %
    guarda_en: str
    aviso: object                   # AvisoRevision de donde sale
    marcada: bool = False

    @property
    def muy_parecida(self) -> bool:
        return self.parecido >= MUY_PARECIDA_PCT


def sugerencias_del_programa(avisos, config) -> list[Sugerencia]:
    """Los avisos con un nombre parecido que se puede confirmar. Ninguna viene marcada."""
    programa_por_nombre = {normalizar(p["nombre"]): p for p in config["programas"]}
    lista = []
    for a in avisos:
        d = a.detalle or {}
        if a.tipo == "institucion_sin_coincidencia" and d.get("sugerencias"):
            s = d["sugerencias"][0]
            lista.append(Sugerencia(INSTITUCION, d["como_aparece"], a.donde, s["institucion"], s["parecido"],
                                    "Se guarda en Equivalencias de instituciones", a))
        elif a.tipo == "programa_parecido":
            p = programa_por_nombre.get(normalizar(d["es"])) or {"nombre": d["es"]}
            lista.append(Sugerencia(PROGRAMA, d["como_aparece"], a.donde, d["es"],
                                    round(parecido_al_programa(d["como_aparece"], p) * 100),
                                    "Se guarda en Equivalencias de programas", a))
        elif a.tipo == "columna_por_confirmar" and d.get("encabezado"):
            dato = d.get("dato") or ""
            if dato.startswith("programa:"):
                que, donde = "la columna del programa", "Se guarda en Programas"
            else:
                que = NOMBRE_DATO.get(dato, dato)
                donde = f"Se guarda en Fuentes de datos › {NOMBRE_FUENTE.get(d.get('fuente'), d.get('fuente'))}"
            lista.append(Sugerencia(COLUMNA, d["encabezado"], a.donde, que, round(float(d.get("puntaje") or 0) * 100),
                                    donde, a))
    return sorted(lista, key=lambda s: -s.parecido)


def marcar_muy_parecidas(sugerencias: list[Sugerencia]) -> int:
    for s in sugerencias:
        if s.muy_parecida:
            s.marcada = True
    return sum(s.marcada for s in sugerencias)


def confirmar_marcadas(config: dict, sugerencias: list[Sugerencia]) -> list[str]:
    hecho = []
    for s in sugerencias:
        if not s.marcada or not s.propone:
            continue
        if s.tipo == INSTITUCION:
            guardar_equivalencia_institucion(config, s.como_aparece, s.propone)
            hecho.append(f"«{s.como_aparece}» es {s.propone}")
        elif s.tipo == PROGRAMA:
            s.aviso.detalle["es"] = s.propone
            hecho.append(confirmar_sugerencia(config, s.aviso))
        else:
            hecho.append(confirmar_sugerencia(config, s.aviso))
    return hecho
