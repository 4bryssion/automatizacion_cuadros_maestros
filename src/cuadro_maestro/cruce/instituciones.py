"""Reconocer instituciones y programas por nombre, con las equivalencias que confirmó la persona."""
from __future__ import annotations

import difflib

from ..texto import normalizar

UMBRAL_SUGERENCIA = 0.6
MUY_PARECIDA = 0.9


class Equivalencias:
    """«Como aparece en el Excel» → «es esta»; ambos lados normalizados."""

    def __init__(self, lista: list[dict]):
        self._mapa = {normalizar(e["como_aparece"]): normalizar(e["es"]) for e in lista}

    def clave(self, nombre) -> str:
        n = normalizar(nombre)
        return self._mapa.get(n, n)


class IndiceInstituciones:
    """Todas las instituciones de la matriz (no solo las del programa), para distinguir un error de escritura
    de una institución que existe pero no tiene convenio con el programa."""

    def __init__(self, nombres: list[str], equivalencias: Equivalencias):
        self.equivalencias = equivalencias
        self._mostrar: dict[str, str] = {}
        for n in nombres:
            if n and str(n).strip():
                self._mostrar.setdefault(normalizar(n), str(n).strip())

    def clave(self, nombre) -> str:
        return self.equivalencias.clave(nombre)

    def existe(self, clave: str) -> bool:
        return clave in self._mostrar

    def sugerencias(self, nombre, cuantas: int = 3) -> list[dict]:
        """Las más parecidas, con su porcentaje (modal «Elegir institución…»)."""
        n = normalizar(nombre)
        puntajes = sorted(((difflib.SequenceMatcher(None, n, k).ratio(), k) for k in self._mostrar), reverse=True)
        return [{"institucion": self._mostrar[k], "parecido": round(p * 100), "muy_parecida": p >= MUY_PARECIDA}
                for p, k in puntajes[:cuantas] if p >= UMBRAL_SUGERENCIA]


def programa_coincide(valor, programa: dict, equivalencias: Equivalencias) -> bool:
    return equivalencias.clave(valor) == normalizar(programa["nombre"])


def parecido_al_programa(valor, programa: dict) -> float:
    return difflib.SequenceMatcher(None, normalizar(valor), normalizar(programa["nombre"])).ratio()
